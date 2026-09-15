#!/usr/bin/env python3
"""Склейка завязки варианта C из живых Wan-кусков + наш Sulafat уже в клипах."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path("/workspace/one-soul-series-1")
CUTS = ROOT / "preview" / "wan-cuts"
OUT = ROOT / "preview" / "series1-wan-open.mp4"
ART = Path("/opt/cursor/artifacts/series1-wan-open.mp4")


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


def norm(src: Path, dest: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
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
    pieces = [
        CUTS / "01-judge.mp4",
        CUTS / "02-allo.mp4",
        CUTS / "03-reject.mp4",
        CUTS / "04-proud.mp4",
    ]
    missing = [p for p in pieces if not p.exists()]
    if missing:
        raise SystemExit(f"missing clips: {missing}")

    normed = []
    for i, src in enumerate(pieces):
        dest = work / f"n{i:02d}.mp4"
        norm(src, dest)
        print(f"  {src.name} {dur(dest):.3f}s")
        normed.append(dest)

    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in normed))
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-c",
            "copy",
            str(OUT),
        ]
    )
    ART.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, ART)
    print("wrote", OUT, "dur", dur(OUT))


if __name__ == "__main__":
    main()
