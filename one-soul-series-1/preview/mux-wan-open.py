#!/usr/bin/env python3
"""Склейка завязки: живые Wan-куски, обрезанные по нашему голосу."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path("/workspace/one-soul-series-1")
CUTS = ROOT / "preview" / "wan-cuts"
AUDIO = CUTS / "audio"
OUT = ROOT / "preview" / "series1-wan-open.mp4"
ART = Path("/opt/cursor/artifacts/series1-wan-open.mp4")

# Клип длиннее голоса — хвост Wan орёт без звука и плывут руки. Режем по дублю.
PIECES = [
    (CUTS / "01-judge.mp4", AUDIO / "shushen-judge.mp3"),
    (CUTS / "02-allo.mp4", AUDIO / "shushen-a1.mp3"),
    (CUTS / "03-reject.mp4", AUDIO / "shushen-a2.mp3"),
    (CUTS / "04-proud.mp4", AUDIO / "shushen-a3.mp3"),
]


def dur(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:12]))
    subprocess.check_call(cmd)


def norm(src: Path, dest: Path, seconds: float) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-t",
            f"{seconds:.3f}",
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "1",
            str(dest),
        ]
    )


def main() -> None:
    work = Path("/tmp/mux-wan-open")
    work.mkdir(parents=True, exist_ok=True)
    missing = [p for p, a in PIECES if not p.exists() or not a.exists()]
    if missing:
        raise SystemExit(f"missing: {missing}")

    normed: list[Path] = []
    for i, (src, vo) in enumerate(PIECES):
        dest = work / f"n{i:02d}.mp4"
        seconds = min(dur(src), dur(vo) + 0.04)
        norm(src, dest, seconds)
        print(f"  {src.name} keep {seconds:.3f}s (vo {dur(vo):.3f})")
        normed.append(dest)

    n = len(normed)
    ins = []
    for p in normed:
        ins.extend(["-i", str(p)])
    pairs = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    run(
        [
            "ffmpeg",
            "-y",
            *ins,
            "-filter_complex",
            f"{pairs}concat=n={n}:v=1:a=1[v][a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "1",
            str(OUT),
        ]
    )
    ART.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, ART)
    print("wrote", OUT, "dur", dur(OUT))


if __name__ == "__main__":
    main()
