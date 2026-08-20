#!/usr/bin/env python3
"""Overlay titles onto generated cover art and export web-sized JPEGs."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
COVERS = ROOT / "covers"
WEB = COVERS / "web"

CASLON = "/System/Library/Fonts/Supplemental/BigCaslon.ttf"
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEORGIA_I = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
NEWYORK = "/System/Library/Fonts/NewYork.ttf"

COVERS_SPEC = [
    {
        "src": "cover-the-womp-life.png",
        "out": "the-womp-life",
        "ink": (28, 24, 18),
        "rule": (110, 86, 48),
        "kicker": "THE WOMP INSTITUTE  ·  VOLUME I",
        "title": ["THE", "WOMP LIFE"],
        "subtitle": "Whomping, Whomping to Live,\nand the Mathematics of the Great Womp",
        "footer": "A field guide for inhabited time",
        "scrim": "light",
    },
    {
        "src": "cover-the-unseen-womp.png",
        "out": "the-unseen-womp",
        "ink": (244, 236, 214),
        "rule": (196, 164, 96),
        "kicker": "THE WOMP INSTITUTE  ·  VOLUME II",
        "title": ["THE", "UNSEEN WOMP"],
        "subtitle": "A spiritual treatise on the soul’s rebound\nand the quiet practice of inner whomping",
        "footer": "For the chamber no one else can hear",
        "scrim": "dark",
    },
    {
        "src": "cover-womp-mechanics.png",
        "out": "womp-mechanics",
        "ink": (18, 32, 58),
        "rule": (140, 72, 36),
        "kicker": "THE WOMP INSTITUTE  ·  VOLUME III",
        "title": ["WOMP", "MECHANICS"],
        "subtitle": "Compression, release, and the\nthermodynamics of lived intensity",
        "footer": "A scientific inquiry into invented quantities",
        "scrim": "light",
    },
    {
        "src": "cover-annals-of-whomping.png",
        "out": "the-annals-of-whomping",
        "ink": (62, 38, 18),
        "rule": (132, 84, 36),
        "kicker": "THE WOMP INSTITUTE  ·  VOLUME IV",
        "title": ["THE ANNALS OF", "WHOMPING"],
        "subtitle": "From the first drum to the present pulse:\na history of humanity’s oldest undocumented practice",
        "footer": "Scholars disagree. The drum does not.",
        "scrim": "light",
    },
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def draw_centered(draw: ImageDraw.ImageDraw, text: str, y: int, fnt, fill, width: int) -> int:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) / 2, y), text, font=fnt, fill=fill)
    return bbox[3] - bbox[1]


def letterspace(draw, text: str, y: int, fnt, fill, width: int, tracking: float) -> int:
    glyphs = list(text)
    sizes = [draw.textbbox((0, 0), g, font=fnt) for g in glyphs]
    widths = [b[2] - b[0] for b in sizes]
    total = sum(widths) + tracking * (len(glyphs) - 1)
    x = (width - total) / 2
    height = 0
    for g, w, b in zip(glyphs, widths, sizes):
        draw.text((x, y), g, font=fnt, fill=fill)
        x += w + tracking
        height = max(height, b[3] - b[1])
    return height


def add_scrim(img: Image.Image, kind: str) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size
    if kind == "dark":
        for i in range(0, int(h * 0.46)):
            alpha = int(150 * (1 - i / (h * 0.46)))
            draw.line([(0, i), (w, i)], fill=(8, 12, 28, alpha))
        for i in range(int(h * 0.82), h):
            t = (i - h * 0.82) / (h * 0.18)
            draw.line([(0, i), (w, i)], fill=(8, 12, 28, int(140 * t)))
    else:
        for i in range(0, int(h * 0.42)):
            alpha = int(92 * (1 - i / (h * 0.42)))
            draw.line([(0, i), (w, i)], fill=(245, 238, 224, alpha))
        for i in range(int(h * 0.86), h):
            t = (i - h * 0.86) / (h * 0.14)
            draw.line([(0, i), (w, i)], fill=(245, 238, 224, int(110 * t)))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def compose(spec: dict) -> None:
    src = Image.open(ASSETS / spec["src"]).convert("RGB")
    src = ImageEnhance.Contrast(src).enhance(1.04)
    src = ImageEnhance.Color(src).enhance(0.92)
    art = add_scrim(src, spec["scrim"]).convert("RGB")
    draw = ImageDraw.Draw(art)
    w, h = art.size
    ink = spec["ink"]
    rule = spec["rule"]

    kicker_font = font(GEORGIA, 18)
    title_font = font(CASLON, 72 if max(len(line) for line in spec["title"]) < 14 else 58)
    sub_font = font(GEORGIA_I, 22)
    foot_font = font(GEORGIA, 16)

    y = 78
    letterspace(draw, spec["kicker"], y, kicker_font, ink, w, 2.4)
    y += 36
    draw.line([(w * 0.38, y), (w * 0.62, y)], fill=rule, width=1)
    y += 36

    for line in spec["title"]:
        size = 76 if len(line) < 12 else 58 if len(line) < 18 else 48
        f = font(CASLON, size)
        draw_centered(draw, line, y, f, ink, w)
        y += size + 8

    y += 10
    draw.line([(w * 0.28, y), (w * 0.72, y)], fill=rule, width=2)
    y += 28

    for line in spec["subtitle"].split("\n"):
        draw_centered(draw, line, y, sub_font, ink, w)
        y += 32

    fy = h - 92
    draw.line([(w * 0.35, fy), (w * 0.65, fy)], fill=rule, width=1)
    draw_centered(draw, spec["footer"], fy + 16, foot_font, ink, w)

    COVERS.mkdir(exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    print_path = COVERS / f"{spec['out']}.png"
    web_path = WEB / f"{spec['out']}.jpg"
    art.save(print_path, "PNG")
    web = art.resize((680, 1020), Image.Resampling.LANCZOS)
    web = web.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=2))
    web.save(web_path, "JPEG", quality=86, optimize=True)
    print(f"wrote {print_path.name} and {web_path.name}")


def main() -> None:
    for spec in COVERS_SPEC:
        compose(spec)
    hero = Image.open(ASSETS / "hero-institute.png").convert("RGB")
    hero = ImageEnhance.Color(hero).enhance(0.85)
    hero = ImageEnhance.Contrast(hero).enhance(1.08)
    hero.resize((1600, 1067), Image.Resampling.LANCZOS).save(
        WEB / "hero-institute.jpg", "JPEG", quality=84, optimize=True
    )
    emblem = Image.open(ASSETS / "emblem-womp.png").convert("RGB")
    emblem.resize((320, 320), Image.Resampling.LANCZOS).save(
        WEB / "emblem-womp.jpg", "JPEG", quality=85, optimize=True
    )
    print("hero and emblem exported")


if __name__ == "__main__":
    main()
