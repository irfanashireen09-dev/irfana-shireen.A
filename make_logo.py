"""Generates Image/Logo.png (white, for dark UI) and Image/inverseLogo.png (dark, for documents)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "Image"
OUT.mkdir(exist_ok=True)


def font(size):
    for name in ("DejaVuSerif.ttf", "LiberationSerif-Regular.ttf", "Times New Roman.ttf", "times.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_logo(color, path):
    w, h = 600, 160
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = 5
    cx, top = 75, 25
    d.line([(cx, top), (cx, 125)], fill=color, width=lw)                 # pillar
    d.line([(cx - 55, top + 12), (cx + 55, top + 12)], fill=color, width=lw)  # beam
    d.line([(cx - 30, 130), (cx + 30, 130)], fill=color, width=lw)       # base
    for x in (cx - 45, cx + 45):                                         # pans
        d.line([(x, top + 12), (x - 20, 80)], fill=color, width=3)
        d.line([(x, top + 12), (x + 20, 80)], fill=color, width=3)
        d.arc([x - 22, 62, x + 22, 98], 0, 180, fill=color, width=lw)
    d.text((150, 30), "LegalEase", font=font(72), fill=color)
    img.save(path)


draw_logo((255, 255, 255, 255), OUT / "Logo.png")
draw_logo((20, 20, 20, 255), OUT / "inverseLogo.png")
print("Logos created in", OUT)