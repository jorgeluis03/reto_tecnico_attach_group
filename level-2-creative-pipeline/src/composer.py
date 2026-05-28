from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from src.templates import Template, ElementConfig


def compose(
    background: Image.Image,
    template: Template,
    logo_path: Path,
    font_path: Path,
    headline: str,
    legal_text: str,
) -> Image.Image:
    canvas = background.copy().resize((template.width, template.height), Image.LANCZOS)

    _place_logo(canvas, logo_path, template.logo, template.width, template.height)
    _draw_text(canvas, headline, font_path, template.headline, template.width, template.height)
    _draw_text(canvas, legal_text, font_path, template.legal, template.width, template.height)

    return canvas


def _place_logo(
    canvas: Image.Image,
    logo_path: Path,
    config: ElementConfig,
    canvas_w: int,
    canvas_h: int,
) -> None:
    logo = Image.open(logo_path).convert("RGBA")

    max_w = int(canvas_w * config.max_width_percent / 100)
    max_h = int(canvas_h * config.max_height_percent / 100)

    logo.thumbnail((max_w, max_h), Image.LANCZOS)

    x = int(canvas_w * config.x_percent / 100)
    y = int(canvas_h * config.y_percent / 100)

    if config.anchor == "center":
        x -= logo.width // 2
        y -= logo.height // 2

    canvas.paste(logo, (x, y), logo)


def _draw_text(
    canvas: Image.Image,
    text: str,
    font_path: Path,
    config: ElementConfig,
    canvas_w: int,
    canvas_h: int,
) -> None:
    if not text:
        return

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(font_path), config.font_size)

    max_w = int(canvas_w * config.max_width_percent / 100)
    lines = _wrap_text(text, font, max_w)
    rendered = "\n".join(lines)

    bbox = draw.multiline_textbbox((0, 0), rendered, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = int(canvas_w * config.x_percent / 100)
    y = int(canvas_h * config.y_percent / 100)

    if config.anchor == "center":
        x -= text_w // 2
        y -= text_h // 2

    draw.multiline_text(
        (x, y),
        rendered,
        font=font,
        fill=config.color,
        align="center",
    )


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines
