import time
from typing import List, Dict, Tuple, Optional, Set
from common.models import Action, ActionType, ScreenState, TransitionEdge
from layer1_instrumentation.base import IDeviceController
from layer3_agent.frontier import ExplorationFrontierManager
from layer3_agent.auth_handler import AuthGateHandler

class ExplorationAgent:
    """
    Autonomous Exploration Agent.
    Navigates an unfamiliar Android application without scripted paths,
    prioritizes bottom navigation tabs and primary create flows (e.g. Post, My Network, Jobs),
    manages interactive frontiers, bypasses auth gates, recovers via backtracking,
    and logs transition triples (from_fp, action, to_fp).
    """

    def __init__(
        self,
        controller: IDeviceController,
        auth_handler: Optional[AuthGateHandler] = None,
        step_budget: int = 35
    ):
        self.controller = controller
        self.auth_handler = auth_handler or AuthGateHandler()
        self.step_budget = step_budget
        self.frontier_mgr = ExplorationFrontierManager()
        self.transitions: List[TransitionEdge] = []
        self.screen_history: List[str] = []
        self.handled_auth_screens: Set[str] = set()
        self.scrolled_screens: Set[str] = set()
        self.same_screen_actions: Dict[str, int] = {}

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

            # 2. Pick next unexplored interactive element on current screen (priority sorted)
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
                        reason=f"Explore interactive element {next_element.element_id} ({next_element.text or next_element.content_desc or next_element.class_name})"
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

                # Anti-thrashing: Detect if tapping elements fails to produce a state change
                if resulting_state.fingerprint == current_fp:
                    self.same_screen_actions[current_fp] = self.same_screen_actions.get(current_fp, 0) + 1
                    # If 2 consecutive clicks on this screen yielded no transition (e.g. static chart/labels on detail screen)
                    if self.same_screen_actions[current_fp] >= 2 and step < self.step_budget:
                        escape_action = Action(
                            action_type=ActionType.BACK,
                            reason=f"Escape non-navigating sub-screen {current_fp}"
                        )
                        step += 1
                        self.controller.perform_action(escape_action)
                        escaped_state = self.controller.get_screen_state()
                        self.transitions.append(TransitionEdge(
                            from_fingerprint=current_fp,
                            action=escape_action,
                            to_fingerprint=escaped_state.fingerprint,
                            timestamp=time.time()
                        ))
                        self.same_screen_actions[current_fp] = 0
                        continue
                else:
                    self.same_screen_actions[current_fp] = 0

            else:
                # 3. No visible unexplored elements on this screen
                # Check if we can scroll down to discover new items on feed/list screens
                has_scrollable = any(el.scrollable for el in current_state.elements)
                if has_scrollable and current_fp not in self.scrolled_screens:
                    self.scrolled_screens.add(current_fp)
                    scroll_action = Action(
                        action_type=ActionType.SCROLL,
                        direction="down",
                        reason="Scroll down to reveal undiscovered content and tab items"
                    )
                    step += 1
                    self.controller.perform_action(scroll_action)
                    resulting_state = self.controller.get_screen_state()
                    self.transitions.append(TransitionEdge(
                        from_fingerprint=current_fp,
                        action=scroll_action,
                        to_fingerprint=resulting_state.fingerprint,
                        timestamp=time.time()
                    ))
                    continue

                # Check if all discovered frontiers are exhausted
                all_exhausted = all(
                    not f.has_unexplored_actions() for f in self.frontier_mgr.frontiers.values()
                )
                if consecutive_backtracks >= 8 or (consecutive_backtracks >= 3 and all_exhausted):
                    # Fully explored accessible reachable graph or trapped
                    break

                back_action = Action(
                    action_type=ActionType.BACK,
                    reason="Backtrack to parent screen to explore unvisited branches/tabs"
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

