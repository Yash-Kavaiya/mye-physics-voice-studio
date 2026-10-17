"""Lesson script format (.md) -> structured narration (JSON).

    # Title
    > One-line subtitle
    ## Section title
    ? Big hook text | Spoken mini-hook line.
    Each narration line is one spoken beat.
    $$ \\oint_C f(z)\\,dz = 2\\pi i \\sum \\operatorname{Res} $$   <- written while the line above is spoken
    - bullet                                                     <- revealed while the line above is spoken
    ### Example: Title                                           <- worked-example card for following beats
"""
from __future__ import annotations
import json, re
from pathlib import Path
import requests

from . import config


def parse_md(text: str) -> dict:
    L = {"title": "", "subtitle": "", "sections": []}
    sec = None; beat = None; example = None; para: list[str] = []

    def flush():
        nonlocal beat, para
        if para and sec is not None:
            beat = {"say": " ".join(para).strip(), "math": [], "bullets": [], "example": example}
            sec["beats"].append(beat)
        para = []

    lines = text.splitlines(); i = 0
    while i < len(lines):
        raw = lines[i]; s = raw.strip(); i += 1
        if s.startswith("$$"):
            flush()
            eq = s[2:]
            while not eq.rstrip().endswith("$$") and i < len(lines):
                eq += " " + lines[i].strip(); i += 1
            eq = eq.rstrip()[:-2].strip()
            if beat is not None:
                beat["math"].append(eq)
            continue
        if s.startswith("# "):
            flush(); L["title"] = s[2:].strip(); continue
        if s.startswith(">") and not L["sections"]:
            flush(); L["subtitle"] = s[1:].strip(); continue
        if s.startswith("## "):
            flush(); example = None; beat = None
            sec = {"title": s[3:].strip(), "hook": None, "beats": []}; L["sections"].append(sec); continue
        if s.startswith("### "):
            flush(); example = re.sub(r"^example\s*:\s*", "", s[4:].strip(), flags=re.I) or "Worked example"; continue
        if s.startswith("? ") and sec is not None:
            flush(); big, _, line = s[2:].partition("|")
            sec["hook"] = {"text": big.strip(), "say": (line or big).strip()}; continue
        if re.match(r"^[-*] ", s):
            flush()
            if beat is not None:
                beat["bullets"].append(s[2:].strip())
            continue
        if not s:
            flush(); continue
        para.append(s); flush()  # one narration line = one beat
    flush()
    return L


def load(path: str | Path) -> dict:
    p = Path(path)
    if p.suffix == ".json":
        return json.loads(p.read_text())
    return parse_md(p.read_text())


PROMPT = """You write narration scripts for animated physics lessons for B.Sc/M.Sc students.
Write a lesson on: {topic}
Output ONLY markdown in this exact format:
# Title
> one-line subtitle
## Section title   (4-6 sections; include at least two '### Example: ...' worked examples and one exam-style problem)
? Big hook text (max 6 words) | One spoken mini-hook sentence.
Spoken narration paragraphs, 1-3 sentences each, plain words (say 'two pi i', never symbols).
$$ LaTeX equation shown while the paragraph above is spoken $$
- short bullet (optional)
"""


def from_topic(topic: str, model: str | None = None) -> str:
    """Generate a .md script with AssemblyAI LLM Gateway (needs LLM Gateway access on the account)."""
    r = requests.post(config.LLM_GATEWAY, headers={"authorization": config.api_key()}, timeout=180,
                      json={"model": model or config.LLM_MODEL, "max_tokens": 4000,
                            "messages": [{"role": "user", "content": PROMPT.format(topic=topic)}]})
    j = r.json()
    if r.status_code != 200:
        raise RuntimeError(f"LLM Gateway error {r.status_code}: {j.get('metadata', j)}. "
                           "Write a .md script instead (see examples/).")
    return j["choices"][0]["message"]["content"]
