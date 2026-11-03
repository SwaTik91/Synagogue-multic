#!/usr/bin/env python3
"""Кладет портрет первой девушки со штампом «ЗАМУЖЕМ» на стекло телефона.

Модель экран не рисует: мелкое лицо и буквы на нём размазываются.
Берётся уже снятый немой кусок и готовый портрет stills/girl-1-stamped.png.
Пальцы остаются поверх картинки.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path("/workspace/one-soul-series-2")
SRC = ROOT / "preview/silent/k09-phone.mp4"
GIRL = ROOT / "stills/girl-1-stamped.png"
OUT = ROOT / "preview/silent/k09-phone-photo.mp4"
WORK = Path("/tmp/phone-photo")


def measure(frame: np.ndarray) -> tuple[int, int, int, int]:
    """Кромка стекла: бока по нейтральному пятну, верх и низ по чёрной рамке."""
    rgb = frame.astype(np.int16)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    neutral = (np.abs(r - g) < 32) & (np.abs(g - b) < 38) & (r > 18) & (r < 180)
    lefts: list[int] = []
    rights: list[int] = []
    for y in (280, 360, 440, 520, 600):
        xs = np.where(neutral[y, 140:560])[0] + 140
        if len(xs) < 30:
            continue
        left, right = _longest(xs)
        lefts.append(left)
        rights.append(right)
    if not lefts:
        raise RuntimeError("screen edge not found")
    left = int(np.median(lefts))
    right = int(np.median(rights))
    cx = (left + right) // 2
    top = _bezel(rgb, cx, range(250, 140, -1))
    bot = _bezel(rgb, cx, range(640, 790))
    return left, top, right, bot


def _bezel(rgb: np.ndarray, cx: int, rows) -> int:
    for y in rows:
        if int(rgb[y, cx].max()) < 18:
            return y
    raise RuntimeError("bezel not found")


def _longest(idx: np.ndarray) -> tuple[int, int]:
    if len(idx) < 8:
        raise RuntimeError("screen edge not found")
    breaks = np.where(np.diff(idx) > 4)[0]
    starts = np.r_[0, breaks + 1]
    ends = np.r_[breaks, len(idx) - 1]
    i = int(np.argmax(ends - starts))
    return int(idx[starts[i]]), int(idx[ends[i]])


def smooth(boxes: np.ndarray) -> np.ndarray:
    k = 7
    pad = k // 2
    out = np.empty_like(boxes)
    for col in range(4):
        ext = np.pad(boxes[:, col], (pad, pad), mode="edge")
        out[:, col] = [np.median(ext[i : i + k]) for i in range(len(boxes))]
    return out


def composite(frame: Image.Image, girl: Image.Image, box: np.ndarray) -> Image.Image:
    left, top, right, bot = (int(round(v)) for v in box)
    # Стекло чуть внутри найденного пятна: верх размыт, низ упирается в чёрную кромку.
    left, top, right, bot = left + 4, top + 6, right - 4, bot - 8
    width, height = right - left, bot - top
    if width < 80 or height < 80:
        raise RuntimeError(f"screen too small: {width}x{height}")

    arr = np.asarray(frame).astype(np.int16)
    red, green, blue = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    skin = (red > 150) & (red > green + 30) & (red > blue + 40) & (green > 70)
    skin_img = Image.fromarray((skin.astype(np.uint8) * 255), "L").filter(ImageFilter.MaxFilter(3))

    gw, gh = girl.size
    scale = max(width / gw, height / gh)
    photo = girl.resize((int(round(gw * scale)), int(round(gh * scale))), Image.Resampling.LANCZOS)
    px = (photo.width - width) // 2
    py = (photo.height - height) // 2
    photo = photo.crop((px, py, px + width, py + height))

    edge = Image.new("L", (width, height), 0)
    ImageDraw.Draw(edge).rounded_rectangle((8, 8, width - 9, height - 9), radius=24, fill=255)
    edge = edge.filter(ImageFilter.GaussianBlur(7))
    dim = ImageEnhance.Brightness(photo).enhance(0.8)
    photo = Image.composite(photo, dim, edge)

    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=32, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.7))
    covered = skin_img.crop((left, top, right, bot))
    mask_a = np.clip(np.asarray(mask).astype(np.int16) - np.asarray(covered).astype(np.int16), 0, 255)
    frame.paste(photo, (left, top), Image.fromarray(mask_a.astype(np.uint8), "L"))
    return frame


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    src_dir = WORK / "in"
    out_dir = WORK / "out"
    src_dir.mkdir(exist_ok=True)
    out_dir.mkdir(exist_ok=True)
    subprocess.check_call([
        "ffmpeg", "-y", "-i", str(SRC), str(src_dir / "%04d.png"),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    paths = sorted(src_dir.glob("*.png"))
    girl = Image.open(GIRL).convert("RGB")
    boxes = np.array([measure(np.asarray(Image.open(p).convert("RGB"))) for p in paths], dtype=float)
    boxes = smooth(boxes)
    for path, box in zip(paths, boxes):
        frame = Image.open(path).convert("RGB")
        composite(frame, girl, box).save(out_dir / path.name)
    subprocess.check_call([
        "ffmpeg", "-y", "-framerate", "30", "-i", str(out_dir / "%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "17",
        "-r", "30", "-an", "-movflags", "+faststart", str(OUT),
    ])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
