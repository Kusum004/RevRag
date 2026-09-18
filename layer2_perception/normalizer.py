import re
import xml.etree.ElementTree as ET
from typing import List, Optional
from common.models import UIElement, BoundingBox

BOUNDS_PATTERN = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")

def parse_bounds(bounds_str: str) -> Optional[BoundingBox]:
    if not bounds_str:
        return None
    match = BOUNDS_PATTERN.match(bounds_str.strip())
    if match:
        left, top, right, bottom = map(int, match.groups())
        return BoundingBox(left=left, top=top, right=right, bottom=bottom)
    return None

def parse_ui_hierarchy(xml_content: str, screen_width: int = 1080, screen_height: int = 2400) -> List[UIElement]:
    """
    Parses Android UIAutomator XML dump into normalized, compact UIElement nodes.
    Filters out off-screen or zero-size container elements.
    """
    if not xml_content or not xml_content.strip():
        return []

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return []

    elements: List[UIElement] = []

    # Interactive keywords for tabs, buttons, and actions
    INTERACTIVE_KEYWORDS = {
        "tab", "button", "nav", "network", "post", "jobs", "notification", 
        "home", "feed", "menu", "search", "create", "add", "compose", "profile", "chat", "message"
    }
    INTERACTIVE_CLASSES = {
        "android.widget.Button", "android.widget.ImageButton", "android.widget.TabWidget",
        "android.widget.ImageView", "android.widget.TextView", "android.view.ViewGroup",
        "android.widget.FrameLayout", "android.widget.LinearLayout", "android.widget.RelativeLayout"
    }

    def traverse(node: ET.Element, depth: int, parent_clickable: bool = False):
        attrib = node.attrib
        bounds_str = attrib.get("bounds", "")
        bounds = parse_bounds(bounds_str)

        node_clickable = attrib.get("clickable", "false").lower() == "true"
        # Propagate clickability if parent or self is clickable
        is_clickable = node_clickable or parent_clickable

        # Basic visibility check
        if bounds and bounds.width > 0 and bounds.height > 0:
            # Check if within screen
            if bounds.left < screen_width and bounds.top < screen_height and bounds.right > 0 and bounds.bottom > 0:
                import html
                class_name = attrib.get("class", "android.view.View")
                resource_id = html.unescape(attrib.get("resource-id", "")) or None
                text = html.unescape(attrib.get("text", "")) or None
                content_desc = html.unescape(attrib.get("content-desc", "")) or None
                editable = attrib.get("focused", "false").lower() == "true" or "EditText" in class_name
                scrollable = attrib.get("scrollable", "false").lower() == "true"

                # Check if this element represents a tab or action based on desc/text/id
                combined_desc = f"{content_desc or ''} {text or ''} {resource_id or ''}".lower()
                has_action_keyword = any(kw in combined_desc for kw in INTERACTIVE_KEYWORDS)
                
                # If it has action keywords or is in bottom navigation region, mark as clickable
                if has_action_keyword or "button" in class_name.lower():
                    is_clickable = True

                # Derive readable element ID
                clean_id = resource_id.split("/")[-1] if resource_id and "/" in resource_id else (resource_id or f"el_{len(elements)}")

                element = UIElement(
                    element_id=clean_id,
                    class_name=class_name,
                    resource_id=resource_id,
                    text=text,
                    content_desc=content_desc,
                    bounds=bounds,
                    clickable=is_clickable,
                    editable=editable,
                    scrollable=scrollable,
                    depth=depth,
                    children_count=len(node)
                )
                elements.append(element)

        for child in node:
            traverse(child, depth + 1, parent_clickable=is_clickable)

    traverse(root, 0, parent_clickable=False)
    return elements

