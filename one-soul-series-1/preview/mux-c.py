#!/usr/bin/env python3
"""Склейка варианта В: I2V в тишине, рот по RMS на каждой реплике."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/workspace/one-soul-series-1")
sys.path.insert(0, str(ROOT / "preview"))
import lipsync  # noqa: E402

CLIPS = ROOT / "preview" / "variant-c-clips"
STYLE = ROOT / "style"
I2V = Path("/tmp/i2v-c2")
VO = ROOT / "voice" / "renders" / "slow"
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
    print("+", " ".join(str(c) for c in cmd[:16]))
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
            f"{seconds:.3f}",
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


def take_i2v(name: str, still: Path, seconds: float) -> Path:
    CLIPS.mkdir(parents=True, exist_ok=True)
    live = I2V / f"{name}.mp4"
    dest = CLIPS / f"{name}.mp4"
    if live.exists() and live.stat().st_size > 10000:
        shutil.copy2(live, dest)
        return dest
    kenburns(still, dest, seconds)
    return dest


def flap(audio: Path, closed: Path, opened: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print("lipsync", dest.name, "from", audio.name)
    lipsync.render(audio, closed, opened, opened, dest)
    return dest


def take_time(src: Path, dest: Path, start: float, seconds: float) -> Path:
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
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
            "veryfast",
            "-crf",
            "18",
            "-an",
            str(dest),
        ]
    )
    return dest


def punch(src: Path, dest: Path, seconds: float) -> Path:
    """Scale lip-flap up and add a slow push-in so it does not sit still."""
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vf",
            "scale=1180:2098:force_original_aspect_ratio=increase,"
            f"crop=1080:1920:'(iw-ow)*t/{max(seconds, 0.1)}':'(ih-oh)*t/{max(seconds, 0.1)}',"
            "setsar=1,fps=24",
            "-t",
            f"{seconds:.3f}",
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
    return dest


def norm_i2v(src: Path, dest: Path) -> Path:
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
    return dest


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    CLIPS.mkdir(parents=True, exist_ok=True)
    lips = WORK / "lips"
    lips.mkdir(exist_ok=True)

    judge_raw = flap(
        VO / "shushen-judge.mp3",
        STYLE / "c-phone-cu-closed.png",
        STYLE / "c-phone-cu-talk.png",
        CLIPS / "lip-judge.mp4",
    )
    a_talk = flap(
        VO / "shushen-a.mp3",
        STYLE / "c-talk-cu-closed.png",
        STYLE / "c-talk-cu-talk.png",
        CLIPS / "lip-a-talk.mp4",
    )
    a_reject = flap(
        VO / "shushen-a.mp3",
        STYLE / "c-02-reject-closed.png",
        STYLE / "c-02-reject-talk.png",
        CLIPS / "lip-a-reject.mp4",
    )
    d_wide = flap(
        VO / "father-d.mp3",
        STYLE / "c-04-talk-closed.png",
        STYLE / "c-04-talk-talk.png",
        CLIPS / "lip-d-wide.mp4",
    )
    d_cu = flap(
        VO / "father-d.mp3",
        STYLE / "c-father-cu-closed.png",
        STYLE / "c-father-cu-talk.png",
        CLIPS / "lip-d-cu.mp4",
    )
    b_wide = flap(
        VO / "shushen-b.mp3",
        STYLE / "c-05-defends-closed.png",
        STYLE / "c-05-defends-talk.png",
        CLIPS / "lip-b-wide.mp4",
    )
    b_cu = flap(
        VO / "shushen-b.mp3",
        STYLE / "c-defend-cu-closed.png",
        STYLE / "c-defend-cu-talk.png",
        CLIPS / "lip-b-cu.mp4",
    )
    e_raw = flap(
        VO / "father-e.mp3",
        STYLE / "c-06-vay-closed.png",
        STYLE / "c-06-vay-talk.png",
        CLIPS / "lip-e.mp4",
    )
    c_raw = flap(
        VO / "shushen-c.mp3",
        STYLE / "c-07-dont-closed.png",
        STYLE / "c-07-dont-talk.png",
        CLIPS / "lip-c.mp4",
    )

    d_judge = dur(judge_raw)
    d_a = dur(a_talk)
    d_d = dur(d_wide)
    d_b = dur(b_wide)
    d_e = dur(e_raw)
    d_c = dur(c_raw)

    a_cut = min(11.0, d_a * 0.52)
    d_cut = min(5.2, d_d * 0.48)
    b_cut = min(6.2, d_b * 0.48)

    pieces = [
        punch(judge_raw, WORK / "p00-judge.mp4", d_judge),
        punch(take_time(a_talk, lips / "a1.mp4", 0.0, a_cut), WORK / "p01-a1.mp4", a_cut),
        punch(take_time(a_reject, lips / "a2.mp4", a_cut, d_a - a_cut), WORK / "p02-a2.mp4", d_a - a_cut),
        kenburns(STYLE / "c-years-later.png", WORK / "p03-years.mp4", 2.4),
        norm_i2v(take_i2v("03", STYLE / "c-03-silent.png", 4.0), WORK / "p04-silent.mp4"),
        punch(take_time(d_wide, lips / "d1.mp4", 0.0, d_cut), WORK / "p05-d1.mp4", d_cut),
        punch(take_time(d_cu, lips / "d2.mp4", d_cut, d_d - d_cut), WORK / "p06-d2.mp4", d_d - d_cut),
        punch(take_time(b_wide, lips / "b1.mp4", 0.0, b_cut), WORK / "p07-b1.mp4", b_cut),
        punch(take_time(b_cu, lips / "b2.mp4", b_cut, d_b - b_cut), WORK / "p08-b2.mp4", d_b - b_cut),
        punch(e_raw, WORK / "p09-e.mp4", d_e),
        punch(c_raw, WORK / "p10-c.mp4", d_c),
        kenburns(STYLE / "c-08-endcard.png", WORK / "p11-end.mp4", 5.0),
    ]

    lst = WORK / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in pieces))
    silent = WORK / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])

    ds = [dur(p) for p in pieces]
    t_a = ds[0]
    t_d = t_a + ds[1] + ds[2] + ds[3] + ds[4]
    t_b = t_d + ds[5] + ds[6]
    t_e = t_b + ds[7] + ds[8]
    t_c = t_e + ds[9]
    print(
        f"offsets judge=0.000 a={t_a:.3f} d={t_d:.3f} b={t_b:.3f} e={t_e:.3f} c={t_c:.3f} "
        f"total={sum(ds):.3f}"
    )
    print("piece durs", [round(x, 3) for x in ds])

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
