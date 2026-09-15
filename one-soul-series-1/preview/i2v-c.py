#!/usr/bin/env python3
"""Submit and poll Kling I2V jobs for Variant C."""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path("/workspace/one-soul-series-1")
STYLE = ROOT / "style"
OUT = Path("/tmp/i2v-c2")
JOBS_PATH = Path("/tmp/i2v-c2-jobs.json")
API = "https://openrouter.ai/api/v1/videos"
MODEL = "kwaivgi/kling-v3.0-std"


def data_uri(path: Path) -> str:
    raw = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


MOVE = (
    "Photoreal cinematic 3D sitcom. BIG motion: camera pushes or orbits, "
    "the actor turns, gestures, leans. Lips talk. Fabric and hair move. "
    "Not a still photo. Keep the same faces and clothes."
)

JOBS = [
    {
        "id": "01w",
        "duration": 4,
        "first": STYLE / "c-opener-judge.png",
        "last": STYLE / "c-phone-cu.png",
        "prompt": MOVE + " Camera rushes from the sofa wide into the phone. She frowns and shakes her head. No joyful wave.",
    },
    {
        "id": "01c",
        "duration": 4,
        "first": STYLE / "c-phone-cu.png",
        "last": STYLE / "c-01-end.png",
        "prompt": MOVE + " Close on the phone. Thumb flicks the photo. She scowls. Pull back a little to the sofa.",
    },
    {
        "id": "02t",
        "duration": 6,
        "first": STYLE / "c-02-phone.png",
        "last": STYLE / "c-talk-cu.png",
        "prompt": MOVE + " She talks on the phone with energy, free hand chopping the air, camera pushes into a close-up.",
    },
    {
        "id": "02s",
        "duration": 4,
        "first": STYLE / "c-son-look.png",
        "last": STYLE / "c-son-look.png",
        "prompt": MOVE + " The shy son sips tea, glances sideways, tiny embarrassed smile. Camera slowly circles.",
    },
    {
        "id": "02r",
        "duration": 5,
        "first": STYLE / "c-02-reject.png",
        "last": STYLE / "c-phone-cu.png",
        "prompt": MOVE + " She rejects the photo, shakes her head, camera snaps closer to the screen.",
    },
    {
        "id": "02p",
        "duration": 6,
        "first": STYLE / "c-02-reject.png",
        "last": STYLE / "c-02-proud.png",
        "prompt": MOVE + " From disgust to pride: she turns to her son, hand to her heart, warm push-in.",
    },
    {
        "id": "03",
        "duration": 4,
        "first": STYLE / "c-03-silent.png",
        "last": STYLE / "c-03-silent.png",
        "prompt": "Photoreal 3D. Tense silent family. Slow dramatic push-in. Father mouth CLOSED, hands on the chair. Breathing only.",
    },
    {
        "id": "04m",
        "duration": 5,
        "first": STYLE / "c-father-scolds.png",
        "last": STYLE / "c-04-talk.png",
        "prompt": MOVE + " Father talks, leans forward, hand chops the air. Normal five fingers, no melted hand, no table slam.",
    },
    {
        "id": "04c",
        "duration": 6,
        "first": STYLE / "c-04-talk.png",
        "last": STYLE / "c-father-cu.png",
        "prompt": MOVE + " Camera slams into his face as he points and speaks. Mouth talks, not a frozen scream. Hand stays a real hand.",
    },
    {
        "id": "05w",
        "duration": 6,
        "first": STYLE / "c-05-defends.png",
        "last": STYLE / "c-defend-cu.png",
        "prompt": MOVE + " She argues, steps in, camera orbits to a close-up. Phone stays in one hand.",
    },
    {
        "id": "05c",
        "duration": 7,
        "first": STYLE / "c-defend-cu.png",
        "last": STYLE / "c-talk-cu.png",
        "prompt": MOVE + " Close-up argument. She gestures hard, lips talking, slight camera shake energy. Same woman.",
    },
    {
        "id": "06",
        "duration": 6,
        "first": STYLE / "c-06-vay.png",
        "last": STYLE / "c-06-vay.png",
        "prompt": MOVE + " Father throws both hands up, leans back, talks. Hands stay normal. Camera push then slight pull.",
    },
    {
        "id": "07",
        "duration": 5,
        "first": STYLE / "c-07-dont.png",
        "last": STYLE / "c-07-dont.png",
        "prompt": MOVE + " She jabs a finger at him and finishes the line. He flinches then freezes. Punchy, not a still.",
    },
]


