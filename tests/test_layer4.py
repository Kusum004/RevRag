import pytest
from layer1_instrumentation.mock_controller import MockDeviceController
from layer4_understanding.schema import ScreenUnderstanding
from layer4_understanding.vlm_client import VlmScreenAnalyzer

def test_screen_understanding_schema_and_extraction():
    controller = MockDeviceController()
    analyzer = VlmScreenAnalyzer(provider="offline_heuristic")
    
    # Analyze Splash Screen
    splash_state = controller.get_screen_state()
    splash_analysis = analyzer.analyze_screen(splash_state)
    
    assert isinstance(splash_analysis, ScreenUnderstanding)
    assert splash_analysis.screen_category == "onboarding"
    assert len(splash_analysis.purpose) > 10
    assert len(splash_analysis.elements) > 0
    assert any(e.role == "button" for e in splash_analysis.elements)
    
    # Analyze Login Screen
    controller.current_screen_id = "login"
    login_state = controller.get_screen_state()
    login_analysis = analyzer.analyze_screen(login_state)
    
    assert login_analysis.screen_category == "authentication"
    phone_field = next(e for e in login_analysis.elements if e.form_field_type == "phone")
    assert phone_field.role == "text_input"
    assert "mobile" in phone_field.plain_description.lower() or "phone" in phone_field.plain_description.lower()

def test_screen_understanding_json_serialization():
    controller = MockDeviceController()
    analyzer = VlmScreenAnalyzer(provider="offline_heuristic")
    state = controller.get_screen_state()
    analysis = analyzer.analyze_screen(state)
    
    dumped = analysis.model_dump()
    assert "fingerprint" in dumped
    assert "purpose" in dumped
    assert "elements" in dumped
    
    # Re-validate from dict
    reconstructed = ScreenUnderstanding.model_validate(dumped)
    assert reconstructed.fingerprint == analysis.fingerprint
