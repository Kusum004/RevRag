from typing import Dict, List, Set, Optional
from common.models import UIElement, Action, ActionType, ScreenState

class ScreenFrontier:
    """
    Maintains the unexplored interactive frontier for a unique screen fingerprint.
    """

    def __init__(self, fingerprint: str, elements: List[UIElement]):
        self.fingerprint = fingerprint
        self.all_elements = elements
        self.unexplored_elements: List[UIElement] = [
            el for el in elements if (el.clickable or el.editable or el.scrollable)
        ]
        self.explored_element_ids: Set[str] = set()

    def get_next_interactive_element(self) -> Optional[UIElement]:
        while self.unexplored_elements:
            el = self.unexplored_elements.pop(0)
            if el.element_id not in self.explored_element_ids:
                self.explored_element_ids.add(el.element_id)
                return el
        return None

    def has_unexplored_actions(self) -> bool:
        return len(self.unexplored_elements) > 0


class ExplorationFrontierManager:
    """
    Manages frontiers across all discovered screen fingerprints.
    """

    def __init__(self):
        self.frontiers: Dict[str, ScreenFrontier] = {}
        self.discovered_screens: Dict[str, ScreenState] = {}
        self.visit_counts: Dict[str, int] = {}

    def register_screen(self, screen_state: ScreenState) -> ScreenFrontier:
        fp = screen_state.fingerprint
        if fp not in self.frontiers:
            self.frontiers[fp] = ScreenFrontier(fp, screen_state.elements)
            self.discovered_screens[fp] = screen_state
            self.visit_counts[fp] = 0
        self.visit_counts[fp] += 1
        return self.frontiers[fp]

    def get_frontier(self, fingerprint: str) -> Optional[ScreenFrontier]:
        return self.frontiers.get(fingerprint)

    def is_screen_fully_explored(self, fingerprint: str) -> bool:
        frontier = self.frontiers.get(fingerprint)
        return frontier is None or not frontier.has_unexplored_actions()