def req(method: str, url: str, payload: dict | None = None) -> dict:
    key = os.environ["OPENROUTER_API_KEY"]
    data = None if payload is None else json.dumps(payload).encode()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/SwaTik91/Synagogue-multic",
        "X-Title": "One Soul Variant C",
    }
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.loads(resp.read().decode())


def submit(job: dict) -> dict:
    frames = [
        {
            "type": "image_url",
            "image_url": {"url": data_uri(job["first"])},
            "frame_type": "first_frame",
        }
    ]
    if job.get("last") and job["last"] != job["first"]:
        frames.append(
            {
                "type": "image_url",
                "image_url": {"url": data_uri(job["last"])},
                "frame_type": "last_frame",
            }
        )
    body = {
        "model": MODEL,
        "prompt": job["prompt"],
        "duration": job["duration"],
        "aspect_ratio": "9:16",
        "resolution": "720p",
        "generate_audio": False,
        "frame_images": frames,
    }
    print("submit", job["id"], flush=True)
    return req("POST", API, body)


def poll_one(entry: dict) -> dict:
    url = entry.get("polling_url") or f"{API}/{entry['id']}"
    return req("GET", url)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    print("saved", dest, dest.stat().st_size, flush=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    state: dict[str, dict] = {}
    if JOBS_PATH.exists():
        state = json.loads(JOBS_PATH.read_text())

    for job in JOBS:
        jid = job["id"]
        if jid in state and state[jid].get("status") == "completed" and Path(state[jid].get("local", "")).exists():
            print("skip", jid)
            continue
        if jid in state and state[jid].get("id") and state[jid].get("status") not in {"failed", "cancelled", "expired"}:
            continue
        try:
            res = submit(job)
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            print("HTTP", e.code, jid, err[:800])
            state[jid] = {"status": "failed", "error": err}
            JOBS_PATH.write_text(json.dumps(state, indent=2))
            continue
        state[jid] = {
            "id": res.get("id") or res.get("generation_id"),
            "polling_url": res.get("polling_url") or (f"{API}/{res.get('id')}" if res.get("id") else None),
            "status": res.get("status", "pending"),
            "raw": {k: res.get(k) for k in ("id", "status", "polling_url", "error")},
        }
        JOBS_PATH.write_text(json.dumps(state, indent=2))
        print(jid, state[jid]["status"], state[jid]["id"])

    # poll
    pending = True
    while pending:
        pending = False
        for job in JOBS:
            jid = job["id"]
            entry = state.get(jid, {})
            if entry.get("status") == "completed" and Path(entry.get("local", "")).exists():
                continue
            if not entry.get("polling_url") and not entry.get("id"):
                continue
            if entry.get("status") in {"failed", "cancelled", "expired"}:
                continue
            try:
                info = poll_one(entry)
            except Exception as e:
                print("poll err", jid, e)
                pending = True
                continue
            status = info.get("status")
            entry["status"] = status
            entry["id"] = entry.get("id") or info.get("id")
            print("poll", jid, status, flush=True)
            if status == "completed":
                url = None
                for key in ("unsigned_urls", "videos", "output"):
                    val = info.get(key)
                    if isinstance(val, list) and val:
                        item = val[0]
                        url = item if isinstance(item, str) else item.get("url") or item.get("unsigned_url")
                        break
                if not url:
                    url = (info.get("content") or {}).get("url")
                if not url and entry.get("id"):
                    url = f"{API}/{entry['id']}/content?index=0"
                dest = OUT / f"{jid}.mp4"
                if url:
                    try:
                        download(url, dest)
                    except Exception:
                        # content endpoint often needs auth header
                        key = os.environ["OPENROUTER_API_KEY"]
                        r = urllib.request.Request(
                            url,
                            headers={"Authorization": f"Bearer {key}"},
                        )
                        with urllib.request.urlopen(r, timeout=180) as resp:
                            dest.write_bytes(resp.read())
                        print("saved-auth", dest, dest.stat().st_size)
                entry["local"] = str(dest)
            elif status in {"failed", "cancelled", "expired"}:
                entry["error"] = info.get("error") or info
                print("FAIL", jid, entry["error"])
            else:
                pending = True
            state[jid] = entry
        JOBS_PATH.write_text(json.dumps(state, indent=2))
        if pending:
            time.sleep(12)

    print("done", json.dumps({k: v.get("status") for k, v in state.items()}, indent=2))


if __name__ == "__main__":
    main()
