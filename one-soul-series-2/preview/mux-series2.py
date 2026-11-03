#!/usr/bin/env python3
"""Склейка серии 2: картинка, голос, тихая улица, провал на 12b–12c, плашка, srt."""

from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path("/workspace/one-soul-series-2")
PRE = ROOT / "preview"
CUTS = ROOT / "voice" / "renders" / "cuts"
OUT = PRE / "series2.mp4"
SRT = ROOT / "voice" / "series2.srt"
STREET = ROOT / "audio" / "street.wav"
ART = Path("/opt/cursor/artifacts/series2.mp4")
WORK = Path("/tmp/mux-series2")

# key, video, voice cut or None, trim seconds or None (voice+pad / full),
# street: open | under | fade | low | off, tail of the piece with street at 0,
# subtitle clauses split on the spoken bars
PIECES = [
    ("01", PRE / "silent/k01-street.mp4", None, 4.0, "open", 0.0, None),
    ("02", PRE / "silent/k02-couple.mp4", None, 3.0, "open", 0.0, None),
    ("03", PRE / "talk/k3-hello.mp4", CUTS / "morgol-k3.mp3", None, "under", 0.0,
     ["Ой, Ихил!", "Сынок, это ты?!"]),
    ("02b", PRE / "silent/k02b-look.mp4", None, 1.0, "open", 0.0, None),
    ("04a", PRE / "silent/k04a-sleeve.mp4", None, 1.0, "open", 0.0, None),
    ("04b", PRE / "talk/k4b-thirty.mp4", CUTS / "morgol-k4a.mp3", None, "under", 0.0,
     ["Ихил, сынок!", "Ляя, тебе уже под тридцать!"]),
    ("04c", PRE / "talk/k4c-why.mp4", CUTS / "morgol-k4b.mp3", None, "under", 0.0,
     ["Почему ты так долго выбираешь?"]),
    ("05a", PRE / "talk/k5a-years.mp4", CUTS / "morgol-k5a.mp3", None, "under", 0.0,
     ["Я твоей маме Шушэн", "пять лет подряд"]),
    ("05b", PRE / "talk/k5b-girls.mp4", CUTS / "morgol-k5b.mp3", None, "under", 0.0,
     ["лучшие варианты нашей общины отправляла!", "Столько хороших девушек было!"]),
    ("06", PRE / "talk/k6-shock.mp4", CUTS / "ikhil-k6.mp3", None, "under", 0.0,
     ["Подождите…", "Вы маме отправляли?!", "Все эти пять лет?!"]),
    ("07a", PRE / "talk/k7a-photos.mp4", CUTS / "ikhil-k7a.mp3", None, "under", 0.0,
     ["Но мама мне показала совсем мало фотографий!"]),
    ("07b", PRE / "talk/k7b-no-more.mp4", CUTS / "ikhil-k7b.mp3", None, "under", 0.0,
     ["Одни нам отказали,", "другие мне не понравились.", "Я думал, больше вариантов нет!"]),
    ("08", PRE / "talk/k8-show.mp4", CUTS / "morgol-k8.mp3", None, "under", 0.0,
     ["Эх, сынок…", "Сейчас я тебе кое-что покажу."]),
    ("09", PRE / "silent/k09-phone.mp4", None, 3.0, "open", 0.0, None),
    ("10a", PRE / "silent/k10a-interest.mp4", None, 1.0, "open", 0.0, None),
    ("10b", PRE / "cards/k10b-married.mp4", CUTS / "ikhil-k10.mp3", None, "under", 0.0,
     ["Ой, какая красивая!", "А почему я её не видел?"]),
    ("11a", PRE / "cards/k11a-two.mp4", CUTS / "ikhil-k11.mp3", None, "under", 0.0,
     ["А эта?!", "И эта хорошенькая!"]),
    ("11c", PRE / "silent/k11c-turn.mp4", None, 1.0, "open", 0.0, None),
    ("12a", PRE / "silent/k12a-lean.mp4", None, 1.0, "open", 0.0, None),
    ("12b", PRE / "cards/k12b-three.mp4", CUTS / "ikhil-k12.mp3", None, "under", 1.0,
     ["А вот эта мне вообще очень нравится!"]),
    ("12c", PRE / "silent/k12c-freeze.mp4", None, 1.0, "off", 0.0, None),
    ("13a", PRE / "silent/k13a-sigh.mp4", None, 1.0, "fade", 0.0, None),
    ("13b", PRE / "talk/k13b-married.mp4", CUTS / "ikhil-k13.mp3", None, "fade", 0.0,
     ["Тётя Моргол!", "Да что же это такое?!", "Все уже замужем?!"]),
    ("14g", PRE / "silent/k14a-hands-down.mp4", None, 2.0, "fade", 0.0, None),
    ("14a", PRE / "talk/k14a-years.mp4", CUTS / "ikhil-k14a.mp3", None, "fade", 0.0,
     ["Пять лет…", "Столько хороших девушек…"]),
    ("14b", PRE / "talk/k14b-why-mama.mp4", CUTS / "ikhil-k14b.mp3", None, "fade", 0.0,
     ["Почему мама их всех от меня скрыла?"]),
    ("15a", PRE / "silent/k15a-shake.mp4", None, 2.0, "fade", 0.0, None),
    ("15b", PRE / "silent/k15b-shoulder.mp4", None, 1.0, "fade", 0.0, None),
    ("15c", PRE / "silent/k15c-down.mp4", None, 1.0, "fade", 0.0, None),
    ("16", PRE / "k16-pull.mp4", CUTS / "vo-k16.mp3", None, "low", 0.0,
     ["Пять лет ожидания…", "Сколько возможностей было упущено", "из-за чужих предубеждений?"]),
    ("17", PRE / "k17-endcard.mp4", None, 3.2, "off", 0.0, None),
]

