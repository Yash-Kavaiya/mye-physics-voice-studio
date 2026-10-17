"""Gradio UI: build a lesson from a script, or ask the teacher out loud (mic or file)."""
from __future__ import annotations
import json, tempfile, time
from pathlib import Path


def launch(share=False):
    import gradio as gr
    from . import assemble, script, teacher, voice

    def do_line(text):
        r = voice.verified_line(text)
        return r["wav"], f"WER {r['wer']:.1%} after {r['tries']} take(s)\nSTT heard: {r['transcript']}"

    def do_lesson(md):
        lesson = script.parse_md(md)
        out = Path(tempfile.mkdtemp(prefix="lesson_", dir="out"))
        res = assemble.build_lesson(lesson, out, "lesson")
        return res["video"], res["captions"]

    def do_ask(audio, topic):
        out = Path("out") / f"qa_{int(time.time())}"
        r = teacher.ask(audio, out, topic=topic or None)
        clip = teacher.render_answer(out)
        return str(clip), f"Q: {r['question']}\n\nA: {r['answer']}\n\nlatency {r['latency_s']}s · WER {r['wer']:.1%}"

    with gr.Blocks(title="Mye Physics Voice Studio") as ui:
        gr.Markdown("# Mye Physics Voice Studio\nAssemblyAI TTS narrates, AssemblyAI STT verifies, ManimGX animates.")
        with gr.Tab("Talk to your teacher"):
            a = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Ask your question")
            tp = gr.Textbox(label="Lesson topic (optional)", value="the residue theorem")
            v = gr.Video(label="Animated answer"); t = gr.Textbox(label="Transcript")
            gr.Button("Ask").click(do_ask, [a, tp], [v, t])
        with gr.Tab("Verified line"):
            x = gr.Textbox(label="Narration line"); o = gr.Audio(); r = gr.Textbox(label="Verification")
            gr.Button("Speak + verify").click(do_line, x, [o, r])
        with gr.Tab("Build lesson"):
            md = gr.Code(language="markdown", value=Path(__file__).parent.parent.joinpath("examples/residue_theorem.md").read_text())
            vid = gr.Video(); cap = gr.File(label="Word-timed captions (.srt)")
            gr.Button("Build").click(do_lesson, md, [vid, cap])
    ui.launch(share=share)
