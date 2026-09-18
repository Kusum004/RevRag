import pytest
from layer1_instrumentation.mock_controller import MockDeviceController
from layer2_perception.normalizer import parse_ui_hierarchy
from layer2_perception.fingerprinter import compute_structural_fingerprint
from common.models import Action, ActionType

def test_xml_hierarchy_parsing():
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <hierarchy rotation="0">
      <node index="0" text="" class="android.widget.FrameLayout" package="com.revrag.sampleapp" bounds="[0,0][1080,2400]">
        <node index="1" text="Log In" resource-id="com.revrag.sampleapp:id/tv_title" class="android.widget.TextView" clickable="false" bounds="[100,200][980,300]" />
        <node index="2" text="Submit" resource-id="com.revrag.sampleapp:id/btn_submit" class="android.widget.Button" clickable="true" bounds="[100,500][980,650]" />
      </node>
    </hierarchy>
    """
    elements = parse_ui_hierarchy(sample_xml, 1080, 2400)
    assert len(elements) == 3
    btn = next(e for e in elements if e.resource_id == "com.revrag.sampleapp:id/btn_submit")
    assert btn.clickable is True
    assert btn.class_name == "android.widget.Button"
    assert btn.bounds.width == 880

def test_structural_fingerprint_invariance_across_dynamic_content():
    """
    PROVES HARD REQUIREMENT:
    Two screenshots/states of the same screen with completely different dynamic text,
    product prices, and labels produce identical structural fingerprint hashes.
    """
    controller = MockDeviceController()
    # Navigate to Home screen
    controller.perform_action(Action(action_type=ActionType.TAP, target_element_id="btn_get_started"))
    controller.perform_action(Action(action_type=ActionType.TAP, target_element_id="btn_skip_login"))
    assert controller.current_screen_id == "home"

    # Variation 1: Sony WH-1000XM5, $349.99
    controller.set_dynamic_variation(0)
    state_v1 = controller.get_screen_state()
    fp1 = state_v1.fingerprint
    text_v1 = [e.text for e in state_v1.elements if e.text]

    # Variation 2: Bose QuietComfort Ultra, $379.00
    controller.set_dynamic_variation(1)
    state_v2 = controller.get_screen_state()
    fp2 = state_v2.fingerprint
    text_v2 = [e.text for e in state_v2.elements if e.text]

    # Verify that content actually changed
    assert text_v1 != text_v2
    # Verify that fingerprint remained STRICTLY IDENTICAL
    assert fp1 == fp2
    assert fp1.startswith("scr_")
