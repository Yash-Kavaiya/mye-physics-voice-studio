"""Light theme in AssemblyAI brand colours + shared ManimGX helpers."""
import manimgx as m
import numpy as np

BG = "#F6F7FB"; FG = "#0E0B3D"; MU = "#626784"; PANEL = "#FFFFFF"; LN = "#D8DCEF"
BLUE = "#2545D3"; SKY = "#5B7BFF"; LAV = "#EEF1FF"; CORAL = "#FF5C39"; GREEN = "#14A06F"; GOLD = "#F2A900"
F = "Latin Modern Roman"


def T(s, fs=30, c=FG, w=None, bold=False):
    t = m.Text(s, font=F, font_size=fs, color=c, weight=m.BOLD if bold else m.NORMAL)
    if w and t.width > w:
        t.scale_to_fit_width(w)
    return t


def M(s, fs=44, c=FG, w=None):
    t = m.MathTex(s, font_size=fs, color=c)
    if w and t.width > w:
        t.scale_to_fit_width(w)
    return t


def card(mob, c=LN, buff=0.25, fill=PANEL, sw=2):
    r = m.RoundedRectangle(width=mob.width + 2 * buff, height=mob.height + 2 * buff, corner_radius=0.14,
                           stroke_color=c, stroke_width=sw, fill_color=fill, fill_opacity=1).move_to(mob)
    return m.VGroup(r, mob)


def grad(mob):
    mob.set_color_by_gradient(BLUE, SKY)
    return mob


def wrap(s, n=46):
    out, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


class Base(m.Scene):
    """Header bar + stacking column layout that never overlaps (auto-clears when full)."""
    header = None; page = None

    def setup(s):
        s.camera.background_color = BG
        s.stack = []; s.region = (-6.4, 6.4, -3.2, 2.55); s.hdr = None
        if s.header:
            t = T(s.header, 34, FG, w=10.5, bold=True).to_corner(m.UL, buff=0.32)
            bar = m.Rectangle(width=0.08, height=t.height + 0.1, stroke_width=0, fill_color=BLUE, fill_opacity=1).next_to(t, m.LEFT, buff=0.15)
            ln = m.Line([-6.9, 0, 0], [6.9, 0, 0], stroke_width=1.5, color=LN).next_to(t, m.DOWN, buff=0.14).set_x(0)
            g = m.VGroup(bar, t, ln)
            if s.page:
                g.add(T(s.page, 20, MU).to_corner(m.DL, buff=0.14))
            s.hdr = g; s.add(g); s.add_foreground_mobjects(g)

    def clear(s):
        ms = [x for x in s.mobjects if x is not s.hdr]
        if ms:
            s.play(*[m.FadeOut(x) for x in ms], run_time=0.5)
        s.stack = []

    def hook(s, big, line):
        h = grad(T(big, 50, BLUE, w=11.5, bold=True).move_to([0, 0.4, 0]))
        ul = m.Line([-3, 0, 0], [3, 0, 0], stroke_width=5).next_to(h, m.DOWN, buff=0.3); grad(ul)
        q = T("mini-hook", 24, MU).next_to(h, m.UP, buff=0.35)
        s.say(line, m.AnimationGroup(m.FadeIn(q), m.Write(h), m.Create(ul)))
        s.play(m.FadeOut(m.VGroup(h, ul, q)), run_time=0.5)

    def col(s, items, gap=0.3):
        x0, x1, y0, y1 = s.region; Wd = x1 - x0
        for it in items:
            if it.width > Wd:
                it.scale_to_fit_width(Wd)
        top = s.stack[-1].get_bottom()[1] - gap if s.stack else y1
        need = sum(it.height for it in items) + gap * (len(items) - 1)
        pre = None
        if top - need < y0 and s.stack:
            pre = m.AnimationGroup(*[m.FadeOut(x) for x in s.stack], run_time=0.4); s.stack = []; top = y1
        an = []
        for it in items:
            it.move_to([(x0 + x1) / 2, 0, 0]).align_to([0, top, 0], m.UP); top = it.get_bottom()[1] - gap
            s.stack.append(it); an.append(m.Write(it))
        g = m.Succession(*an) if len(an) > 1 else an[0]
        return m.Succession(pre, g) if pre else g
