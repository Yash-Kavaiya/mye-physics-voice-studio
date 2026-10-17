"""AssemblyAI text-to-speech.

AssemblyAI exposes TTS through the Voice Agent API (docs: /voice-agents/voice-agent-api).
The documented `greeting` field "is sent straight to the TTS engine ... exactly what the user
hears, word for word", so an inline session whose greeting is our narration line is a
deterministic, documented TTS call. Output: 24 kHz mono PCM16 plus per-word timings from
`transcript.agent.delta` events.
"""
from __future__ import annotations
import asyncio, base64, hashlib, json, wave
from dataclasses import dataclass, field
from pathlib import Path

import websockets

from . import config

SR = 24000


@dataclass
class TTSResult:
    pcm: bytes
    text: str
    voice: str
    words: list = field(default_factory=list)  # [(word, start_s, end_s)] from the TTS engine

    @property
    def seconds(self) -> float:
        return len(self.pcm) / (2 * SR)

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(self.pcm)
        return path


async def _synth(text: str, voice: str) -> TTSResult:
    headers = {"Authorization": f"Bearer {config.api_key()}"}
    async with websockets.connect(config.AGENT_WS, additional_headers=headers, max_size=None,
                                  open_timeout=30) as ws:
        await ws.send(json.dumps({"type": "session.update", "session": {
            "system_prompt": "You are a narrator. Do not speak unless asked.",
            "greeting": text,
            "output": {"voice": voice, "format": {"encoding": "audio/pcm"}},
        }}))
        pcm, words = bytearray(), []
        async for raw in ws:
            ev = json.loads(raw)
            t = ev.get("type")
            if t == "reply.audio":
                pcm += base64.b64decode(ev["data"])
            elif t == "transcript.agent.delta" and ev.get("start_ms") is not None:
                words.append((ev["delta"], ev["start_ms"] / 1000, ev["end_ms"] / 1000))
            elif t == "reply.done":
                await ws.send(json.dumps({"type": "session.end"}))
            elif t == "session.ended":
                break
            elif t in ("session.error", "error"):
                raise RuntimeError(f"AssemblyAI TTS error: {ev.get('code')} {ev.get('message')}")
    if not pcm:
        raise RuntimeError("AssemblyAI TTS returned no audio")
    return TTSResult(bytes(pcm), text, voice, words)


def synthesize(text: str, voice: str | None = None, retries: int = 3) -> TTSResult:
    voice = voice or config.VOICE
    err = None
    for a in range(retries):
        try:
            return asyncio.run(_synth(text, voice))
        except Exception as e:  # network hiccups
            err = e
            import time; time.sleep(2 * (a + 1))
    raise RuntimeError(f"TTS failed after {retries} tries: {err}")


def cache_key(text: str, voice: str, attempt: int = 0) -> str:
    return hashlib.sha1(f"{voice}|{attempt}|{text}".encode()).hexdigest()[:16]
