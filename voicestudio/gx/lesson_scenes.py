"""ManimGX scenes generated from a lesson JSON (env VS_LESSON). Render one class per section:
S00 = opening (about / why / agenda), S01..Sn = sections, S99 = recap & outro."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import manimgx as m
from voicestudio.gx.theme import *
from voicestudio.voice import AssemblyAIVoice

L = json.load(open(os.environ.get("VS_LESSON", os.path.join(os.path.dirname(__file__), "lesson.json"))))
SECS = L["sections"]


class Lesson(Base):
    voice = staticmethod(AssemblyAIVoice)

    def beat(s, b):
        items = []
        if b.get("example") and not getattr(s, "_ex", None) == b["example"]:
            s._ex = b["example"]
            if s.stack:
                s.play(*[m.FadeOut(x) for x in s.stack], run_time=0.4); s.stack = []
            items.append(card(T("Example: " + b["example"], 30, BLUE, w=11, bold=True), BLUE, 0.18, LAV))
        for e in b.get("math", []):
            items.append(M(e, 46, FG, w=12))
        for bl in b.get("bullets", []):
            items.append(T("•  " + bl, 30, FG, w=12))
        if not items:  # pure narration: show a short caption-card of the key sentence
            first = b["say"].replace("[", "").replace("]", "").split(". ")[0]
            items.append(m.VGroup(*[T(l, 32, FG) for l in wrap(first, 52)[:3]]).arrange(m.DOWN, buff=0.12))
        s.say(b["say"].replace("[", "").replace("]", ""), s.col(items))


class S00(Lesson):
    def construct(s):
        a = grad(T(L["title"], 64, BLUE, w=12, bold=True)).move_to([0, 0.7, 0])
        b = T(L.get("subtitle", ""), 32, MU, w=11).next_to(a, m.DOWN, buff=0.4)
        s.say(f"This lesson is about {L['title']}. {L.get('subtitle','')}", m.AnimationGroup(m.Write(a), m.FadeIn(b)))
        s.clear()
        hd = grad(T("Agenda", 46, BLUE, bold=True).to_corner(m.UL, buff=0.45))
        items = m.VGroup(*[T(f"{i}.  {x['title']}", 32, FG) for i, x in enumerate(SECS, 1)]).arrange(m.DOWN, buff=0.22, aligned_edge=m.LEFT).move_to([0, -0.3, 0])
        if items.height > 5.5:
            items.scale_to_fit_height(5.5)
        s.play(m.Write(hd), run_time=0.8)
        s.say("Here is the plan. " + ". ".join(x["title"] for x in SECS) + ".", m.Succession(*[m.FadeIn(i, shift=m.RIGHT * 0.2) for i in items]))
        s.wait(0.5)


def _make(i, sec):
    class _S(Lesson):
        header = sec["title"]; page = f"{i} / {len(SECS)}"

        def construct(s):
            if sec.get("hook"):
                s.hook(sec["hook"]["text"], sec["hook"]["say"])
            for b in sec["beats"]:
                s.beat(b)
            s.wait(0.6)
    _S.__name__ = _S.__qualname__ = f"S{i:02d}"
    return _S


for _i, _sec in enumerate(SECS, 1):
    globals()[f"S{_i:02d}"] = _make(_i, _sec)


class S99(Lesson):
    header = "Recap"

    def construct(s):
        cs = m.VGroup(*[card(T(x["title"], 30, BLUE, bold=True), LN, 0.16) for x in SECS]).arrange(m.DOWN, buff=0.2).move_to([0, -0.2, 0])
        if cs.height > 5.4:
            cs.scale_to_fit_height(5.4)
        s.say("Let's recap. We covered " + ", ".join(x["title"] for x in SECS) + ". Keep practising, and see you in the next lesson.",
              m.Succession(*[m.FadeIn(c, shift=m.UP * 0.15) for c in cs]))
        s.wait(1)
