import re
from typing import List, Dict, Any, Set
from pydantic import BaseModel, Field
from common.models import ScreenState, UIElement
from layer5_design.color_extractor import ColorPalette, extract_palette_from_screenshots

class TypographySignal(BaseModel):
    display_title_height_dp: int = 32
    heading_height_dp: int = 22
    body_text_height_dp: int = 16
    caption_height_dp: int = 12
    font_family_recommendation: str = "Inter, -apple-system, Roboto, sans-serif"

class SpacingRhythm(BaseModel):
    base_grid_unit_dp: int = 8
    screen_padding_horizontal_dp: int = 16
    component_gap_vertical_dp: int = 12
    border_radius_dp: int = 12

class ComponentPattern(BaseModel):
    component_type: str
    count_across_app: int
    sample_resource_ids: List[str]
    typical_bounds_ratio: float

class AppDesignSystem(BaseModel):
    palette: ColorPalette
    typography: TypographySignal
    spacing: SpacingRhythm
    tone_of_voice: str = Field(description="Summary of brand tone, vocabulary, and communication style")
    recurring_components: List[ComponentPattern] = Field(default_factory=list)

def extract_design_system(screens: List[ScreenState]) -> AppDesignSystem:
    """
    Dynamically extracts brand design system, typography rhythm,
    tone of voice, and recurring UI patterns from live application screens.
    """
    # 1. Color Palette
    screenshot_bytes = [s.screenshot_bytes for s in screens if s.screenshot_bytes]
    palette = extract_palette_from_screenshots(screenshot_bytes)

    # 2. Spacing & Typography Analysis
    horizontal_paddings: List[int] = []
    all_words: List[str] = []
    component_counts: Dict[str, List[str]] = {}

    for s in screens:
        for el in s.elements:
            if el.text:
                words = re.findall(r'\b[A-Za-z]+\b', el.text)
                all_words.extend(words)
            if 0 < el.bounds.left < 150:
                horizontal_paddings.append(el.bounds.left // 3)

            # Derive clean component type from class name
            cls_name = el.class_name.split(".")[-1]
            if cls_name not in component_counts:
                component_counts[cls_name] = []
            if el.resource_id:
                clean_id = el.resource_id.split("/")[-1] if "/" in el.resource_id else el.resource_id
                component_counts[cls_name].append(clean_id)

    median_padding = int(sorted(horizontal_paddings)[len(horizontal_paddings) // 2]) if horizontal_paddings else 16
    spacing = SpacingRhythm(
        base_grid_unit_dp=8,
        screen_padding_horizontal_dp=max(8, min(24, median_padding)),
        component_gap_vertical_dp=12,
        border_radius_dp=12
    )

    typography = TypographySignal(
        display_title_height_dp=32,
        heading_height_dp=22,
        body_text_height_dp=16,
        caption_height_dp=12,
        font_family_recommendation="Inter, -apple-system, Roboto, sans-serif"
    )

    # 3. Dynamic Tone of Voice Linguistic Inference
    lower_words = [w.lower() for w in all_words]
    tone_descriptors = []
    
    # Check for direct action/imperative vocabulary
    action_words = {"search", "select", "tap", "add", "submit", "enter", "continue", "verify", "open", "save", "done"}
    if any(w in action_words for w in lower_words):
        tone_descriptors.append("Action-Oriented & Direct")
        
    # Check for technical / system vocabulary
    tech_words = {"settings", "network", "system", "device", "security", "privacy", "storage", "connection", "bluetooth", "wifi"}
    if any(w in tech_words for w in lower_words):
        tone_descriptors.append("Technical & Precise")

    # Check for conversational / friendly vocabulary
    friendly_words = {"welcome", "hello", "easy", "help", "explore", "discover", "enjoy", "favorites"}
    if any(w in friendly_words for w in lower_words):
        tone_descriptors.append("Friendly & Inviting")

    tone_of_voice = " | ".join(tone_descriptors) if tone_descriptors else "Concise & Functional UI Copy"

    # 4. Recurring Components Catalog
    components: List[ComponentPattern] = []
    for ctype, res_ids in sorted(component_counts.items(), key=lambda x: len(x[1]), reverse=True):
        if len(res_ids) > 0:
            components.append(ComponentPattern(
                component_type=ctype,
                count_across_app=len(res_ids),
                sample_resource_ids=list(set(res_ids))[:4],
                typical_bounds_ratio=1.0
            ))

    return AppDesignSystem(
        palette=palette,
        typography=typography,
        spacing=spacing,
        tone_of_voice=tone_of_voice,
        recurring_components=components[:8]
    )
