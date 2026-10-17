"""voicestudio CLI.

  voicestudio lesson examples/residue_theorem.md -o out/residue     # .md script -> narrated, verified lesson video
  voicestudio lesson --topic "Gauss's law" -o out/gauss               # topic -> script (LLM Gateway) -> video
  voicestudio say "Two pi i times the residue." -o line.wav            # one verified TTS line
  voicestudio ask question.wav -o out/qa --topic "residue theorem"    # Talk to your teacher
  voicestudio report                                                   # WER verification report
"""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path

from . import config


def main(argv=None):
    p = argparse.ArgumentParser(prog="voicestudio", description="Mye Physics Voice Studio (AssemblyAI TTS + STT + ManimGX)")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("lesson", help="build a narrated lesson video")
    a.add_argument("script", nargs="?", help=".md or .json lesson script")
    a.add_argument("--topic", help="generate the script from a topic via AssemblyAI LLM Gateway")
    a.add_argument("-o", "--out", default="out/lesson")
    a.add_argument("--name", default="lesson")
    a.add_argument("--plan-only", action="store_true", help="only write the structured narration JSON")
    b = sub.add_parser("say", help="synthesize + verify one line")
    b.add_argument("text"); b.add_argument("-o", "--out", default="line.wav"); b.add_argument("--voice")
    c = sub.add_parser("ask", help="Talk to your teacher: spoken question -> animated answer")
    c.add_argument("audio"); c.add_argument("-o", "--out", default="out/qa"); c.add_argument("--topic"); c.add_argument("--no-video", action="store_true")
    sub.add_parser("report", help="summarize WER verification log")
    sub.add_parser("ui", help="launch the Gradio web UI")
    args = p.parse_args(argv)

    if args.cmd == "lesson":
        from . import script, assemble
        out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
        if args.topic:
            md = script.from_topic(args.topic); (out / "script.md").write_text(md); lesson = script.parse_md(md)
        elif args.script:
            lesson = script.load(args.script)
        else:
            p.error("give a script file or --topic")
        (out / "lesson.json").write_text(json.dumps(lesson, indent=1))
        print(f"{len(lesson['sections'])} sections, {sum(len(s['beats']) for s in lesson['sections'])} beats -> {out/'lesson.json'}")
        if not args.plan_only:
            print(json.dumps(assemble.build_lesson(lesson, out, args.name), indent=1))
    elif args.cmd == "say":
        from . import voice
        r = voice.verified_line(args.text, args.voice)
        shutil.copy(r["wav"], args.out)
        print(f"WER {r['wer']:.1%} after {r['tries']} take(s) -> {args.out}\nSTT: {r['transcript']}")
    elif args.cmd == "ask":
        from . import teacher
        r = teacher.ask(args.audio, args.out, topic=args.topic)
        print(f"Q: {r['question']}\nA: {r['answer']}\nfirst-audio latency {r['latency_s']}s, answer WER {r['wer']:.1%}")
        if not args.no_video:
            print(teacher.render_answer(args.out))
    elif args.cmd == "report":
        rows = [json.loads(l) for l in open(config.CACHE / "verify_log.jsonl")]
        bad = [r for r in rows if r["wer"] > config.WER_THRESHOLD]
        best = {}
        for r in rows:
            best[r["text"]] = min(best.get(r["text"], 9), r["wer"])
        for t, w in best.items():
            if w > config.WER_THRESHOLD:
                print(f"FLAGGED ({w:.0%}): {t}")
        texts = {r["text"] for r in rows}
        print(f"takes: {len(rows)}  unique lines: {len(texts)}  takes over {config.WER_THRESHOLD:.0%} WER: {len(bad)}  "
              f"mean WER: {sum(r['wer'] for r in rows)/max(len(rows),1):.2%}  audio: {sum(r['seconds'] for r in rows)/60:.1f} min")
    elif args.cmd == "ui":
        from .app import launch
        launch()


if __name__ == "__main__":
    main()
