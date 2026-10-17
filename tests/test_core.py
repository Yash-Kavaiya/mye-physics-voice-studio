from voicestudio import stt, script
from voicestudio.voice import align


def test_wer_normalizes_math():
    assert stt.wer("equals two pi i times the sum", "equals 2πi times the sum") == 0.0
    assert abs(stt.wer("a b c d", "a x c d") - 0.25) < 1e-9


def test_parse_md():
    L = script.parse_md("# T\n> sub\n## S\n? Hook | Say hook.\nLine one.\n$$ x^2 $$\n- b\n### Example: E\nLine two.\n")
    s = L["sections"][0]
    assert L["title"] == "T" and s["hook"]["say"] == "Say hook."
    assert s["beats"][0]["math"] == ["x^2"] and s["beats"][0]["bullets"] == ["b"]
    assert s["beats"][1]["example"] == "E"


def test_align_interpolates():
    w = [{"text": "Two", "start": 0, "end": 100}, {"text": "πi", "start": 100, "end": 300}]
    out = align("two pi i", w)
    assert [t for t, _, _ in out] == ["two", "pi", "i"]
