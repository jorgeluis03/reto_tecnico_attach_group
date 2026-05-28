import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ElementConfig:
    x_percent: float
    y_percent: float
    max_width_percent: float
    anchor: str
    max_height_percent: float = 0
    font_size: int = 0
    color: str = "#FFFFFF"


@dataclass
class Template:
    name: str
    width: int
    height: int
    logo: ElementConfig
    headline: ElementConfig
    legal: ElementConfig


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def load_template(name: str) -> Template:
    path = TEMPLATES_DIR / f"{name}.json"
    if not path.exists():
        available = [f.stem for f in TEMPLATES_DIR.glob("*.json")]
        raise ValueError(f"Template '{name}' not found. Available: {available}")

    data = json.loads(path.read_text(encoding="utf-8"))
    return Template(
        name=data["name"],
        width=data["width"],
        height=data["height"],
        logo=ElementConfig(**data["logo"]),
        headline=ElementConfig(**data["headline"]),
        legal=ElementConfig(**data["legal"]),
    )
