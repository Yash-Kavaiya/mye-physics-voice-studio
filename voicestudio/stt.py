"""AssemblyAI pre-recorded STT (Universal) + word error rate."""
from __future__ import annotations
import re, time
from pathlib import Path
import requests

from . import config

_NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six",
        "7": "seven", "8": "eight", "9": "nine", "10": "ten", "12": "twelve", "100": "hundred"}


def _h():
    return {"authorization": config.api_key()}


def upload(path: str | Path) -> str:
    with open(path, "rb") as f:
        r = requests.post(f"{config.API}/v2/upload", headers=_h(), data=f, timeout=120)
    r.raise_for_status()
    return r.json()["upload_url"]


def transcribe(path: str | Path, keyterms: list[str] | None = None) -> dict:
    body = {"audio_url": upload(path), "speech_models": ["universal-3-5-pro", "universal-2"],
            "language_code": "en"}
    if keyterms:
        body["keyterms_prompt"] = keyterms[:100]
    r = requests.post(f"{config.API}/v2/transcript", headers=_h(), json=body, timeout=60)
    if r.status_code == 400 and keyterms:  # keyterms unsupported on fallback model: retry plain
        body.pop("keyterms_prompt"); r = requests.post(f"{config.API}/v2/transcript", headers=_h(), json=body, timeout=60)
    r.raise_for_status()
    tid = r.json()["id"]
    while True:
        j = requests.get(f"{config.API}/v2/transcript/{tid}", headers=_h(), timeout=60).json()
        if j["status"] == "completed":
            return j
        if j["status"] == "error":
            raise RuntimeError(f"STT error: {j.get('error')}")
        time.sleep(1.0)


def normalize(s: str) -> list[str]:
    s = s.lower().replace("-", " ").replace("’", "'")
    s = s.replace("π", " pi ").replace("²", " squared ").replace("³", " cubed ").replace("√", " root ")
    s = re.sub(r"(\d)([a-z])", r"\1 \2", s); s = re.sub(r"([a-z])(\d)", r"\1 \2", s)
    s = s.replace("%", " percent ").replace("=", " equals ").replace("+", " plus ")
    s = re.sub(r"\[|\]", " ", s)
    toks = re.findall(r"[a-z0-9']+", s)
    out = []
    for t in toks:
        out.append(_NUM.get(t, t))
    return [t.strip("'") for t in out if t.strip("'")]


def wer(ref: str, hyp: str) -> float:
    r, h = normalize(ref), normalize(hyp)
    if not r:
        return 0.0 if not h else 1.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev = cur
    return d[len(h)] / len(r)