VF = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=24"
SR = 48000


def run(cmd: list[str]) -> None:
    subprocess.check_call(cmd)


def dur(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def speech_len(path: Path) -> float:
    pk = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "packet=duration_time", "-of", "csv=p=0", str(path)],
        text=True,
    )
    total = 0.0
    for line in pk.splitlines():
        for part in line.split(","):
            part = part.strip()
            if part:
                total += float(part)
    return total


def ts(t: float) -> str:
    if t < 0:
        t = 0.0
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def make_street() -> None:
    STREET.parent.mkdir(parents=True, exist_ok=True)
    raw = WORK / "street-raw.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-t", "30", "-i", "anoisesrc=color=brown:r=48000:a=0.45",
        "-f", "lavfi", "-t", "30", "-i", "anoisesrc=color=pink:r=48000:a=0.12",
        "-filter_complex",
        "[0:a]highpass=f=70,lowpass=f=320[a];"
        "[1:a]highpass=f=180,lowpass=f=1600,tremolo=f=0.18:d=0.35[b];"
        "[a][b]amix=inputs=2:duration=first:normalize=0,volume=0.8[a]",
        "-map", "[a]", "-c:a", "pcm_s16le", str(raw),
    ])
    # keep a copy in the repo as the 30s loop the plan names
    run(["ffmpeg", "-y", "-i", str(raw), "-c:a", "pcm_s16le", str(STREET)])


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    make_street()
    normed: list[Path] = []
    timeline: list[tuple[str, float, float, str, float, list[str] | None, float]] = []
    clock = 0.0
    for key, src, voice, trim, street, tail_off, lines in PIECES:
        if not src.exists():
            raise SystemExit(f"missing {src}")
        full = dur(src)
        spoken = speech_len(voice) if voice else 0.0
        # Cards keep the stamp hold. Talking clips lose only the silent tail.
        if key in {"10b", "11a", "12b"}:
            seconds = full
        elif trim is None:
            seconds = min(full, spoken + 0.18)
        else:
            seconds = min(full, float(trim))
        dest = WORK / f"n-{key}.mp4"
        cmd = ["ffmpeg", "-y", "-i", str(src), "-t", f"{seconds:.3f}", "-vf", VF]
        if voice is None and key != "10b" and key != "11a" and key != "12b":
            # silent picture, or the end card. Cards keep their own thud.
            if key == "17" or not _has_audio(src):
                cmd = [
                    "ffmpeg", "-y", "-i", str(src),
                    "-f", "lavfi", "-t", f"{seconds:.3f}", "-i", "anullsrc=r=48000:cl=mono",
                    "-t", f"{seconds:.3f}",
                    "-map", "0:v", "-map", "1:a",
                    "-vf", VF,
                ]
        cmd += [
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
            "-r", "24", "-fps_mode", "cfr",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "1",
            str(dest),
        ]
        run(cmd)
        got = dur(dest)
        normed.append(dest)
        timeline.append((key, clock, got, street, tail_off, lines, spoken))
        print(f"  {key:4} {got:6.3f}s  street={street:5}  at {clock:7.3f}")
        clock += got

    listing = WORK / "list.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in normed))
    picture = WORK / "picture.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(picture)])

    dialogue = WORK / "dialogue.wav"
    run(["ffmpeg", "-y", "-i", str(picture), "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(dialogue)])
    bed = _envelope(dialogue, timeline)
    mixed = WORK / "mixed.wav"
    _mix(dialogue, bed, mixed)

    run([
        "ffmpeg", "-y", "-i", str(picture), "-i", str(mixed),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "1",
        "-shortest", "-movflags", "+faststart",
        str(OUT),
    ])
    _write_srt(timeline)
    ART.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["cp", str(OUT), str(ART)])
    print("wrote", OUT, "dur", dur(OUT))


def _has_audio(path: Path) -> bool:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)],
        text=True,
    ).strip()
    return bool(out)


