#!/usr/bin/env python3
"""Врезать Higgsfield Sync Lipsync в живой вариант В. Голос не трогаем."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path("/workspace/one-soul-series-1")
BASE = ROOT / "preview" / "series1-variant-c.mp4"
HF50 = ROOT / "higgsfield" / "back" / "02-around-50s-cu.mp4"
HFEND = ROOT / "higgsfield" / "back" / "01-end.mp4"
OUT = ROOT / "preview" / "series1-variant-c.mp4"
ART = Path("/opt/cursor/artifacts/series1-variant-c.mp4")
ART2 = Path("/opt/cursor/artifacts/one-soul-listen/series1-variant-c.mp4")
WORK = Path("/tmp/mux-c-lipsync.mp4")

# Living C offsets from mux-c.py clip lengths.
T_B = 46.792  # shushen-b / ~50s
T_C = 65.917  # shushen-c tender end
END_KEEP = 4.40  # drop Sync tail before hands melt


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


def main() -> None:
    d50 = dur(HF50)
    t50_end = T_B + d50
    t_end_end = T_C + END_KEEP
    filt = (
        f"[1:v]trim=start=0:end={d50:.3f},setpts=PTS-STARTPTS,"
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24,"
        f"setpts=PTS-STARTPTS+{T_B}/TB[cu];"
        f"[2:v]trim=start=0:end={END_KEEP:.3f},setpts=PTS-STARTPTS,"
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24,"
        f"setpts=PTS-STARTPTS+{T_C}/TB[end];"
        f"[0:v][cu]overlay=0:0:enable='between(t,{T_B},{t50_end:.3f})'[mid];"
        f"[mid][end]overlay=0:0:enable='between(t,{T_C},{t_end_end:.3f})'[v]"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(BASE),
        "-i",
        str(HF50),
        "-i",
        str(HFEND),
        "-filter_complex",
        filt,
        "-map",
        "[v]",
        "-map",
        "0:a",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        str(WORK),
    ]
    print("+", " ".join(cmd[:12]), "...")
    subprocess.check_call(cmd)
    shutil.copy2(WORK, OUT)
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART2.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, ART)
    shutil.copy2(OUT, ART2)
    print("wrote", OUT, "dur", dur(OUT), "overlays", T_B, t50_end, T_C, t_end_end)


if __name__ == "__main__":
    main()
