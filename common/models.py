from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    TAP = "tap"
    INPUT_TEXT = "input_text"
    SCROLL = "scroll"
    BACK = "back"
    WAIT = "wait"

class BoundingBox(BaseModel):
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    @property
    def center(self) -> tuple[int, int]:
        return ((self.left + self.right) // 2, (self.top + self.bottom) // 2)

class UIElement(BaseModel):
    element_id: str
    class_name: str
    resource_id: Optional[str] = None
    text: Optional[str] = None
    content_desc: Optional[str] = None
    bounds: BoundingBox
    clickable: bool = False
    editable: bool = False
    scrollable: bool = False
    depth: int = 0
    children_count: int = 0
    # Enriched semantic fields (Layer 4)
    role: Optional[str] = None
    semantic_description: Optional[str] = None
    form_field_type: Optional[str] = None

class ScreenState(BaseModel):
    fingerprint: str
    activity_name: Optional[str] = None
    elements: List[UIElement] = Field(default_factory=list)
    screenshot_bytes: Optional[bytes] = None
    screenshot_path: Optional[str] = None
    raw_xml: Optional[str] = None
    width: int = 1080
    height: int = 2400

class Action(BaseModel):
    action_type: ActionType
    target_element_id: Optional[str] = None
    target_bounds: Optional[BoundingBox] = None
    input_text: Optional[str] = None
    direction: Optional[str] = None  # "up", "down", "left", "right"
    reason: Optional[str] = None

class TransitionEdge(BaseModel):
    from_fingerprint: str
    action: Action
    to_fingerprint: str
    timestamp: float
