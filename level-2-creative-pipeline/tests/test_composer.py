import pytest
from pathlib import Path
from PIL import Image, ImageDraw
from src.composer import compose, _place_logo, _draw_text, _wrap_text
from src.templates import Template, ElementConfig, load_template


ASSETS_DIR = Path(__file__).parent.parent / "assets"
FONT_PATH = ASSETS_DIR / "tipografia.otf"
LOGO_PATH = ASSETS_DIR / "logo.png"


@pytest.fixture
def mock_background():
    return Image.new("RGB", (1080, 1080), color=(50, 50, 50))


@pytest.fixture
def post_template():
    return load_template("post")


@pytest.fixture
def story_template():
    return load_template("story")


@pytest.fixture
def banner_template():
    return load_template("banner")


class TestCompose:
    def test_output_dimensions_post(self, mock_background, post_template):
        result = compose(mock_background, post_template, LOGO_PATH, FONT_PATH, "Test", "Legal")
        assert result.size == (1080, 1080)

    def test_output_dimensions_story(self, mock_background, story_template):
        result = compose(mock_background, story_template, LOGO_PATH, FONT_PATH, "Test", "Legal")
        assert result.size == (1080, 1920)

    def test_output_dimensions_banner(self, mock_background, banner_template):
        result = compose(mock_background, banner_template, LOGO_PATH, FONT_PATH, "Test", "Legal")
        assert result.size == (1200, 628)

    def test_logo_is_rendered(self, mock_background, post_template):
        bg_pixels = mock_background.resize((1080, 1080)).load()
        result = compose(mock_background, post_template, LOGO_PATH, FONT_PATH, "", "")
        result_pixels = result.load()
        # The logo region should differ from the plain background
        logo_y = int(1080 * post_template.logo.y_percent / 100)
        logo_x = int(1080 * post_template.logo.x_percent / 100)
        differs = False
        for dx in range(-20, 20):
            for dy in range(-20, 20):
                px, py = logo_x + dx, logo_y + dy
                if 0 <= px < 1080 and 0 <= py < 1080:
                    if result_pixels[px, py] != bg_pixels[px, py]:
                        differs = True
                        break
            if differs:
                break
        assert differs, "Logo should modify pixels in its expected region"

    def test_headline_is_rendered(self, mock_background, post_template):
        result_no_text = compose(mock_background, post_template, LOGO_PATH, FONT_PATH, "", "")
        result_with_text = compose(mock_background, post_template, LOGO_PATH, FONT_PATH, "BIG HEADLINE", "")
        # Center region should differ when headline is present
        center_y = int(1080 * post_template.headline.y_percent / 100)
        center_x = int(1080 * post_template.headline.x_percent / 100)
        p1 = result_no_text.load()
        p2 = result_with_text.load()
        differs = any(
            p1[center_x + dx, center_y] != p2[center_x + dx, center_y]
            for dx in range(-50, 50)
            if 0 <= center_x + dx < 1080
        )
        assert differs, "Headline should render text in the center region"

    def test_legal_text_is_rendered(self, mock_background, post_template):
        result_no_legal = compose(mock_background, post_template, LOGO_PATH, FONT_PATH, "", "")
        result_with_legal = compose(mock_background, post_template, LOGO_PATH, FONT_PATH, "", "Terms apply.")
        bottom_y = int(1080 * post_template.legal.y_percent / 100)
        center_x = int(1080 * post_template.legal.x_percent / 100)
        p1 = result_no_legal.load()
        p2 = result_with_legal.load()
        differs = any(
            p1[center_x + dx, bottom_y] != p2[center_x + dx, bottom_y]
            for dx in range(-50, 50)
            if 0 <= center_x + dx < 1080
        )
        assert differs, "Legal text should render at bottom region"

    def test_does_not_modify_original_background(self, mock_background, post_template):
        original_size = mock_background.size
        compose(mock_background, post_template, LOGO_PATH, FONT_PATH, "X", "Y")
        assert mock_background.size == original_size


class TestWrapText:
    def test_short_text_no_wrap(self):
        from PIL import ImageFont
        font = ImageFont.truetype(str(FONT_PATH), 40)
        lines = _wrap_text("Hello", font, 800)
        assert lines == ["Hello"]

    def test_long_text_wraps(self):
        from PIL import ImageFont
        font = ImageFont.truetype(str(FONT_PATH), 40)
        long_text = "This is a very long headline that should definitely wrap to multiple lines"
        lines = _wrap_text(long_text, font, 300)
        assert len(lines) > 1
