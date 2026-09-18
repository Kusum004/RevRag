import pytest
from layer1_instrumentation.mock_controller import MockDeviceController
from layer5_design.color_extractor import extract_palette_from_screenshots
from layer5_design.design_system import extract_design_system, AppDesignSystem

def test_color_palette_and_dark_mode_extraction():
    controller = MockDeviceController()
    screenshot_1 = controller.take_screenshot()
    
    controller.current_screen_id = "login"
    screenshot_2 = controller.take_screenshot()
    
    palette = extract_palette_from_screenshots([screenshot_1, screenshot_2])
    
    assert palette.is_dark_mode is True
    assert palette.primary_accent.startswith("#")
    assert palette.background.startswith("#")
    assert len(palette.palette_hex_list) >= 3

def test_full_design_system_extraction():
    controller = MockDeviceController()
    screens = []
    for scr_id in ["splash", "login", "home", "product_detail", "profile", "kyc"]:
        controller.current_screen_id = scr_id
        screens.append(controller.get_screen_state())
        
    ds = extract_design_system(screens)
    
    assert isinstance(ds, AppDesignSystem)
    assert ds.spacing.base_grid_unit_dp == 8
    assert len(ds.tone_of_voice) > 5
    assert len(ds.recurring_components) >= 2
    comp_types = [c.component_type for c in ds.recurring_components]
    assert any(c in ["Button", "EditText", "TextView", "CardView", "FrameLayout"] for c in comp_types)
