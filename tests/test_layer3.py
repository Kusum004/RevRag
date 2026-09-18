import pytest
from layer1_instrumentation.mock_controller import MockDeviceController
from layer3_agent.auth_handler import AuthGateHandler
from layer3_agent.explorer import ExplorationAgent

def test_auth_gate_handler():
    controller = MockDeviceController()
    # Go to login screen
    controller.current_screen_id = "login"
    state = controller.get_screen_state()
    
    handler = AuthGateHandler()
    actions = handler.detect_and_handle_gate(state.elements)
    
    assert actions is not None
    assert len(actions) >= 2
    # Verify phone input and submit are generated
    action_types = [a.action_type.value for a in actions]
    assert "input_text" in action_types
    assert "tap" in action_types

def test_autonomous_exploration_loop():
    controller = MockDeviceController()
    agent = ExplorationAgent(controller=controller, step_budget=20)
    
    screens, transitions = agent.explore()
    
    # Must have discovered multiple distinct screens
    assert len(screens) >= 3
    # Must have logged transition triples
    assert len(transitions) > 0
    for edge in transitions:
        assert edge.from_fingerprint.startswith("scr_")
        assert edge.to_fingerprint.startswith("scr_")
        assert edge.action is not None
