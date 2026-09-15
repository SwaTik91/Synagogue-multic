#!/usr/bin/env python3
"""Плашки Pillow. Не drawtext: он съедает пробелы в кириллице."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path("/workspace/one-soul-series-1/style")
FONT = Path("/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT), size)


def darken(src: Path, factor: float = 0.42) -> Image.Image:
    im = Image.open(src).convert("RGB")
    im = ImageEnhance.Brightness(im).enhance(factor)
    veil = Image.new("RGB", im.size, (8, 4, 2))
    return Image.blend(im, veil, 0.18)


def word_width(draw: ImageDraw.ImageDraw, word: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), word, font=font)
    return bbox[2] - bbox[0]


def line_size(
    draw: ImageDraw.ImageDraw, words: list[str], font: ImageFont.FreeTypeFont, word_gap: int
) -> tuple[int, int]:
    widths = [word_width(draw, w, font) for w in words]
    bbox = draw.textbbox((0, 0), "Ну", font=font)
    height = bbox[3] - bbox[1]
    width = sum(widths) + word_gap * max(0, len(words) - 1)
    return width, height


def draw_words(
    draw: ImageDraw.ImageDraw,
    words: list[str],
    font: ImageFont.FreeTypeFont,
    x: int,
    y: int,
    word_gap: int,
) -> None:
    cream = (245, 230, 200)
    shadow = (20, 10, 6)
    cursor = x
    for word in words:
        for dx, dy in ((3, 4), (0, 3), (3, 0)):
            draw.text((cursor + dx, y + dy), word, font=font, fill=shadow)
        draw.text((cursor, y), word, font=font, fill=cream)
        cursor += word_width(draw, word, font) + word_gap


def draw_lines(
    im: Image.Image,
    lines: list[tuple[list[str], ImageFont.FreeTypeFont, int]],
    gap: int,
) -> None:
    draw = ImageDraw.Draw(im)
    sizes = [line_size(draw, words, font, word_gap) for words, font, word_gap in lines]
    total_h = sum(h for _, h in sizes) + gap * (len(lines) - 1)
    y = (im.height - total_h) // 2
    cx = im.width // 2
    for (words, font, word_gap), (w, h) in zip(lines, sizes):
        draw_words(draw, words, font, cx - w // 2, y, word_gap)
        y += h + gap


def main() -> None:
    years = darken(ROOT / "c-years-bg.png", 0.38)
    years = years.filter(ImageFilter.GaussianBlur(0.4))
    draw_lines(
        years,
        [
            (["Несколько", "лет"], load_font(92), 48),
            (["спустя"], load_font(92), 48),
        ],
        gap=36,
    )
    years.save(ROOT / "c-years-later.png", optimize=True)

    end = darken(ROOT / "c-08-end.png", 0.48)
    draw_lines(
        end,
        [
            (["Продолжение"], load_font(86), 40),
            (["во", "2-й", "серии..."], load_font(80), 40),
            (["Подпишись", "на", "One", "Soul"], load_font(42), 28),
        ],
        gap=28,
    )
    end.save(ROOT / "c-08-endcard.png", optimize=True)
    print("wrote", ROOT / "c-years-later.png", ROOT / "c-08-endcard.png")


if __name__ == "__main__":
    main()
