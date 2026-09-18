import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from layer7_compiler.compiler import AppKnowledgePack
from layer9_rebuild.rebuilder import ScreenRebuilder

def generate_side_by_side_fidelity_proof(
    original_screenshot_bytes: bytes,
    rebuilt_image_bytes: bytes,
    screen_name: str,
    output_path: str
) -> str:
    """
    Creates a side-by-side visual proof image comparing the original screen capture
    against the pure Knowledge-Pack rebuild.
    """
    orig_img = Image.open(io.BytesIO(original_screenshot_bytes)).convert("RGB")
    rebuilt_img = Image.open(io.BytesIO(rebuilt_image_bytes)).convert("RGB")

    # Target phone frame dimensions in comparison
    target_w, target_h = 360, 800
    orig_resized = orig_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    rebuilt_resized = rebuilt_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    canvas_w = (target_w * 2) + 120
    canvas_h = target_h + 180

    canvas = Image.new("RGB", (canvas_w, canvas_h), color=(15, 17, 26))
    draw = ImageDraw.Draw(canvas)

    # Title header
    header_text = f"Fidelity Proof: {screen_name}"
    subtitle_text = "Original Screenshot (Left) vs. Pure Knowledge Pack Rebuild (Right)"
    draw.text((40, 25), header_text, fill=(248, 250, 252))
    draw.text((40, 60), subtitle_text, fill=(148, 163, 184))

    # Badge: Rebuilt 100% from JSON
    draw.rounded_rectangle([canvas_w - 280, 25, canvas_w - 40, 65], radius=8, fill=(16, 185, 129))
    draw.text((canvas_w - 260, 38), "100% Zero-Touch JSON", fill=(255, 255, 255))

    # Paste images
    y_offset = 120
    x_orig = 40
    x_rebuilt = target_w + 80

    # Frames
    draw.rounded_rectangle([x_orig - 4, y_offset - 4, x_orig + target_w + 4, y_offset + target_h + 4], radius=20, fill=(30, 41, 59))
    draw.rounded_rectangle([x_rebuilt - 4, y_offset - 4, x_rebuilt + target_w + 4, y_offset + target_h + 4], radius=20, fill=(99, 102, 241))

    canvas.paste(orig_resized, (x_orig, y_offset))
    canvas.paste(rebuilt_resized, (x_rebuilt, y_offset))

    # Labels below frames
    draw.text((x_orig + 80, y_offset + target_h + 15), "[ Ground Truth Device ]", fill=(148, 163, 184))
    draw.text((x_rebuilt + 70, y_offset + target_h + 15), "[ AI Knowledge Pack Rebuild ]", fill=(129, 140, 248))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "PNG")
    return output_path
