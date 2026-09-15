#!/usr/bin/env python3
"""Склейка живого варианта А.

Завязка — бракует фото. Между молодым сыном и 28 годами — плашка
«Несколько лет спустя». Отец сначала сидит молча; когда говорит,
рот идёт от RMS голоса, рука не бьёт по столу.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/workspace/one-soul-series-1")
sys.path.insert(0, str(ROOT / "preview"))
import lipsync  # noqa: E402

CLIPS = ROOT / "preview" / "variant-a-clips"
VO = ROOT / "voice" / "renders"
SB = ROOT / "storyboard"
WORK = Path("/tmp/mux-living")
OUT = ROOT / "preview" / "series1-variant-a-living.mp4"
ART = Path("/opt/cursor/artifacts/one-soul-listen/series1-variant-a-living.mp4")
ART_ROOT = Path("/opt/cursor/artifacts/series1-variant-a-living.mp4")


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
    print("+", " ".join(cmd[:14]))
    subprocess.check_call(cmd)


def ms(t: float) -> int:
    return int(round(t * 1000))


def make_years_card(dest: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            "24",
            "-i",
            str(SB / "sb-years-later.png"),
            "-vf",
            "scale=1120:1991:force_original_aspect_ratio=increase,"
            "crop=1080:1920:'(iw-ow)*t/2.4':'(ih-oh)*t/2.4',setsar=1",
            "-t",
            "2.4",
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


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    CLIPS.mkdir(parents=True, exist_ok=True)

    years = CLIPS / "years-later.mp4"
    make_years_card(years)

    talk04 = CLIPS / "04-talk.mp4"
    lipsync.render(
        VO / "father-d.mp3",
        SB / "sb-04-mouth-closed.png",
        SB / "sb-04-mouth-talk.png",
        SB / "sb-04-mouth-talk.png",
        talk04,
        min_seconds=9.8,
    )
    talk06 = CLIPS / "06-talk.mp4"
    lipsync.render(
        VO / "father-e.mp3",
        SB / "sb-06-mouth-closed.png",
        SB / "sb-06-mouth-talk.png",
        SB / "sb-06-mouth-talk.png",
        talk06,
        min_seconds=5.4,
    )

    kb = WORK / "03-silent.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            "24",
            "-i",
            str(SB / "sb-03-silent-seated.png"),
            "-vf",
            "scale=780:1387:force_original_aspect_ratio=increase,"
            "crop=720:1280:'(iw-ow)*t/3.5':'(ih-oh)*t/3.5',setsar=1",
            "-t",
            "3.5",
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
            str(kb),
        ]
    )

    end = WORK / "08.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            "24",
            "-i",
            str(SB / "sb-08-endcard.png"),
            "-vf",
            "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1",
            "-t",
            "5",
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
            str(end),
        ]
    )

    pieces = [
        CLIPS / "01.mp4",
        CLIPS / "02.mp4",
        CLIPS / "02b.mp4",
        years,
        kb,
        talk04,
        CLIPS / "05.mp4",
        talk06,
        CLIPS / "07.mp4",
        end,
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
            str(silent),
        ]
    )

    d01, d02, d02b, d_years, d03, d04, d05, d06 = (dur(p) for p in normed[:8])
    t_a = d01
    t_d = d01 + d02 + d02b + d_years + d03
    t_b = t_d + d04
    t_e = t_b + d05
    t_c = t_e + d06
    print(
        f"offsets judge=0.000 a={t_a:.3f} years={d01+d02+d02b:.3f} "
        f"father-d={t_d:.3f} b={t_b:.3f} e={t_e:.3f} c={t_c:.3f}"
    )

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
    shutil.copy2(OUT, ART)
    shutil.copy2(OUT, ART_ROOT)
    print("wrote", OUT)
    print("copied", ART)
    print("copied", ART_ROOT)


if __name__ == "__main__":
    main()
