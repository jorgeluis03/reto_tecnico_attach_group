import io
import os
from PIL import Image, ImageOps
from google import genai


PHOTO_MODIFIERS = (
    "shot on smartphone, 24mm lens, direct flash, natural sensor noise, "
    "photorealistic, high resolution, no text, no watermark, no logo"
)


def generate_background(prompt: str, width: int, height: int) -> Image.Image:
    project_id = os.environ.get("GCP_PROJECT_ID")
    location = os.environ.get("GCP_LOCATION", "us-central1")
    if not project_id:
        raise RuntimeError("GCP_PROJECT_ID not set. Add it to .env file.")

    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
    )

    full_prompt = f"{prompt}, {PHOTO_MODIFIERS}"
    aspect_ratio = _closest_aspect_ratio(width, height)

    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=full_prompt,
        config=genai.types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=aspect_ratio,
        ),
    )

    image_data = response.generated_images[0].image.image_bytes
    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    img = ImageOps.fit(img, (width, height), Image.LANCZOS)
    return img


def _closest_aspect_ratio(width: int, height: int) -> str:
    ratios = ["1:1", "16:9", "9:16", "4:3", "3:4"]
    target = width / height
    ratio_values = {
        "1:1": 1.0,
        "16:9": 16 / 9,
        "9:16": 9 / 16,
        "4:3": 4 / 3,
        "3:4": 3 / 4,
    }
    return min(ratios, key=lambda r: abs(ratio_values[r] - target))
