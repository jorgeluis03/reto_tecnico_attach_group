import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator import generate_background
from src.composer import compose
from src.templates import load_template


ASSETS_DIR = Path(__file__).parent.parent / "assets"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main():
    load_dotenv(Path(__file__).parent.parent / ".env")

    parser = argparse.ArgumentParser(
        description="Creative Pipeline: AI background + deterministic brand composition"
    )
    parser.add_argument("--prompt", default="", help="Prompt for AI background generation")
    parser.add_argument("--background", default=None, help="Path to a local image to use as background (skips AI generation)")
    parser.add_argument(
        "--template",
        choices=["story", "post", "banner"],
        default="post",
        help="Output format template (default: post)",
    )
    parser.add_argument("--headline", default="", help="Headline text to render on the creative")
    parser.add_argument("--legal-text", default="", help="Legal disclaimer text")
    parser.add_argument("--logo", default=str(ASSETS_DIR / "logo.png"), help="Path to logo file")
    parser.add_argument("--font", default=str(ASSETS_DIR / "tipografia.otf"), help="Path to font file")
    parser.add_argument("--output", default=None, help="Output file path (auto-generated if not set)")

    args = parser.parse_args()

    template = load_template(args.template)

    if args.background:
        from PIL import Image
        print(f"[1/3] Loading local background: {args.background}")
        background = Image.open(args.background).convert("RGB")
    elif args.prompt:
        print(f"[1/3] Generating background ({template.width}x{template.height})...")
        background = generate_background(args.prompt, template.width, template.height)
    else:
        parser.error("Either --prompt or --background is required")

    print("[2/3] Compositing brand assets...")
    result = compose(
        background=background,
        template=template,
        logo_path=Path(args.logo),
        font_path=Path(args.font),
        headline=args.headline,
        legal_text=args.legal_text,
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"{args.template}_{timestamp}.png"

    result.save(output_path, "PNG")
    print(f"[3/3] Done! Saved to: {output_path}")


if __name__ == "__main__":
    main()
