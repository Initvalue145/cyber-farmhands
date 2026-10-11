# -*- coding: utf-8 -*-
# 《赛博长工 Cyber Farmhands》 —— 由 Claude Opus 5.5 extra 制作 / Made by Claude Opus 5.5 extra
"""语言切换 / Language switch.  FILM_LANG=en 渲染英文版 / renders the English cut.

画面里的中文在绘制时查表替换；时间轴始终按中文计算，所以中英两版逐帧同步。
On-screen Chinese is looked up at draw time; the timeline is always computed from the
Chinese text, so both cuts are frame-for-frame identical in timing.
"""
import os, re

LANG = os.environ.get("FILM_LANG", "zh")
MISSING = set()
_CJK = re.compile(r"[　-〿一-鿿＀-￯]")

from i18n_en_英文表 import EN, PATTERNS  # noqa: E402


def has_cjk(s):
    return bool(_CJK.search(s))


def T(s):
    if LANG != "en" or not s or not has_cjk(s):
        return s
    r = EN.get(s)
    if r is not None:
        return r
    for pat, rep in PATTERNS:
        m = re.fullmatch(pat, s)
        if m:
            return m.expand(rep)
    MISSING.add(s)
    return s
