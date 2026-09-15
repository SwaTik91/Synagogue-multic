#!/usr/bin/env python3
"""Склейка варианта В: 3D-клипы + те же голоса, что в Б."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path("/workspace/one-soul-series-1")
CLIPS = ROOT / "preview" / "variant-c-clips"
VO = ROOT / "voice" / "renders"
STYLE = ROOT / "style"
I2V = Path("/tmp/i2v-c")
WORK = Path("/tmp/mux-c")
OUT = ROOT / "preview" / "series1-variant-c.mp4"
ART = Path("/opt/cursor/artifacts/series1-variant-c.mp4")
ART2 = Path("/opt/cursor/artifacts/one-soul-listen/series1-variant-c.mp4")


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
    print("+", " ".join(str(c) for c in cmd[:14]))
    subprocess.check_call(cmd)


def ms(t: float) -> int:
    return int(round(t * 1000))


def kenburns(src: Path, dest: Path, seconds: float) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            "24",
            "-i",
            str(src),
            "-vf",
            "scale=1180:2098:force_original_aspect_ratio=increase,"
            f"crop=1080:1920:'(iw-ow)*t/{seconds}':'(ih-oh)*t/{seconds}',setsar=1",
            "-t",
            str(seconds),
            "-r",
            "24",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-an",
            str(dest),
        ]
    )


def take_clip(name: str, still: Path, seconds: float) -> Path:
    CLIPS.mkdir(parents=True, exist_ok=True)
    live = I2V / f"{name}.mp4"
    dest = CLIPS / f"{name}.mp4"
    if live.exists() and live.stat().st_size > 10000:
        shutil.copy2(live, dest)
        return dest
    kenburns(still, dest, seconds)
    return dest


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    pieces = [
        take_clip("01", STYLE / "c-opener-judge.png", 7.0),
        take_clip("02", STYLE / "c-02-phone.png", 10.0),
        take_clip("02b", STYLE / "c-02-proud.png", 8.5),
        take_clip("years", STYLE / "c-years-later.png", 2.4),
        take_clip("03", STYLE / "c-03-silent.png", 3.5),
        take_clip("04", STYLE / "c-04-talk.png", 9.8),
        take_clip("05", STYLE / "c-05-defends.png", 11.3),
        take_clip("06", STYLE / "c-06-vay.png", 5.4),
        take_clip("07", STYLE / "c-07-dont.png", 4.0),
        take_clip("08", STYLE / "c-08-endcard.png", 5.0),
    ]

    normed: list[Path] = []
    for i, src in enumerate(pieces):
        dest = WORK / f"n{i:02d}.mp4"
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
                "veryfast",
                "-crf",
                "18",
                "-an",
                str(dest),
            ]
        )
        normed.append(dest)

    lst = WORK / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in normed))
    silent = WORK / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])

    d01, d02, d02b, d_years, d03, d04, d05, d06 = (dur(p) for p in normed[:8])
    t_a = d01
    t_d = d01 + d02 + d02b + d_years + d03
    t_b = t_d + d04
    t_e = t_b + d05
    t_c = t_e + d06
    print(f"offsets a={t_a:.3f} d={t_d:.3f} b={t_b:.3f} e={t_e:.3f} c={t_c:.3f}")

    filt = (
        f"[1:a]adelay={ms(0)}|{ms(0)},volume=2.6[j];"
        f"[2:a]adelay={ms(t_a)}|{ms(t_a)},volume=2.6[a];"
        f"[3:a]adelay={ms(t_d)}|{ms(t_d)},volume=2.6[d];"
        f"[4:a]adelay={ms(t_b)}|{ms(t_b)},volume=2.6[b];"
        f"[5:a]adelay={ms(t_e)}|{ms(t_e)},volume=2.6[e];"
        f"[6:a]adelay={ms(t_c)}|{ms(t_c)},volume=2.6[c];"
        "[j][a][d][b][e][c]amix=inputs=6:duration=longest:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.95,apad[aout]"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent),
            "-i",
            str(VO / "shushen-judge.mp3"),
            "-i",
            str(VO / "shushen-a.mp3"),
            "-i",
            str(VO / "father-d.mp3"),
            "-i",
            str(VO / "shushen-b.mp3"),
            "-i",
            str(VO / "father-e.mp3"),
            "-i",
            str(VO / "shushen-c.mp3"),
            "-filter_complex",
            filt,
            "-map",
            "0:v",
            "-map",
            "[aout]",
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
            "-shortest",
            str(OUT),
        ]
    )
    ART.parent.mkdir(parents=True, exist_ok=True)
    ART2.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, ART)
    shutil.copy2(OUT, ART2)
    print("wrote", OUT, "dur", dur(OUT))


if __name__ == "__main__":
    main()
