"""Assemble the hackathon demo: narrated demo parts + the real generated lesson + the real Q&A clip."""
import shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from voicestudio import assemble

D = Path(__file__).resolve().parent; O = D.parent / "out"
order = [D / "parts/D1.mp4", D / "parts/D2.mp4", D / "parts/D3.mp4", D / "parts/D4.mp4", D / "parts/Seg1.mp4",
         *sorted((O / "residue/parts").glob("S*.mp4")), D / "parts/Seg2.mp4", D / "parts/D5.mp4", O / "qa/answer_clip.mp4", D / "parts/D6.mp4"]
# raw (un-watermarked) parts; assemble.concat watermarks each once
work = D / "build"; work.mkdir(exist_ok=True)
parts = []
for p in order:
    q = work / f"{len(parts):02d}_{p.name}"
    if not q.exists():
        shutil.copy(p, q)
        if p.with_suffix(".srt").exists():
            shutil.copy(p.with_suffix(".srt"), q.with_suffix(".srt"))
    parts.append(q)
d = assemble.concat(parts, D / "demo.mp4", D / "demo.srt")
print(f"demo.mp4 {int(d//60)}:{int(d%60):02d}")
