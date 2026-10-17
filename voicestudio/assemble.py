"""Render ManimGX sections, then ffmpeg: watermark -> concat -> loudnorm; merge word-timed SRTs."""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path

from . import config

GX = Path(__file__).parent / "gx"
FONT = "/usr/share/texmf/fonts/opentype/public/lm/lmroman10-regular.otf"
MANIMGX = shutil.which("manimgx") or str(Path(sys.executable).parent / "manimgx")


def dur(f) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]))


def render(scene_file: Path, scene: str, out: Path, env: dict | None = None, res="1920x1080", log=None) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return out
    tmp = scene_file.parent / f"raw_{scene}.mp4"
    cmd = [MANIMGX, "render", str(scene_file), scene, "-r", res, "--fps", "30", "--preset", "veryfast", "--crf", "20", "-o", str(tmp)]
    with open(log or os.devnull, "w") as lg:
        subprocess.run(cmd, check=True, stdout=lg, stderr=subprocess.STDOUT, env={**os.environ, **(env or {})}, cwd=scene_file.parent)
    shutil.move(tmp, out)
    srt = tmp.with_suffix(".srt")
    if srt.exists():
        shutil.move(srt, out.with_suffix(".srt"))
    return out


def watermark(src: Path, dst: Path, text: str = config.WATERMARK) -> Path:
    if dst.exists():
        return dst
    txt = text.replace(":", r"\:").replace("|", r"\|")
    vf = (f"fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#F6F7FB,"
          f"drawtext=fontfile={FONT}:text='{txt}':fontsize=30:fontcolor=#0E0B3D@0.55:x=w-tw-28:y=h-th-22,format=yuv420p")
    has_a = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(src)],
                           capture_output=True, text=True).stdout.strip()
    ain = [] if has_a else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(src), *ain, "-vf", vf, "-map", "0:v", "-map", "0:a" if has_a else "1:a",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", str(dst) + ".tmp.mp4"]
    subprocess.run(cmd, check=True)
    os.replace(str(dst) + ".tmp.mp4", dst)
    return dst


def _pt(x):
    h, mm, rest = x.split(":"); ss, ms = rest.split(","); return int(h) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000


def _ts(x):
    h = int(x // 3600); mm = int(x % 3600 // 60); ss = x % 60
    return f"{h:02d}:{mm:02d}:{int(ss):02d},{int(round((ss % 1) * 1000)) % 1000:03d}"


def concat(parts: list[Path], out: Path, captions: Path | None = None) -> float:
    work = out.parent / "_wm"; work.mkdir(exist_ok=True, parents=True)
    wm = [watermark(p, work / p.name) for p in parts]
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in wm))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
    if captions:
        t = 0.0; n = 1; blocks = []
        for p, w in zip(parts, wm):
            s = p.with_suffix(".srt")
            if s.exists():
                for blk in s.read_text().strip().split("\n\n"):
                    L = blk.split("\n")
                    if len(L) >= 3 and " --> " in L[1]:
                        a, b = L[1].split(" --> ")
                        blocks.append(f"{n}\n{_ts(_pt(a) + t)} --> {_ts(_pt(b) + t)}\n" + "\n".join(L[2:])); n += 1
            t += dur(w)
        captions.write_text("\n\n".join(blocks) + "\n")
    return dur(out)


def build_lesson(lesson: dict, outdir: Path, name="lesson") -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    lj = outdir / "lesson.json"; lj.write_text(json.dumps(lesson, indent=1))
    scenes = ["S00"] + [f"S{i:02d}" for i in range(1, len(lesson["sections"]) + 1)] + ["S99"]
    parts = []
    for sc in scenes:
        print(f"[render] {sc}", flush=True)
        parts.append(render(GX / "lesson_scenes.py", sc, outdir / "parts" / f"{sc}.mp4", env={"VS_LESSON": str(lj)},
                            log=outdir / f"render_{sc}.log"))
    final = outdir / f"{name}.mp4"
    d = concat(parts, final, outdir / f"{name}.srt")
    print(f"[done] {final} {d:.1f}s", flush=True)
    return {"video": str(final), "captions": str(outdir / f"{name}.srt"), "seconds": d}
