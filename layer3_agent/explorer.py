import time
from typing import List, Dict, Tuple, Optional
from common.models import Action, ActionType, ScreenState, TransitionEdge
from layer1_instrumentation.base import IDeviceController
from layer3_agent.frontier import ExplorationFrontierManager
from layer3_agent.auth_handler import AuthGateHandler

class ExplorationAgent:
    """
    Autonomous Exploration Agent.
    Navigates an unfamiliar Android application without scripted paths,
    manages interactive frontiers, bypasses auth gates, recovers via backtracking,
    and logs transition triples (from_fp, action, to_fp).
    """

    def __init__(
        self,
        controller: IDeviceController,
        auth_handler: Optional[AuthGateHandler] = None,
        step_budget: int = 30
    ):
        self.controller = controller
        self.auth_handler = auth_handler or AuthGateHandler()
        self.step_budget = step_budget
        self.frontier_mgr = ExplorationFrontierManager()
        self.transitions: List[TransitionEdge] = []
        self.screen_history: List[str] = []
        self.handled_auth_screens: set[str] = set()

    def explore(self) -> Tuple[Dict[str, ScreenState], List[TransitionEdge]]:
        """
        Runs the full autonomous exploration loop.
        Returns (discovered_screens_dict, transitions_list).
        """
        step = 0
        consecutive_backtracks = 0

        while step < self.step_budget:
            current_state = self.controller.get_screen_state()
            current_fp = current_state.fingerprint
            self.screen_history.append(current_fp)
            frontier = self.frontier_mgr.register_screen(current_state)

            # 1. Check for Authentication / KYC gates
            if current_fp not in self.handled_auth_screens:
                gate_actions = self.auth_handler.detect_and_handle_gate(current_state.elements)
                if gate_actions:
                    self.handled_auth_screens.add(current_fp)
                    for g_action in gate_actions:
                        step += 1
                        self.controller.perform_action(g_action)
                        next_state = self.controller.get_screen_state()
                        self.transitions.append(TransitionEdge(
                            from_fingerprint=current_fp,
                            action=g_action,
                            to_fingerprint=next_state.fingerprint,
                            timestamp=time.time()
                        ))
                        current_fp = next_state.fingerprint
                    continue

            # 2. Pick next unexplored interactive element on current screen
            next_element = frontier.get_next_interactive_element()

            if next_element:
                consecutive_backtracks = 0
                if next_element.editable:
                    action = Action(
                        action_type=ActionType.INPUT_TEXT,
                        target_element_id=next_element.element_id,
                        target_bounds=next_element.bounds,
                        input_text="RevRag Autonomous Test",
                        reason=f"Fill editable field {next_element.element_id}"
                    )
                else:
                    action = Action(
                        action_type=ActionType.TAP,
                        target_element_id=next_element.element_id,
                        target_bounds=next_element.bounds,
                        reason=f"Explore interactive element {next_element.element_id}"
                    )

                step += 1
                self.controller.perform_action(action)
                resulting_state = self.controller.get_screen_state()
                self.transitions.append(TransitionEdge(
                    from_fingerprint=current_fp,
                    action=action,
                    to_fingerprint=resulting_state.fingerprint,
                    timestamp=time.time()
                ))

            else:
                # 3. No unexplored elements on this screen -> Backtrack
                if consecutive_backtracks >= 4:
                    # Trapped in deep loop or reached app root
                    break

                back_action = Action(
                    action_type=ActionType.BACK,
                    reason="Backtrack to explore unvisited branches"
                )
                step += 1
                consecutive_backtracks += 1
                self.controller.perform_action(back_action)
                resulting_state = self.controller.get_screen_state()
                self.transitions.append(TransitionEdge(
                    from_fingerprint=current_fp,
                    action=back_action,
                    to_fingerprint=resulting_state.fingerprint,
                    timestamp=time.time()
                ))

        return self.frontier_mgr.discovered_screens, self.transitions
