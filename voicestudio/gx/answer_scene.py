"""Short animated answer clip for 'Talk to your teacher' (env VS_ANSWER -> answer.json)."""
import io, json, os, sys, wave
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import manimgx as m
from manimgx.audio.sound import Word
from voicestudio.gx.theme import *
from voicestudio.voice import AssemblyAIVoice, clean

A = json.load(open(os.environ["VS_ANSWER"]))


def answer_voice(text):
    if clean(text) != clean(A["answer"]):
        return AssemblyAIVoice(text)
    with wave.open(A["wav"]) as w:
        fr = w.readframes(w.getnframes()); sr = w.getframerate()
    b = io.BytesIO()
    with wave.open(b, "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(fr + b"\0" * int(sr * 0.5))
    return m.Speech(b.getvalue(), text=clean(text), words=[Word(*x) for x in A["words"]])


class Answer(Base):
    header = "Talk to your teacher"
    voice = staticmethod(answer_voice)

    def construct(s):
        tag = card(T("Student asked", 26, PANEL, bold=True), BLUE, 0.14, BLUE).move_to([-4.6, 2.0, 0])
        q = m.VGroup(*[T(l, 34, FG, bold=True) for l in wrap(A["question"], 50)]).arrange(m.DOWN, buff=0.12, aligned_edge=m.LEFT)
        q.next_to(tag, m.DOWN, buff=0.3).align_to(tag, m.LEFT)
        if q.width > 12: q.scale_to_fit_width(12)
        s.play(m.FadeIn(tag), m.Write(q), run_time=1.5)
        s.wait(0.4)
        tag2 = card(T("Teacher", 26, PANEL, bold=True), CORAL, 0.14, CORAL).next_to(q, m.DOWN, buff=0.45).align_to(tag, m.LEFT)
        lines = wrap(A["answer"], 64)
        ans = m.VGroup(*[T(l, 30, FG) for l in lines]).arrange(m.DOWN, buff=0.14, aligned_edge=m.LEFT)
        avail = tag2.get_bottom()[1] - 0.3 - (-3.3)
        if ans.height > avail: ans.scale_to_fit_height(avail)
        if ans.width > 12.4: ans.scale_to_fit_width(12.4)
        ans.next_to(tag2, m.DOWN, buff=0.3).align_to(tag, m.LEFT)
        s.play(m.FadeIn(tag2), run_time=0.4)
        s.say(A["answer"], m.Succession(*[m.Write(l) for l in ans]))
        s.wait(0.8)
