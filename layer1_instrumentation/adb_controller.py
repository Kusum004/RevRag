import subprocess
import time
import re
from pathlib import Path
from typing import Optional, Tuple, List
from common.config import get_adb_path
from common.models import Action, ActionType, ScreenState, UIElement, BoundingBox
from layer1_instrumentation.base import IDeviceController
from layer2_perception.normalizer import parse_ui_hierarchy
from layer2_perception.fingerprinter import compute_structural_fingerprint

class AdbDeviceController(IDeviceController):
    """
    Real Android Device & Emulator Controller.
    Directly drives physical devices or Android emulators via ADB / UIAutomator.
    Captures live UI hierarchies, real screenshot pixels, and performs touch/text/back actions.
    """

    def __init__(self, device_id: Optional[str] = None):
        self.adb_bin = get_adb_path()
        self.device_id = device_id
        self._cached_dimensions: Optional[Tuple[int, int]] = None
        self._auto_detect_device()

    def _auto_detect_device(self):
        """Automatically detects the first available running device/emulator if not specified."""
        if not self.device_id:
            res = self._run_adb(["devices"])
            output = res.stdout.decode("utf-8", errors="ignore")
            for line in output.splitlines()[1:]:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[1] == "device":
                    self.device_id = parts[0]
                    break

    def _run_adb(self, cmd_args: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
        base_cmd = [self.adb_bin]
        if self.device_id:
            base_cmd.extend(["-s", self.device_id])
        full_cmd = base_cmd + cmd_args
        try:
            return subprocess.run(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False
            )
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(args=full_cmd, returncode=1, stdout=b"", stderr=b"timeout")
        except Exception as e:
            return subprocess.CompletedProcess(args=full_cmd, returncode=1, stdout=b"", stderr=str(e).encode("utf-8"))

    def start_app(self, package_name: str, activity_name: Optional[str] = None) -> bool:
        """Launches any real Android application package on the device."""
        if activity_name:
            comp = f"{package_name}/{activity_name}"
            res = self._run_adb(["shell", "am", "start", "-n", comp])
        else:
            # Universal launch using monkey launcher intent
            res = self._run_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"])
            if res.returncode != 0:
                # Fallback to direct am start
                res = self._run_adb(["shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", "-p", package_name])
        time.sleep(2.0)
        return res.returncode == 0

    def stop_app(self, package_name: str) -> bool:
        res = self._run_adb(["shell", "am", "force-stop", package_name])
        return res.returncode == 0

    def get_screen_dimensions(self) -> Tuple[int, int]:
        if self._cached_dimensions:
            return self._cached_dimensions
        res = self._run_adb(["shell", "wm", "size"])
        output = res.stdout.decode("utf-8", errors="ignore")
        for line in output.splitlines():
            if "size:" in line.lower():
                parts = line.split(":")[-1].strip().split("x")
                if len(parts) == 2:
                    w, h = int(parts[0]), int(parts[1])
                    self._cached_dimensions = (w, h)
                    return self._cached_dimensions
        self._cached_dimensions = (1080, 2400)
        return self._cached_dimensions

    def take_screenshot(self) -> bytes:
        """Pulls real live screen pixel bytes from device."""
        # 1. Direct stream capture (fastest)
        res = self._run_adb(["exec-out", "screencap", "-p"])
        if res.returncode == 0 and len(res.stdout) > 1000:
            return res.stdout

        # 2. File-based fallback pull
        self._run_adb(["shell", "screencap", "-p", "/sdcard/revrag_sc.png"])
        res_pull = self._run_adb(["exec-out", "cat", "/sdcard/revrag_sc.png"])
        if res_pull.returncode == 0 and len(res_pull.stdout) > 1000:
            return res_pull.stdout
        return b""

    def get_ui_tree(self) -> str:
        """Dumps live Android UIAutomator XML hierarchy from foreground window."""
        self._run_adb(["shell", "uiautomator", "dump", "/sdcard/window_dump.xml"], timeout=15)
        res = self._run_adb(["exec-out", "cat", "/sdcard/window_dump.xml"])
        if res.returncode == 0 and res.stdout:
            return res.stdout.decode("utf-8", errors="ignore")
        return ""

    def get_current_activity(self) -> str:
        """Queries the live foreground activity name from the device."""
        res = self._run_adb(["shell", "dumpsys", "activity", "activities"])
        output = res.stdout.decode("utf-8", errors="ignore")
        match = re.search(r"ResumedActivity:\s*ActivityRecord\{[^}]+\s+([^\s/]+)/([^\s}]+)", output)
        if match:
            return f"{match.group(1)}{match.group(2)}"
        return "MainActivity"

    def perform_action(self, action: Action) -> bool:
        """Drives real touch, input, swipe, and key events on the device."""
        if action.action_type == ActionType.TAP:
            if action.target_bounds:
                cx, cy = action.target_bounds.center
                res = self._run_adb(["shell", "input", "tap", str(cx), str(cy)])
                time.sleep(1.0)
                return res.returncode == 0
            return False

        elif action.action_type == ActionType.INPUT_TEXT:
            if action.target_bounds:
                cx, cy = action.target_bounds.center
                self._run_adb(["shell", "input", "tap", str(cx), str(cy)])
                time.sleep(0.3)
            if action.input_text:
                escaped_text = action.input_text.replace(" ", "%s")
                res = self._run_adb(["shell", "input", "text", escaped_text])
                time.sleep(0.5)
                return res.returncode == 0
            return False

        elif action.action_type == ActionType.SCROLL:
            w, h = self.get_screen_dimensions()
            mid_x = w // 2
            if action.direction == "down" or not action.direction:
                res = self._run_adb(["shell", "input", "swipe", str(mid_x), str(int(h * 0.70)), str(mid_x), str(int(h * 0.30)), "300"])
            else:
                res = self._run_adb(["shell", "input", "swipe", str(mid_x), str(int(h * 0.30)), str(mid_x), str(int(h * 0.70)), "300"])
            time.sleep(1.0)
            return res.returncode == 0

        elif action.action_type == ActionType.BACK:
            res = self._run_adb(["shell", "input", "keyevent", "4"])  # KEYCODE_BACK
            time.sleep(1.0)
            return res.returncode == 0

        elif action.action_type == ActionType.WAIT:
            time.sleep(1.5)
            return True

        return False

    def get_screen_state(self) -> ScreenState:
        """Captures complete live screen state directly from the attached device."""
        xml_content = self.get_ui_tree()
        screenshot_data = self.take_screenshot()
        w, h = self.get_screen_dimensions()
        elements = parse_ui_hierarchy(xml_content, w, h)
        fingerprint = compute_structural_fingerprint(elements)
        activity_name = self.get_current_activity()

        return ScreenState(
            fingerprint=fingerprint,
            activity_name=activity_name,
            elements=elements,
            screenshot_bytes=screenshot_data,
            raw_xml=xml_content,
            width=w,
            height=h
        )
