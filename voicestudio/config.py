import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path(os.environ.get("VOICE_STUDIO_CACHE", ROOT / "cache"))
CACHE.mkdir(parents=True, exist_ok=True)

VOICE = os.environ.get("VOICE_STUDIO_VOICE", "michael")
LLM_MODEL = os.environ.get("VOICE_STUDIO_LLM_MODEL", "claude-sonnet-4-6")
WER_THRESHOLD = float(os.environ.get("VOICE_STUDIO_WER", "0.10"))
MAX_TRIES = int(os.environ.get("VOICE_STUDIO_MAX_TRIES", "3"))
WATERMARK = "@myephysics | Yash Kavaiya"

API = "https://api.assemblyai.com"
AGENT_WS = "wss://agents.assemblyai.com/v1/ws"
LLM_GATEWAY = "https://llm-gateway.assemblyai.com/v1/chat/completions"


def api_key() -> str:
    k = os.environ.get("ASSEMBLYAI_API_KEY")
    if not k:
        raise RuntimeError("ASSEMBLYAI_API_KEY is not set (copy .env.example to .env)")
    return k
