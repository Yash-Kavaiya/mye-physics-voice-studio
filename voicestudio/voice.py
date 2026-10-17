"""Self-verifying AssemblyAI narrator.

For each narration line:  TTS (Voice Agent API)  ->  STT (Universal)  ->  WER vs. script.
Lines with WER above the threshold are re-synthesised (up to MAX_TRIES); the best take wins.
STT word timestamps are aligned back onto the script's own words, giving exact word timing
for ManimGX animation cues and word-timed SRT captions.
"""
from __future__ import annotations
import difflib, fcntl, io, json, re, time, wave
from pathlib import Path

from . import config, stt, tts

LOG = config.CACHE / "verify_log.jsonl"
SUB = [("—", ", "), ("–", " "), ("’", "'"), ("…", "...")]


def clean(text: str) -> str:
    for a, b in SUB:
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text.replace("[", "").replace("]", "")).strip()


def align(script: str, stt_words: list[dict]) -> list[tuple[str, float, float]]:
    """Map STT word timings (ms) onto the script's whitespace tokens."""
    toks = script.split()
    if not stt_words:
        return []
    key = lambda w: " ".join(stt.normalize(w))
    a = [key(t) for t in toks]
    b = [key(w["text"]) for w in stt_words]
    times: list[tuple[float, float] | None] = [None] * len(toks)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            w = stt_words[blk.b + k]
            times[blk.a + k] = (w["start"] / 1000, w["end"] / 1000)
    # interpolate gaps
    t0, t1 = stt_words[0]["start"] / 1000, stt_words[-1]["end"] / 1000
    i = 0
    while i < len(toks):
        if times[i] is None:
            j = i
            while j < len(toks) and times[j] is None:
                j += 1
            lo = times[i - 1][1] if i > 0 else t0
            hi = times[j][0] if j < len(toks) else t1
            step = max(hi - lo, 0.01) / (j - i)
            for k in range(i, j):
                times[k] = (lo + step * (k - i), lo + step * (k - i + 1))
            i = j
        else:
            i += 1
    return [(t, s, e) for t, (s, e) in zip(toks, times)]


def verified_line(text: str, voice: str | None = None, keyterms: list[str] | None = None) -> dict:
    """Return {'wav': path, 'words': [(w,s,e)], 'wer': float, 'tries': n, 'transcript': str}."""
    voice = voice or config.VOICE
    text = clean(text)
    key = tts.cache_key(text, voice)
    meta_p = config.CACHE / f"{key}.json"
    if meta_p.exists():
        return json.loads(meta_p.read_text())
    best = None
    for attempt in range(config.MAX_TRIES):
        r = tts.synthesize(text, voice)
        wav = config.CACHE / f"{key}_{attempt}.wav"
        r.save(wav)
        tr = stt.transcribe(wav, keyterms)
        score = stt.wer(text, tr["text"] or "")
        rec = {"text": text, "voice": voice, "attempt": attempt + 1, "wer": round(score, 4),
               "transcript": tr["text"], "seconds": round(r.seconds, 2), "wav": str(wav),
               "stt_model": tr.get("speech_model_used"), "words_stt": tr.get("words", [])}
        with open(LOG, "a") as f:
            f.write(json.dumps({k: v for k, v in rec.items() if k != "words_stt"} | {"t": time.time()}) + "\n")
        if best is None or score < best["wer"]:
            best = rec
        if score <= config.WER_THRESHOLD:
            break
    best["tries"] = best["attempt"]
    best["flagged"] = best["wer"] > config.WER_THRESHOLD  # still failing after MAX_TRIES: needs human review
    best["words"] = align(text, best.pop("words_stt"))
    meta_p.write_text(json.dumps(best, indent=1))
    return best


def AssemblyAIVoice(text: str):
    """ManimGX voice: `voice = staticmethod(AssemblyAIVoice)` on a scene class."""
    import manimgx as m
    from manimgx.audio.sound import Word
    with open("/tmp/voicestudio.lock", "w") as lk:  # serialize API usage across render workers
        fcntl.flock(lk, fcntl.LOCK_EX)
        rec = verified_line(text)
    with wave.open(rec["wav"]) as w:
        fr = w.readframes(w.getnframes()); sr = w.getframerate()
    fr += b"\0" * int(sr * 2 * 0.25)
    b = io.BytesIO()
    with wave.open(b, "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(fr)
    words = [Word(t, s, e) for t, s, e in rec["words"]]
    return m.Speech(b.getvalue(), text=clean(text), words=words)
