"""Hackathon demo segments (narrated by AssemblyAI TTS through the same self-verifying voice)."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
import manimgx as m
import numpy as np
from voicestudio.gx.theme import *
from voicestudio.voice import AssemblyAIVoice

LOG = [json.loads(l) for l in open(os.path.join(ROOT, "cache/verify_log.jsonl"))]
QA = json.load(open(os.path.join(ROOT, "out/qa/answer.json")))
MONO = "Latin Modern Mono"


def box(txt, c=BLUE, w=3.2, h=1.0, fs=24, sub=None):
    r = m.RoundedRectangle(width=w, height=h, corner_radius=0.16, stroke_color=c, stroke_width=3, fill_color=PANEL, fill_opacity=1)
    t = T(txt, fs, c, w=w - 0.3, bold=True)
    g = m.VGroup(t)
    if sub:
        g.add(T(sub, 17, MU, w=w - 0.3)); g.arrange(m.DOWN, buff=0.08)
    g.move_to(r)
    return m.VGroup(r, g)


def arrow(a, b, c=MU):
    return m.Arrow(a, b, buff=0.08, color=c, stroke_width=4, max_tip_length_to_length_ratio=0.15)


class D(Base):
    voice = staticmethod(AssemblyAIVoice)


class D1(D):
    def construct(s):
        a = grad(T("Mye Physics Voice Studio", 72, BLUE, bold=True)).move_to([0, 0.9, 0])
        b = T("Animated physics lessons, narrated and self-verified with AssemblyAI", 32, MU, w=12).next_to(a, m.DOWN, buff=0.35)
        tags = m.VGroup(*[card(T(x, 24, BLUE, bold=True), BLUE, 0.14, LAV) for x in ["Text-to-Speech", "Universal STT", "Voice Agent API", "ManimGX"]]).arrange(m.RIGHT, buff=0.3).next_to(b, m.DOWN, buff=0.6)
        s.say("Hi, I'm Yash. This is Mye Physics Voice Studio: it turns a physics script into a fully animated lesson, narrated with AssemblyAI text to speech, and it checks every single line it says.",
              m.AnimationGroup(m.Write(a), m.FadeIn(b), m.Succession(*[m.FadeIn(t, shift=m.UP * 0.2) for t in tags])))
        s.clear()
        hd = grad(T("The problem", 50, BLUE, bold=True)).to_corner(m.UL, buff=0.5)
        s.play(m.Write(hd), run_time=0.7)
        pts = [("Hours per lesson", "script, record, re-record, sync, caption"),
               ("Silent TTS mistakes", "a misread symbol ships to thousands of students"),
               ("Captions by hand", "word timing is tedious, so it gets skipped")]
        def pc(a_, b_):
            body = m.VGroup(*[T(l, 24, MU) for l in wrap(b_, 24)]).arrange(m.DOWN, buff=0.08)
            g = m.VGroup(T(a_, 32, CORAL, bold=True), body).arrange(m.DOWN, buff=0.22)
            r = m.RoundedRectangle(width=3.9, height=2.2, corner_radius=0.14, stroke_color=LN, stroke_width=2, fill_color=PANEL, fill_opacity=1)
            return m.VGroup(r, g.move_to(r))
        cards = m.VGroup(*[pc(a_, b_) for a_, b_ in pts]).arrange(m.RIGHT, buff=0.35).move_to([0, -0.2, 0])
        if cards.width > 12.8: cards.scale_to_fit_width(12.8)
        s.say("I run a physics channel for B.Sc and M.Sc students. One narrated lesson used to take me [hours]. Worse, text to speech can [silently misread] a line, and nobody notices until a student does. And [word timed captions] are so tedious they usually get skipped.",
              m.FadeIn(cards[0], shift=m.UP * 0.2), m.FadeIn(cards[1], shift=m.UP * 0.2), m.FadeIn(cards[2], shift=m.UP * 0.2))
        s.wait(0.4)


class D2(D):
    header = "Architecture"

    def construct(s):
        r1 = [("Topic / .md script", "input"), ("Structured narration", "sections, hooks, examples"), ("ManimGX animation", "equations written live")]
        r2 = [("AssemblyAI TTS", "Voice Agent API voice"), ("AssemblyAI STT", "Universal-3.5 Pro"), ("WER check", "regenerate if > 10%")]
        r3 = [("Word-timed captions", "from STT timestamps"), ("ffmpeg", "concat, loudnorm, watermark"), ("Lesson video", "1080p + .srt")]
        rows = []
        for y, row, c in [(1.6, r1, BLUE), (-0.2, r2, CORAL), (-2.0, r3, GREEN)]:
            g = m.VGroup(*[box(a, c, 3.4, 1.15, 24, b) for a, b in row]).arrange(m.RIGHT, buff=1.0).move_to([-0.3, y, 0])
            rows.append(g)
        ar = []
        for g in rows:
            ar.append([arrow(g[i].get_right(), g[i + 1].get_left()) for i in range(2)])
        down1 = arrow(rows[0][1].get_bottom(), rows[1][0].get_top())
        down2 = arrow(rows[1][2].get_bottom(), rows[2][0].get_top())
        wb = rows[1][2]
        loop = m.CurvedArrow(wb.get_corner(m.UR) + [0, -0.2, 0], wb.get_corner(m.DR) + [0, 0.2, 0], angle=-2.6, color=CORAL, stroke_width=4)
        lt = T("retry", 18, CORAL, bold=True).next_to(loop, m.RIGHT, buff=0.04)
        s.say("Here is the pipeline. A [topic or markdown script] becomes [structured narration] with sections, mini hooks and worked examples, and each beat becomes [ManimGX animation].",
              m.FadeIn(rows[0][0]), m.AnimationGroup(m.Create(ar[0][0]), m.FadeIn(rows[0][1])), m.AnimationGroup(m.Create(ar[0][1]), m.FadeIn(rows[0][2])))
        s.say("Every narration line is spoken by [AssemblyAI text to speech], then transcribed straight back by [AssemblyAI Universal speech to text]. We compute the [word error rate] against the script, and if it is above ten percent, the line is [regenerated] automatically.",
              m.AnimationGroup(m.Create(down1), m.FadeIn(rows[1][0])), m.AnimationGroup(m.Create(ar[1][0]), m.FadeIn(rows[1][1])), m.AnimationGroup(m.Create(ar[1][1]), m.FadeIn(rows[1][2])), m.AnimationGroup(m.Create(loop), m.FadeIn(lt)))
        s.say("The same transcript gives exact word timestamps, so animations land on the right word and we get [word timed captions] for free. Finally [ffmpeg] joins the sections, normalizes loudness and adds the watermark, giving a [finished lesson].",
              m.AnimationGroup(m.Create(down2), m.FadeIn(rows[2][0])), m.AnimationGroup(m.Create(ar[2][0]), m.FadeIn(rows[2][1])), m.AnimationGroup(m.Create(ar[2][1]), m.FadeIn(rows[2][2])))
        s.wait(0.5)


class D3(D):
    header = "Self-verifying narration"

    def construct(s):
        f = M(r"\mathrm{WER}=\frac{S+D+I}{N}\le 10\%", 54, FG).move_to([0, 1.7, 0])
        ref = T("script:  “... equals two pi i times the sum of the residues”", 26, FG, w=12.4)
        hyp = T("STT heard:  “... equals 2πi times the sum of the residues”", 26, BLUE, w=12.4)
        nm = T("normalised:  2πi  →  two pi i      WER = 0%", 26, GREEN, w=12.4, bold=True)
        g = m.VGroup(ref, hyp, nm).arrange(m.DOWN, buff=0.3, aligned_edge=m.LEFT).move_to([0, -0.2, 0])
        s.say("The check is simple. Word error rate is [substitutions, deletions and insertions over the number of script words]. The STT writes [two pi i as a symbol], so we [normalize math tokens] before comparing, and only real mistakes count.",
              m.Write(f), m.AnimationGroup(m.FadeIn(ref), m.FadeIn(hyp)), m.Write(nm))
        s.clear()
        n = len(LOG); u = len({r["text"] for r in LOG}); retakes = sum(r["attempt"] > 1 for r in LOG)
        best = {}
        for r in LOG:
            best[r["text"]] = min(best.get(r["text"], 9), r["wer"])
        flagged = sum(v > 0.10 for v in best.values()); mean = sum(best.values()) / len(best)
        stats = [(f"{u}", "lines narrated"), (f"{n}", "TTS takes scored"), (f"{mean:.1%}", "mean WER"), (f"{flagged}", "flagged for review")]
        cs = m.VGroup(*[card(m.VGroup(T(a, 52, BLUE, bold=True), T(b, 24, MU)).arrange(m.DOWN, buff=0.15), LN, 0.3) for a, b in stats]).arrange(m.RIGHT, buff=0.35).move_to([0, 0.5, 0])
        if cs.width > 12.6: cs.scale_to_fit_width(12.6)
        ex = card(m.VGroup(T("script:  “... a one over z minus a term”", 24, FG), T("STT heard:  “... a 1/ term”   WER 20%  ×3 takes", 24, CORAL)).arrange(m.DOWN, buff=0.12, aligned_edge=m.LEFT), CORAL, 0.2).next_to(cs, m.DOWN, buff=0.5)
        s.say(f"In this demo, Voice Studio narrated [{u} lines], and every take was transcribed and scored. And it caught something real: [one line kept losing the words z minus a], so after three takes it was flagged for a human to review instead of slipping through.",
              m.Succession(*[m.FadeIn(c, shift=m.UP * 0.2) for c in cs]), m.FadeIn(ex))
        s.wait(0.4)


class D4(D):
    header = "Live pipeline"

    def construct(s):
        lines = ["$ voicestudio lesson examples/residue_theorem.md -o out/residue",
                 "3 sections, 9 beats -> out/residue/lesson.json",
                 "[tts]  voice=michael  'Take a function that is analytic ...'",
                 "[stt]  universal-3-5-pro  WER 0.0%  take 1/3  ok",
                 "[render] S01 ... S03, S99",
                 "[ffmpeg] concat + loudnorm -16 LUFS + watermark",
                 "[done] residue_theorem.mp4  + word-timed residue_theorem.srt"]
        term = m.VGroup(*[m.Text(l, font=MONO, font_size=22, color=(GREEN if l.startswith("$") else FG)) for l in lines]).arrange(m.DOWN, buff=0.18, aligned_edge=m.LEFT)
        if term.width > 11.8: term.scale_to_fit_width(11.8)
        win = card(term, FG, 0.4, PANEL).move_to([0, -0.3, 0])
        dots = m.VGroup(*[m.Dot(radius=0.07, color=c) for c in [CORAL, GOLD, GREEN]]).arrange(m.RIGHT, buff=0.12).next_to(win[0].get_corner(m.UL), m.DR, buff=0.15)
        s.play(m.FadeIn(win[0]), m.FadeIn(dots), run_time=0.5)
        s.say("One command runs everything. The markdown script is parsed into beats, each line goes through text to speech and is verified, the sections render in ManimGX, and ffmpeg assembles the final video with captions. Here is the lesson it produced, untouched.",
              m.Succession(*[m.Write(l) for l in term]))
        s.wait(0.3)


class D5(D):
    header = "Talk to your teacher"

    def construct(s):
        steps = [("Student speaks", "mic or audio file"), ("Voice Agent API", "streaming STT + LLM"), ("AssemblyAI TTS", "spoken answer"), ("Animated clip", "verified + captioned")]
        g = m.VGroup(*[box(a, c, 2.7, 1.2, 24, b) for (a, b), c in zip(steps, [BLUE, CORAL, CORAL, GREEN])]).arrange(m.RIGHT, buff=0.55).move_to([0, 0.6, 0])
        ar = [arrow(g[i].get_right(), g[i + 1].get_left()) for i in range(3)]
        lat = T(f"first answer audio {QA['latency_s']} s after the question ends   ·   answer WER {QA['wer']:.1%}", 26, MU, w=12).move_to([0, -1.5, 0])
        s.say("Lessons raise doubts, so there is a second mode: talk to your teacher. A student [asks out loud]. The [Voice Agent API] transcribes the question in real time and writes a short answer, [AssemblyAI text to speech] speaks it, and Voice Studio turns it into an [animated, captioned clip]. Here a student asks about residues.",
              m.FadeIn(g[0]), m.AnimationGroup(m.Create(ar[0]), m.FadeIn(g[1])), m.AnimationGroup(m.Create(ar[1]), m.FadeIn(g[2])), m.AnimationGroup(m.Create(ar[2]), m.FadeIn(g[3]), m.FadeIn(lat)))
        s.wait(0.3)


class D6(D):
    header = "What's next"

    def construct(s):
        items = ["AssemblyAI TTS for every narration line",
                 "Universal STT verification with automatic retakes",
                 "Word-timed captions from STT timestamps",
                 "Voice Agent API for spoken Q&A",
                 "Open source: github.com/Yash-Kavaiya/mye-physics-voice-studio"]
        g = m.VGroup(*[T("•  " + x, 30, FG, w=12) for x in items]).arrange(m.DOWN, buff=0.28, aligned_edge=m.LEFT).move_to([0, 0.2, 0])
        g[-1].set_color(BLUE)
        s.say("To recap: AssemblyAI text to speech narrates, Universal speech to text verifies and times every word, and the Voice Agent API answers questions out loud. Everything is open source on GitHub. Thanks for watching, and happy learning from Mye Physics.",
              m.Succession(*[m.FadeIn(x, shift=m.RIGHT * 0.2) for x in g]))
        s.wait(1.2)


class Seg(Base):
    """Title card between demo parts."""
    label = ""; sub = ""

    def construct(s):
        a = grad(T(s.label, 60, BLUE, bold=True)).move_to([0, 0.3, 0]); b = T(s.sub, 30, MU, w=11).next_to(a, m.DOWN, buff=0.3)
        s.play(m.Write(a), m.FadeIn(b), run_time=1.2); s.wait(1.0); s.play(m.FadeOut(m.VGroup(a, b)), run_time=0.4)


class Seg1(Seg):
    label = "Generated mini-lesson"; sub = "The Residue Theorem, narrated by AssemblyAI TTS"


class Seg2(Seg):
    label = "Ask the teacher"; sub = "Spoken question in, animated answer out"


class Thumb(Base):
    def construct(s):
        a = grad(T("Voice Studio", 110, BLUE, bold=True)).move_to([0, 1.5, 0])
        b = T("Physics lessons that check their own voice", 44, FG, w=12).next_to(a, m.DOWN, buff=0.35)
        chain = m.VGroup(*[card(T(x, 34, c, bold=True), c, 0.2, PANEL, 3) for x, c in [("AssemblyAI TTS", CORAL), ("Universal STT", BLUE), ("WER ≤ 10%", GREEN)]]).arrange(m.RIGHT, buff=0.9)
        chain.next_to(b, m.DOWN, buff=0.7)
        ars = m.VGroup(*[m.Arrow(chain[i].get_right(), chain[i + 1].get_left(), buff=0.1, color=MU, stroke_width=5) for i in range(2)])
        eq = M(r"\oint_C f\,dz = 2\pi i\sum \mathrm{Res}", 56, FG).next_to(chain, m.DOWN, buff=0.6)
        wm = T("@myephysics | Yash Kavaiya", 28, MU).to_corner(m.DR, buff=0.3)
        s.add(a, b, chain, ars, eq, wm); s.wait(0.5)
