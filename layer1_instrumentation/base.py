from abc import ABC, abstractmethod
from typing import Optional, Tuple
from common.models import Action, ScreenState

class IDeviceController(ABC):
    """
    Abstract Interface for Device Interaction.
    Wraps real Android devices (ADB / UIAutomator2) or simulated mock devices.
    """

    @abstractmethod
    def start_app(self, package_name: str, activity_name: Optional[str] = None) -> bool:
        """Launches the target application."""
        pass

    @abstractmethod
    def stop_app(self, package_name: str) -> bool:
        """Stops/kills the target application."""
        pass

    @abstractmethod
    def get_screen_state(self) -> ScreenState:
        """Captures the current screen state including UI tree and screenshot."""
        pass

    @abstractmethod
    def perform_action(self, action: Action) -> bool:
        """Executes a touch, input, scroll, or back navigation action."""
        pass

    @abstractmethod
    def get_ui_tree(self) -> str:
        """Returns the raw XML or hierarchy tree of the foreground window."""
        pass

    @abstractmethod
    def take_screenshot(self) -> bytes:
        """Captures screen pixels as compressed PNG/JPEG bytes."""
        pass

    @abstractmethod
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """Returns (width, height) of the device screen."""
        pass
