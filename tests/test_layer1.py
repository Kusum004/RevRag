import pytest
from common.models import Action, ActionType, BoundingBox
from layer1_instrumentation.mock_controller import MockDeviceController

def test_mock_controller_initialization():
    controller = MockDeviceController()
    assert controller.current_screen_id == "splash"
    
    state = controller.get_screen_state()
    assert state is not None
    assert len(state.elements) > 0
    assert state.screenshot_bytes is not None
    assert len(state.screenshot_bytes) > 0
    assert state.raw_xml is not None

def test_mock_controller_navigation():
    controller = MockDeviceController()
    
    # Tap Get Started on Splash -> should go to Login
    tap_action = Action(
        action_type=ActionType.TAP,
        target_element_id="btn_get_started"
    )
    success = controller.perform_action(tap_action)
    assert success is True
    assert controller.current_screen_id == "login"
    
    # Fill phone and OTP and submit login -> should go to Home
    controller.perform_action(Action(action_type=ActionType.INPUT_TEXT, target_element_id="edit_phone", input_text="9876543210"))
    controller.perform_action(Action(action_type=ActionType.INPUT_TEXT, target_element_id="edit_otp", input_text="123456"))
    controller.perform_action(Action(action_type=ActionType.TAP, target_element_id="btn_login_submit"))
    assert controller.current_screen_id == "home"

def test_mock_controller_back_navigation():
    controller = MockDeviceController()
    controller.perform_action(Action(action_type=ActionType.TAP, target_element_id="btn_get_started"))
    assert controller.current_screen_id == "login"
    
    # Go back
    controller.perform_action(Action(action_type=ActionType.BACK))
    assert controller.current_screen_id == "splash"
