#!/usr/bin/env python3
"""Cartoon lip-flap from two or three stills driven by VO RMS."""

from __future__ import annotations

import math
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path


def _wav_mono_s16(src: Path, work: Path) -> tuple[bytes, int]:
    wav = work / "vo.wav"
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-ac",
            "1",
            "-ar",
            "24000",
            "-c:a",
            "pcm_s16le",
            str(wav),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    raw = wav.read_bytes()
    # skip header: find 'data' chunk
    idx = raw.find(b"data")
    if idx < 0:
        raise RuntimeError("no data chunk")
    payload = raw[idx + 8 :]
    return payload, 24000


def _rms_windows(pcm: bytes, sr: int, fps: int) -> list[float]:
    samples = struct.unpack("<" + "h" * (len(pcm) // 2), pcm[: len(pcm) // 2 * 2])
    hop = sr / fps
    out: list[float] = []
    i = 0.0
    while int(i) < len(samples):
        a = int(i)
        b = min(len(samples), int(i + hop))
        chunk = samples[a:b]
        if not chunk:
            break
        acc = sum(x * x for x in chunk) / len(chunk)
        out.append(math.sqrt(acc) / 32768.0)
        i += hop
    return out


def _choose(rms: list[float]) -> list[int]:
    """0=closed, 1=mid, 2=open. Percentile thresholds + 2-frame hold."""
    ranked = sorted(rms)
    if not ranked:
        return []
    lo = ranked[int(len(ranked) * 0.22)]
    hi = ranked[int(len(ranked) * 0.62)]
    picks: list[int] = []
    last = 0
    hold = 0
    for v in rms:
        if v < max(lo, 0.012):
            want = 0
        elif v < hi:
            want = 1
        else:
            want = 2
        if want != last and hold < 2:
            want = last
        if want != last:
            last = want
            hold = 1
        else:
            hold += 1
        picks.append(want)
    return picks


def render(
    audio: Path,
    closed: Path,
    mid: Path,
    opened: Path,
    dest: Path,
    fps: int = 24,
    min_seconds: float = 0.0,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lipsync-") as td:
        work = Path(td)
        pcm, sr = _wav_mono_s16(audio, work)
        rms = _rms_windows(pcm, sr, fps)
        need = max(len(rms), int(math.ceil(min_seconds * fps)))
        while len(rms) < need:
            rms.append(0.0)
        picks = _choose(rms)

        sized = []
        for name, src in [("c", closed), ("m", mid), ("o", opened)]:
            out = work / f"{name}.png"
            subprocess.check_call(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(src),
                    "-vf",
                    "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1",
                    str(out),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            sized.append(out)

        frames = work / "frames"
        frames.mkdir()
        for i, pick in enumerate(picks):
            src = sized[min(pick, 2)]
            dst = frames / f"{i:05d}.png"
            try:
                dst.hardlink_to(src)
            except OSError:
                shutil.copy2(src, dst)

        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(fps),
                "-i",
                str(frames / "%05d.png"),
                "-vf",
                "scale=720:1280,setsar=1",
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


if __name__ == "__main__":
    import sys

    render(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
