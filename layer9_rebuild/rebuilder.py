import io
import json
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
from layer7_compiler.compiler import AppKnowledgePack

class ScreenRebuilder:
    """
    Pure Knowledge-Pack Rebuilder.
    Recreates visual UI screens (HTML/CSS + Synthesized Images)
    using EXCLUSIVELY the structured AppKnowledgePack JSON data
    (zero access to original runtime screenshots).
    """

    def __init__(self, knowledge_pack: AppKnowledgePack):
        self.pack = knowledge_pack
        self.design = knowledge_pack.design_system

    def generate_html_rebuild(self, screen_fingerprint: str) -> str:
        """
        Generates modern, standalone HTML5 + CSS recreating the screen from design tokens and element definitions.
        """
        profile = self.pack.screen_profiles.get(screen_fingerprint)
        if not profile:
            raise ValueError(f"Fingerprint {screen_fingerprint} not found in knowledge pack")

        palette = self.design.palette
        spacing = self.design.spacing
        typography = self.design.typography
        elements = profile.get("elements", [])

        # Generate HTML elements
        rendered_elements = []
        for el in elements:
            bounds = el.get("bounds", {})
            left_pct = round((bounds.get("left", 0) / 1080) * 100, 2)
            top_pct = round((bounds.get("top", 0) / 2400) * 100, 2)
            width_pct = round((bounds.get("width", max(50, bounds.get("right", 100) - bounds.get("left", 0))) / 1080) * 100, 2)
            height_pct = round((bounds.get("height", max(40, bounds.get("bottom", 100) - bounds.get("top", 0))) / 2400) * 100, 2)

            role = el.get("role", "view")
            text = el.get("text") or el.get("plain_description") or ""

            if role == "button":
                rendered_elements.append(
                    f'<button class="ui-button" style="left:{left_pct}%; top:{top_pct}%; width:{width_pct}%; height:{height_pct}%;">'
                    f'{text}</button>'
                )
            elif role == "text_input":
                form_type = el.get("form_field_type", "text")
                placeholder = f"Enter {form_type}..." if form_type else text
                rendered_elements.append(
                    f'<input type="text" class="ui-input" placeholder="{placeholder}" value="{text if text != placeholder else ""}" '
                    f'style="left:{left_pct}%; top:{top_pct}%; width:{width_pct}%; height:{height_pct}%;" />'
                )
            elif role == "card":
                rendered_elements.append(
                    f'<div class="ui-card" style="left:{left_pct}%; top:{top_pct}%; width:{width_pct}%; height:{height_pct}%;"></div>'
                )
            elif role == "heading":
                rendered_elements.append(
                    f'<h2 class="ui-heading" style="left:{left_pct}%; top:{top_pct}%; width:{width_pct}%;">{text}</h2>'
                )
            elif role == "tab":
                rendered_elements.append(
                    f'<div class="ui-tab" style="left:{left_pct}%; top:{top_pct}%; width:{width_pct}%; height:{height_pct}%;">{text}</div>'
                )
            elif role == "badge":
                rendered_elements.append(
                    f'<span class="ui-badge" style="left:{left_pct}%; top:{top_pct}%;">{text}</span>'
                )
            else:
                rendered_elements.append(
                    f'<div class="ui-text" style="left:{left_pct}%; top:{top_pct}%; width:{width_pct}%;">{text}</div>'
                )

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rebuild: {profile.get("screen_name")}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background-color: #0f111a;
    font-family: {typography.font_family_recommendation};
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
  }}
  .phone-frame {{
    width: 360px;
    height: 800px;
    position: relative;
    background-color: {palette.background};
    border-radius: 36px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 0 8px #262938;
    overflow: hidden;
  }}
  .status-bar {{
    position: absolute;
    top: 0; left: 0; right: 0; height: 28px;
    background-color: {palette.surface};
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 16px; font-size: 10px; color: {palette.text_secondary};
  }}
  .ui-button {{
    position: absolute;
    background: {palette.primary_accent};
    color: #ffffff;
    border: none;
    border-radius: {spacing.border_radius_dp}px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    display: flex; align-items: center; justify-content: center;
  }}
  .ui-input {{
    position: absolute;
    background: {palette.surface};
    color: {palette.text_primary};
    border: 1.5px solid {palette.primary_accent};
    border-radius: {spacing.border_radius_dp}px;
    padding: 0 12px;
    font-size: 12px;
    outline: none;
  }}
  .ui-card {{
    position: absolute;
    background: {palette.surface};
    border: 1px solid #334155;
    border-radius: {spacing.border_radius_dp}px;
  }}
  .ui-heading {{
    position: absolute;
    color: {palette.text_primary};
    font-size: 16px;
    font-weight: 700;
  }}
  .ui-text {{
    position: absolute;
    color: {palette.text_secondary};
    font-size: 11px;
    line-height: 1.3;
  }}
  .ui-badge {{
    position: absolute;
    background: #059669;
    color: #ffffff;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 9px;
    font-weight: 600;
  }}
  .ui-tab {{
    position: absolute;
    background: {palette.surface};
    color: {palette.text_secondary};
    border-top: 1px solid #334155;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px;
  }}
