#!/usr/bin/env python3
"""Полная живая склейка: утверждённая завязка + хвост Wan + плашки Pillow."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path("/workspace/one-soul-series-1")
CUTS = ROOT / "preview" / "wan-cuts"
AUDIO = CUTS / "audio"
STYLE = ROOT / "style"
OUT = ROOT / "preview" / "series1-wan.mp4"
ART = Path("/opt/cursor/artifacts/series1-wan.mp4")

# (video or still, optional vo, kind)
# kind: clip = living video trimmed to vo or own duration
# still = pillow card with silence
PIECES = [
    (ROOT / "preview" / "series1-wan-open.mp4", None, "clip"),
    (STYLE / "c-years-later.png", 2.4, "still"),
    (CUTS / "05-silent.mp4", 4.0, "clip"),
    (CUTS / "06-father-d1.mp4", AUDIO / "father-d1.mp3", "clip"),
    (CUTS / "07-father-d2.mp4", AUDIO / "father-d2.mp3", "clip"),
    (CUTS / "08-defend-b1.mp4", AUDIO / "shushen-b1.mp3", "clip"),
    (CUTS / "09-defend-b2.mp4", AUDIO / "shushen-b2.mp3", "clip"),
    (CUTS / "10-vay.mp4", AUDIO / "father-e.mp3", "clip"),
    (ROOT / "preview" / "piece-end-wan27.mp4", AUDIO / "shushen-c.mp3", "clip"),
    (STYLE / "c-08-endcard.png", 3.2, "still"),
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


def encode(cmd_tail: list[str], dest: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            *cmd_tail,
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
    work = Path("/tmp/mux-wan-full")
    work.mkdir(parents=True, exist_ok=True)
    normed: list[Path] = []
    for i, (src, vo, kind) in enumerate(PIECES):
        dest = work / f"n{i:02d}.mp4"
        if kind == "still":
            if not src.exists():
                raise SystemExit(f"missing still {src}")
            seconds = float(vo)
            encode(
                [
                    "-loop",
                    "1",
                    "-framerate",
                    "24",
                    "-i",
                    str(src),
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=r=48000:cl=mono",
                    "-t",
                    f"{seconds:.3f}",
                    "-shortest",
                ],
                dest,
            )
            print(f"  {src.name} still {seconds:.3f}s")
        else:
            if not src.exists():
                raise SystemExit(f"missing clip {src}")
            if vo is None:
                seconds = dur(src)
            elif isinstance(vo, Path):
                if not vo.exists():
                    raise SystemExit(f"missing vo {vo}")
                seconds = min(dur(src), dur(vo) + 0.04)
            else:
                seconds = min(dur(src), float(vo))
            encode(["-i", str(src), "-t", f"{seconds:.3f}"], dest)
            print(f"  {src.name} keep {seconds:.3f}s")
        normed.append(dest)

    n = len(normed)
    ins: list[str] = []
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
