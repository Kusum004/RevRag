import re
from typing import Dict, List, Set, Optional
from common.models import UIElement, Action, ActionType, ScreenState

TAB_KEYWORDS = {
    "network", "post", "jobs", "notification", "notifications", "tab", "nav",
    "home", "feed", "menu", "search", "create", "add", "compose", "plus",
    "discover", "explore", "profile", "message", "messages", "chat"
}

def calculate_element_priority(el: UIElement, screen_height: int = 2400) -> int:
    """
    Computes priority score for an interactive element (higher = explored sooner).
    Ensures bottom tabs, FABs, and primary navigation destinations are explored first.
    """
    score = 10
    desc_str = f"{el.content_desc or ''} {el.text or ''} {el.resource_id or ''}".lower()
    
    # Check for tab / primary action keywords
    is_tab_keyword = any(kw in desc_str for kw in TAB_KEYWORDS)
    is_bottom_nav = el.bounds.top >= int(screen_height * 0.75) if el.bounds else False
    is_top_bar = el.bounds.bottom <= int(screen_height * 0.18) if el.bounds else False

    # Priority 1: Bottom Navigation tabs (Post, My Network, Notifications, Jobs, Home)
    if is_bottom_nav and (is_tab_keyword or el.clickable):
        score += 100
        # Post / Add / Create FABs in the bottom bar get highest priority
        if any(kw in desc_str for kw in ["post", "create", "add", "plus", "+"]):
            score += 30
        elif any(kw in desc_str for kw in ["network", "job", "notification"]):
            score += 20

    # Priority 2: Floating Action Buttons (FAB) & Create Actions anywhere
    elif any(kw in desc_str for kw in ["post", "create", "add", "compose", "fab"]):
        score += 80

    # Priority 3: Top Navigation / Search / Menu / Tabs
    elif is_tab_keyword or is_top_bar:
        score += 50

    # Priority 4: Editable Text Inputs
    elif el.editable:
        score += 40

    # Priority 5: General Buttons
    elif "button" in el.class_name.lower() or el.clickable:
        score += 30

    # Deprioritize small micro-actions inside feed (like, comment, share, repost)
    if any(kw in desc_str for kw in ["like", "comment", "share", "repost", "reactions"]):
        score -= 15

    return score


class ScreenFrontier:
    """
    Maintains the unexplored interactive frontier for a unique screen fingerprint,
    ordered by exploration priority (bottom tabs, FABs, and primary actions first).
    """

    def __init__(self, fingerprint: str, elements: List[UIElement], screen_height: int = 2400):
        self.fingerprint = fingerprint
        self.all_elements = elements
        self.screen_height = screen_height
        
        candidates = [
            el for el in elements if (el.clickable or el.editable or el.scrollable)
        ]
        # Sort candidates descending by priority score
        self.unexplored_elements: List[UIElement] = sorted(
            candidates,
            key=lambda el: calculate_element_priority(el, self.screen_height),
            reverse=True
        )
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
            self.frontiers[fp] = ScreenFrontier(fp, screen_state.elements, screen_height=screen_state.height)
            self.discovered_screens[fp] = screen_state
            self.visit_counts[fp] = 0
        self.visit_counts[fp] += 1
        return self.frontiers[fp]

    def get_frontier(self, fingerprint: str) -> Optional[ScreenFrontier]:
        return self.frontiers.get(fingerprint)

    def is_screen_fully_explored(self, fingerprint: str) -> bool:
        frontier = self.frontiers.get(fingerprint)
        return frontier is None or not frontier.has_unexplored_actions()