def _read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        if w.getframerate() != SR or w.getnchannels() != 1:
            raise SystemExit(f"unexpected wav {path}")
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def _envelope(dialogue: Path, timeline: list) -> np.ndarray:
    n = len(_read_wav(dialogue))
    env = np.zeros(n, dtype=np.float32)
    fade_bits = [(a, b) for _k, a, b, street, _t, _l, _s in timeline if street == "fade"]
    fade_start = fade_bits[0][0]
    fade_end = fade_bits[-1][0] + fade_bits[-1][1]
    loop = _read_wav(STREET)
    if len(loop) < 2:
        raise SystemExit("street loop is empty")
    tiled = np.resize(loop, n)
    level = {
        "open": 0.42,
        "under": 0.16,
        "low": 0.09,
        "fade": 0.0,
        "off": 0.0,
    }
    for _key, start, length, street, tail_off, _lines, _spoken in timeline:
        i0 = int(start * SR)
        i1 = min(n, int((start + length) * SR))
        if street == "fade":
            t = np.linspace(start, start + length, i1 - i0, endpoint=False)
            p = np.clip((t - fade_start) / max(fade_end - fade_start, 0.001), 0, 1)
            env[i0:i1] = (0.34 * (1 - p) + 0.05 * p).astype(np.float32)
        else:
            env[i0:i1] = level[street]
        if tail_off > 0:
            z0 = int((start + length - tail_off) * SR)
            env[max(i0, z0):i1] = 0.0
    # short bag rustle at the phone cut
    phone = next(item for item in timeline if item[0] == "09")
    rustle = np.random.default_rng(2).standard_normal(int(0.45 * SR)).astype(np.float32)
    # cheap one-pole high emphasis so it reads as cloth, not thunder
    acc = 0.0
    for i, s in enumerate(rustle):
        acc = acc * 0.82 + s * 0.18
        rustle[i] = s - acc
    ramp = np.linspace(0, 1, len(rustle), dtype=np.float32)
    rustle *= np.minimum(ramp * 6, 1) * np.minimum((1 - ramp) * 4, 1) * 0.08
    r0 = int((phone[1] + 0.12) * SR)
    r1 = min(n, r0 + len(rustle))
    bed = tiled * env
    bed[r0:r1] += rustle[: r1 - r0]
    peak = float(np.max(np.abs(bed))) or 1.0
    if peak > 0.9:
        bed *= 0.9 / peak
    return bed


def _mix(dialogue: Path, bed: np.ndarray, dest: Path) -> None:
    voice = _read_wav(dialogue)
    n = min(len(voice), len(bed))
    mixed = np.clip(voice[:n] + bed[:n], -1, 1)
    pcm = (mixed * 32767).astype(np.int16)
    with wave.open(str(dest), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def _write_srt(timeline: list) -> None:
    cues: list[str] = []
    n = 1
    for _key, start, length, _street, _tail, lines, spoken in timeline:
        if not lines:
            continue
        window = min(spoken, length) if spoken else length
        weights = [max(len(line), 1) for line in lines]
        total = sum(weights)
        cursor = start
        for line, weight in zip(lines, weights):
            span = window * weight / total
            end = cursor + span
            cues.append(f"{n}\n{ts(cursor)} --> {ts(end)}\n{line}\n")
            n += 1
            cursor = end
    SRT.write_text("\n".join(cues), encoding="utf-8")
    print("srt", SRT, "cues", n - 1)


if __name__ == "__main__":
    main()
