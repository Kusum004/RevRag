import io
from typing import List, Tuple, Dict, Any
from PIL import Image
from pydantic import BaseModel

class ColorPalette(BaseModel):
    primary_accent: str
    secondary_accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    is_dark_mode: bool
    palette_hex_list: List[str]

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    # Standard relative luminance formula
    r, g, b = [x / 255.0 for x in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def extract_palette_from_screenshots(screenshot_bytes_list: List[bytes]) -> ColorPalette:
    """
    Extracts dominant color palette, surface colors, text colors,
    and light/dark mode classification across a batch of screenshots.
    """
    if not screenshot_bytes_list:
        # Default fallback sleek dark theme
        return ColorPalette(
            primary_accent="#6366F1",
            secondary_accent="#818CF8",
            background="#12141D",
            surface="#1A1D29",
            text_primary="#F8FAFC",
            text_secondary="#94A3B8",
            is_dark_mode=True,
            palette_hex_list=["#12141D", "#1A1D29", "#6366F1", "#818CF8", "#F8FAFC"]
        )

    color_frequencies: Dict[Tuple[int, int, int], int] = {}

    for raw_bytes in screenshot_bytes_list:
        if not raw_bytes:
            continue
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        # Resize for fast color extraction
        img = img.resize((100, 100))
        # Quantize colors
        quantized = img.quantize(colors=16).convert("RGB")
        colors = quantized.getcolors(maxcolors=10000) or []
        for count, color in colors:
            color_frequencies[color] = color_frequencies.get(color, 0) + count

    if not color_frequencies:
        return ColorPalette(
            primary_accent="#6366F1",
            secondary_accent="#818CF8",
            background="#12141D",
            surface="#1A1D29",
            text_primary="#F8FAFC",
            text_secondary="#94A3B8",
            is_dark_mode=True,
            palette_hex_list=["#12141D", "#1A1D29", "#6366F1", "#818CF8", "#F8FAFC"]
        )

    # Sort colors by frequency
    sorted_colors = sorted(color_frequencies.items(), key=lambda x: x[1], reverse=True)
    hex_list = [rgb_to_hex(c[0]) for c in sorted_colors[:8]]

    # Most frequent color is usually the background
    bg_color = sorted_colors[0][0]
    bg_hex = rgb_to_hex(bg_color)
    bg_lum = calculate_luminance(bg_color)
    is_dark = bg_lum < 0.5

    # Find vibrant accent color (high saturation / hue difference from background)
    accents = [c[0] for c in sorted_colors if abs(calculate_luminance(c[0]) - bg_lum) > 0.2]
    primary = accents[0] if accents else (sorted_colors[1][0] if len(sorted_colors) > 1 else (99, 102, 241))
    secondary = accents[1] if len(accents) > 1 else (129, 140, 248)

    surface = sorted_colors[1][0] if len(sorted_colors) > 1 else (26, 29, 41)
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#64748B"

    return ColorPalette(
        primary_accent=rgb_to_hex(primary),
        secondary_accent=rgb_to_hex(secondary),
        background=bg_hex,
        surface=rgb_to_hex(surface),
        text_primary=text_primary,
        text_secondary=text_secondary,
        is_dark_mode=is_dark,
        palette_hex_list=hex_list
    )
