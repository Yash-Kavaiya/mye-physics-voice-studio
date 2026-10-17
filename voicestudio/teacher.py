"""'Talk to your teacher': a student's spoken question -> spoken + animated answer.

Uses the AssemblyAI Voice Agent API end to end: the question audio is streamed in (real-time
STT with turn detection), the managed LLM writes a short answer, and AssemblyAI TTS speaks it.
The answer audio is then verified with pre-recorded Universal STT (WER) and rendered as a short
ManimGX clip with word-timed captions.
"""
from __future__ import annotations
import asyncio, base64, json, subprocess, time, wave
from pathlib import Path

import websockets

from . import config, stt
from .tts import SR

SYSTEM = ("You are Mye Physics, a warm physics teacher for B.Sc and M.Sc students. Answer the student's question "
          "in at most three short sentences, clearly and correctly. Speak math in words (say 'two pi i', never symbols). "
          "No lists, no markdown.")


def to_pcm24k(path: str | Path) -> bytes:
    return subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                          check=True, capture_output=True).stdout


async def _ask(pcm: bytes, voice: str, topic: str | None):
    headers = {"Authorization": f"Bearer {config.api_key()}"}
    session = {"system_prompt": SYSTEM + (f" The current lesson is about {topic}." if topic else ""),
               "input": {"format": {"encoding": "audio/pcm"}, "keyterms": ["residue", "Laurent", "contour", "pole", "analytic"]},
               "output": {"voice": voice, "format": {"encoding": "audio/pcm"}}}
    res = {"question": "", "answer": "", "pcm": bytearray(), "words": [], "latency_s": None}
    async with websockets.connect(config.AGENT_WS, additional_headers=headers, max_size=None, open_timeout=30) as ws:
        await ws.send(json.dumps({"type": "session.update", "session": session}))
        ready = asyncio.Event(); done = asyncio.Event(); t_end = {}

        async def send():
            await ready.wait()
            chunk = int(SR * 2 * 0.05)
            audio = pcm + b"\0" * (SR * 2 * 3)  # trailing silence lets turn detection close the turn
            for i in range(0, len(audio), chunk):
                if done.is_set():
                    return
                await ws.send(json.dumps({"type": "input.audio", "audio": base64.b64encode(audio[i:i + chunk]).decode()}))
                if i >= len(pcm) and "t" not in t_end:
                    t_end["t"] = time.time()
                await asyncio.sleep(0.05)
            while not done.is_set():  # keep the line open with silence until the reply finishes
                await ws.send(json.dumps({"type": "input.audio", "audio": base64.b64encode(b"\0" * chunk).decode()}))
                await asyncio.sleep(0.05)

        sender = asyncio.create_task(send())
        async for raw in ws:
            ev = json.loads(raw); t = ev.get("type")
            if t == "session.ready":
                ready.set()
            elif t == "transcript.user":
                res["question"] = ev.get("text", "")
            elif t == "reply.audio":
                if res["latency_s"] is None and "t" in t_end:
                    res["latency_s"] = round(time.time() - t_end["t"], 2)
                res["pcm"] += base64.b64decode(ev["data"])
            elif t == "transcript.agent.delta" and ev.get("start_ms") is not None:
                res["words"].append((ev["delta"], ev["start_ms"] / 1000, ev["end_ms"] / 1000))
            elif t == "transcript.agent":
                res["answer"] = ev.get("text", "")
            elif t == "reply.done":
                done.set(); await ws.send(json.dumps({"type": "session.end"}))
            elif t == "session.ended":
                break
            elif t in ("session.error", "error"):
                done.set(); raise RuntimeError(f"Voice Agent error: {ev}")
        sender.cancel()
    return res


def ask(question_audio: str | Path, outdir: str | Path, voice: str | None = None, topic: str | None = None) -> dict:
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    res = asyncio.run(_ask(to_pcm24k(question_audio), voice or config.VOICE, topic))
    wav = (outdir / "answer.wav").resolve()
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(res["pcm"]))
    tr = stt.transcribe(wav)
    from .voice import align
    rec = {"question": res["question"], "answer": res["answer"], "wav": str(wav), "latency_s": res["latency_s"],
           "wer": round(stt.wer(res["answer"], tr["text"] or ""), 4), "transcript": tr["text"],
           "words": align(res["answer"], tr.get("words", [])) or res["words"]}
    (outdir / "answer.json").write_text(json.dumps(rec, indent=1))
    return rec


def render_answer(outdir: str | Path) -> Path:
    from .assemble import GX, render
    outdir = Path(outdir)
    return render(GX / "answer_scene.py", "Answer", outdir / "answer_clip.mp4",
                  env={"VS_ANSWER": str((outdir / "answer.json").resolve())}, log=outdir / "render_answer.log")
