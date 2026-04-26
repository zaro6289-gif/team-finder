import colorsys
import random
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


def generate_avatar(name, email):
    size = 200
    hue = random.random()
    rgb = tuple(int(x * 255) for x in colorsys.hls_to_rgb(hue, 0.6, 0.5))

    image = Image.new("RGB", (size, size), rgb)
    draw = ImageDraw.Draw(image)

    first_letter = name[0].upper() if name else "?"

    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), first_letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2
    y = (size - text_height) // 2

    draw.text((x, y), first_letter, fill="white", font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), f"avatar_{email}.png")