</style>
</head>
<body>
  <div class="phone-frame">
    <div class="status-bar">
      <span>9:41</span>
      <span>5G 100%</span>
    </div>
    {"".join(rendered_elements)}
  </div>
</body>
</html>
"""
        return html_template

    def render_rebuild_image(self, screen_fingerprint: str, width: int = 1080, height: int = 2400) -> bytes:
        """
        Renders a synthesized PNG image rebuild using knowledge pack design tokens & elements.
        """
        profile = self.pack.screen_profiles.get(screen_fingerprint)
        if not profile:
            raise ValueError(f"Fingerprint {screen_fingerprint} not found in knowledge pack")

        palette = self.design.palette
        bg_rgb = self._hex_to_rgb(palette.background)
        surface_rgb = self._hex_to_rgb(palette.surface)
        primary_rgb = self._hex_to_rgb(palette.primary_accent)
        text_pri_rgb = self._hex_to_rgb(palette.text_primary)
        text_sec_rgb = self._hex_to_rgb(palette.text_secondary)

        img = Image.new("RGB", (width, height), color=bg_rgb)
        draw = ImageDraw.Draw(img)

        # Status bar
        draw.rectangle([0, 0, width, 80], fill=surface_rgb)

        elements = profile.get("elements", [])
        for el in elements:
            b = el.get("bounds", {})
            left, top, right, bottom = b.get("left", 0), b.get("top", 0), b.get("right", 0), b.get("bottom", 0)
            if right <= left or bottom <= top:
                continue

            role = el.get("role", "view")
            text = el.get("text") or el.get("plain_description") or ""

            if role == "button":
                draw.rounded_rectangle([left, top, right, bottom], radius=16, fill=primary_rgb)
                draw.text((left + 30, top + (bottom - top)//2 - 15), text, fill=(255, 255, 255))
            elif role == "text_input":
                draw.rounded_rectangle([left, top, right, bottom], radius=12, fill=surface_rgb, outline=primary_rgb, width=2)
                draw.text((left + 25, top + (bottom - top)//2 - 15), text or "Input Field", fill=text_sec_rgb)
            elif role == "card":
                draw.rounded_rectangle([left, top, right, bottom], radius=20, fill=surface_rgb, outline=(51, 65, 85), width=1)
            elif role == "tab":
                draw.rectangle([left, top, right, bottom], fill=surface_rgb, outline=(51, 65, 85), width=1)
                draw.text((left + 60, top + 70), text, fill=text_sec_rgb)
            elif role == "heading":
                draw.text((left, top + 10), text, fill=text_pri_rgb)
            else:
                draw.text((left, top + 10), text, fill=text_sec_rgb)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def _hex_to_rgb(self, hex_code: str) -> tuple[int, int, int]:
        hex_code = hex_code.lstrip("#")
        if len(hex_code) == 3:
            hex_code = "".join([c*2 for c in hex_code])
        if len(hex_code) != 6:
            return (18, 20, 29)
        return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
