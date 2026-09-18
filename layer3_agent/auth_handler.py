import json
from pathlib import Path
from typing import Optional, List, Tuple
from common.models import UIElement, Action, ActionType
from common.config import BASE_DIR

class AuthGateHandler:
    """
    Autonomous Login, OTP, and KYC solver.
    Detects authentication / identification gates and returns input/submit actions.
    """

    def __init__(self, test_data_path: Optional[str] = None):
        path = Path(test_data_path) if test_data_path else BASE_DIR / "common" / "test_data.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.test_data = json.load(f)
        else:
            self.test_data = {
                "credentials": {"phone": "9876543210", "otp": "123456", "email": "test@revrag.ai", "password": "Pass123"},
                "kyc_data": {"pan_number": "ABCDE1234F", "aadhaar_last_four": "5678"}
            }

    def detect_and_handle_gate(self, elements: List[UIElement]) -> Optional[List[Action]]:
        """
        Scans elements for login/OTP/KYC fields.
        If a gate is detected, returns an ordered sequence of input and submit actions.
        """
        editable_elements = [el for el in elements if el.editable]
        if not editable_elements:
            return None

        actions_to_take: List[Action] = []
        has_matched_field = False

        for el in editable_elements:
            identifier = f"{el.resource_id or ''} {el.text or ''} {el.content_desc or ''} {el.element_id}".lower()

            if any(k in identifier for k in ["phone", "mobile", "number"]):
                actions_to_take.append(Action(
                    action_type=ActionType.INPUT_TEXT,
                    target_element_id=el.element_id,
                    target_bounds=el.bounds,
                    input_text=self.test_data["credentials"]["phone"],
                    reason="Auto-fill test phone number for login"
                ))
                has_matched_field = True

            elif any(k in identifier for k in ["otp", "code", "pin", "verification"]):
                actions_to_take.append(Action(
                    action_type=ActionType.INPUT_TEXT,
                    target_element_id=el.element_id,
                    target_bounds=el.bounds,
                    input_text=self.test_data["credentials"]["otp"],
                    reason="Auto-fill test OTP for verification"
                ))
                has_matched_field = True

            elif any(k in identifier for k in ["pan", "tax"]):
                actions_to_take.append(Action(
                    action_type=ActionType.INPUT_TEXT,
                    target_element_id=el.element_id,
                    target_bounds=el.bounds,
                    input_text=self.test_data["kyc_data"]["pan_number"],
                    reason="Auto-fill test PAN for KYC"
                ))
                has_matched_field = True

            elif any(k in identifier for k in ["aadhaar", "ssn", "identity"]):
                actions_to_take.append(Action(
                    action_type=ActionType.INPUT_TEXT,
                    target_element_id=el.element_id,
                    target_bounds=el.bounds,
                    input_text=self.test_data["kyc_data"]["aadhaar_last_four"],
                    reason="Auto-fill test Aadhaar for KYC"
                ))
                has_matched_field = True

        if has_matched_field:
            # Find matching submit button
            submit_btn = self._find_submit_button(elements)
            if submit_btn:
                actions_to_take.append(Action(
                    action_type=ActionType.TAP,
                    target_element_id=submit_btn.element_id,
                    target_bounds=submit_btn.bounds,
                    reason="Submit authentication or KYC form"
                ))
            return actions_to_take

        return None

    def _find_submit_button(self, elements: List[UIElement]) -> Optional[UIElement]:
        for el in elements:
            if el.clickable:
                txt = f"{el.resource_id or ''} {el.text or ''} {el.content_desc or ''} {el.element_id}".lower()
                if any(k in txt for k in ["login", "verify", "submit", "continue", "proceed", "done"]):
                    return el
        return None
