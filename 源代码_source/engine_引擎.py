# -*- coding: utf-8 -*-
# 《赛博长工 Cyber Farmhands》 —— 由 Claude Opus 5.5 extra 制作 / Made by Claude Opus 5.5 extra
"""Pixel engine: canvas, fonts, palette, sprites, UI widgets, timeline."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from i18n_翻译 import T, has_cjk, LANG

W, H = 480, 270
FPS = 24

# 宋体 12px 自带点阵字形，是像素风文字的关键 / SimSun 12px ships embedded bitmap glyphs (the pixel look)
FONT_SONG = os.environ.get("PIXEL_FONT_SONG", "C:/Windows/Fonts/simsun.ttc")
FONT_HEI = os.environ.get("PIXEL_FONT_HEI", "C:/Windows/Fonts/simhei.ttf")
F12 = ImageFont.truetype(FONT_SONG, 12, index=0)
FH12 = ImageFont.truetype(FONT_HEI, 12)


def dr(img):
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    return d


# ---------------------------------------------------------------- palette
P = dict(
    black=(14, 12, 22), ink=(28, 24, 42), night=(22, 22, 44), night2=(34, 34, 66),
    white=(250, 248, 240), grey=(150, 150, 168), dgrey=(80, 80, 98), lgrey=(205, 205, 215),
    red=(232, 72, 72), dred=(150, 36, 46), green=(96, 210, 110), dgreen=(40, 120, 70),
    yellow=(255, 214, 72), gold=(250, 190, 50), orange=(240, 140, 60),
    blue=(80, 150, 240), dblue=(40, 70, 150), sky=(120, 190, 255), cyan=(110, 230, 240),
    pink=(255, 140, 170), purple=(150, 100, 220), brown=(130, 82, 56), dbrown=(84, 52, 38),
    term=(18, 20, 30), termg=(110, 240, 150),
    clawd=(217, 119, 87), xianyu=(255, 222, 60),
)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, dur):
    if dur <= 0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / dur)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in(x):
    return x ** 3


def ease_io(x):
    return 3 * x * x - 2 * x * x * x


def ease_back(x):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def mixc(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- text
_tcache = {}


def text_img(s, col, font=F12, outline=None, shadow=None):
    if font is FH12 and "¥" in s:
        font = F12
    key = (s, col, id(font), outline, shadow)
    im = _tcache.get(key)
    if im is not None:
        return im
    tw = int(math.ceil(font.getlength(s))) + 4
    th = 16
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = dr(im)
    ox, oy = 1, 1
    if outline:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    d.text((ox + dx, oy + dy), s, font=font, fill=outline + (255,))
    if shadow:
        d.text((ox + 1, oy + 1), s, font=font, fill=shadow + (255,))
    d.text((ox, oy), s, font=font, fill=col + (255,))
    _tcache[key] = im
    if len(_tcache) > 6000:
        _tcache.clear()
    return im


def tw(s, font=F12):
    s = T(s)
    if font is FH12 and "¥" in s:
        font = F12
    return int(round(font.getlength(s)))


def text(img, x, y, s, col=P["white"], font=F12, outline=None, shadow=None, anchor="l", scale=1):
    if not s:
        return
    s = T(s)
    im = text_img(s, col, font, outline, shadow)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    w = (tw(s, font) + 2) * scale
    if anchor == "c":
        x = x - w // 2
    elif anchor == "r":
        x = x - w
    img.paste(im, (int(x) - scale, int(y) - scale), im)


def wrap(s, maxw, font=F12):
    s = T(s)
    lines = []
    for para in s.split("\n"):
        if not has_cjk(para):  # English: wrap on word boundaries
            cur = ""
            for word in para.split(" "):
                cand = word if not cur else cur + " " + word
                if cur and tw(cand, font) > maxw:
                    lines.append(cur)
                    cur = word
                else:
                    cur = cand
            lines.append(cur)
            continue
        cur = ""
        for ch in para:
            if tw(cur + ch, font) > maxw:
                # keep CJK punctuation from starting a line
                if ch in "，。！？、…）」』：；":
                    cur += ch
                    lines.append(cur)
                    cur = ""
                    continue
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        lines.append(cur)
    return lines


def big_text(img, x, y, s, col, scale=3, font=FH12, outline=P["black"], shadow=None, anchor="c"):
    s = T(s)
    im = text_img(s, col, font, outline=None)
    w0 = tw(s, font) + 2
    base = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    bw = w0 * scale
    if anchor == "c":
        x = x - bw // 2
    x = int(x) - scale
    y = int(y) - scale
    if shadow:
        sh = text_img(s, shadow, font).resize(base.size, Image.NEAREST)
        img.paste(sh, (x + scale, y + scale), sh)
    if outline:
        ol = text_img(s, outline, font).resize(base.size, Image.NEAREST)
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                if dx or dy:
                    img.paste(ol, (x + dx, y + dy), ol)
    img.paste(base, (x, y), base)


# ---------------------------------------------------------------- ascii sprites
def ascii_sprite(rows, cmap):
    h = len(rows)
    w = max(len(r) for r in rows)
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in cmap:
                a[y, x, :3] = cmap[ch]
                a[y, x, 3] = 255
    return Image.fromarray(a, "RGBA")


_scache = {}


def scaled(spr, s):
    if s == 1:
        return spr
    key = (id(spr), s)
    r = _scache.get(key)
    if r is None:
        r = spr.resize((spr.width * s, spr.height * s), Image.NEAREST)
        _scache[key] = r
    return r


def paste(img, spr, x, y, s=1, flip=False):
    sp = scaled(spr, s)
    if flip:
        sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(sp, (int(round(x)), int(round(y))), sp)


def outline_rgba(a, col, diag=False):
    """add 1px outline around alpha>0 of numpy RGBA array (in place, returns new)."""
    m = a[:, :, 3] > 0
    d = np.zeros_like(m)
    d[1:, :] |= m[:-1, :]
    d[:-1, :] |= m[1:, :]
    d[:, 1:] |= m[:, :-1]
    d[:, :-1] |= m[:, 1:]
    if diag:
        d[1:, 1:] |= m[:-1, :-1]
        d[:-1, :-1] |= m[1:, 1:]
        d[1:, :-1] |= m[:-1, 1:]
        d[:-1, 1:] |= m[1:, :-1]
    o = d & ~m
    a[o, :3] = col
    a[o, 3] = 255
    return a


ICON_CMAP = {
    "O": (150, 90, 10), "Y": (255, 206, 64), "y": (196, 128, 24),
    "W": (250, 250, 255), "w": (170, 190, 230), "B": (60, 90, 170), "K": (20, 20, 30),
    "R": (232, 72, 72), "r": (150, 36, 46), "G": (96, 210, 110), "g": (40, 120, 70),
    "P": (255, 140, 170), "C": (110, 230, 240), "N": (40, 40, 60), "S": (190, 190, 205),
    "L": (120, 190, 255), "D": (90, 90, 110),
}

ICONS = {
    "coin": ascii_sprite([
        "...OOOO...",
        ".OOYYYYOO.",
        ".OYyYYyYO.",
        "OYYYyyYYYO",
        "OYYyyyyYYO",
        "OYYYyyYYYO",
        "OYYyyyyYYO",
        ".OYYyyYYO.",
        ".OOYYYYOO.",
        "...OOOO...",
    ], ICON_CMAP),
    "plane": ascii_sprite([
        "..........W",
        "........WWW",
        "......WWWWw",
        "....WWWWWw.",
        "..WWWWWWww.",
        "WWWWWWWww..",
        "...wwWWw...",
        "....wwWw...",
        ".....wWw...",
        "......w....",
    ], ICON_CMAP),
    "clock": ascii_sprite([
        "..NNNNN..",
        ".NWWWWWN.",
        "NWWWKWWWN",
        "NWWWKWWWN",
        "NWWWKKKWN",
        "NWWWWWWWN",
        "NWWWWWWWN",
        ".NWWWWWN.",
        "..NNNNN..",
    ], ICON_CMAP),
    "check": ascii_sprite([
        ".......GG",
        "......GGg",
        "GG...GGg.",
        "gGG.GGg..",
        ".gGGGg...",
        "..gGg....",
    ], ICON_CMAP),
    "cross": ascii_sprite([
        "RR....RR",
        "rRR..RRr",
        ".rRRRRr.",
        "..rRRr..",
        ".RRrrRR.",
        "RRr..rRR",
        "Rr....rR",
    ], ICON_CMAP),
    "warn": ascii_sprite([
        "....YY....",
        "...YKKY...",
        "...YKKY...",
        "..YYKKYY..",
        "..YYKKYY..",
        ".YYYKKYYY.",
        ".YYYYYYYY.",
        "YYYYKKYYYY",
        "YYYYYYYYYY",
    ], {"Y": (255, 206, 64), "K": (40, 30, 20)}),
    "lock": ascii_sprite([
        "..SSSS..",
        ".S....S.",
        ".S....S.",
        "YYYYYYYY",
        "YYYKKYYY",
        "YYYKKYYY",
        "YYYYYYYY",
    ], ICON_CMAP),
    "eye": ascii_sprite([
        "..WWWWW..",
        ".WWKKKWW.",
        "WWKKWKKWW",
        ".WWKKKWW.",
        "..WWWWW..",
    ], ICON_CMAP),
    "heart": ascii_sprite([
        ".RR.RR.",
        "RRRRRRR",
        "RRRRRRR",
        ".RRRRR.",
        "..RRR..",
        "...R...",
    ], ICON_CMAP),
    "person": ascii_sprite([
        "..WWW..",
        "..WWW..",
        "..WWW..",
        ".......",
        ".WWWWW.",
        "WWWWWWW",
        "WWWWWWW",
    ], ICON_CMAP),
    "bolt": ascii_sprite([
        "...YY",
        "..YY.",
        ".YYYY",
        "YYYY.",
        "..YY.",
        ".YY..",
        ".Y...",
    ], ICON_CMAP),
    "wifi": ascii_sprite([
        ".WWWWW.",
        "W.....W",
        "..WWW..",
        ".W...W.",
        "...W...",
    ], ICON_CMAP),
    "speaker": ascii_sprite([
        "..W..",
        ".WW.W",
        "WWW..",
        "WWW.W",
        ".WW..",
        "..W..",
    ], ICON_CMAP),
}


# ---------------------------------------------------------------- characters
CL_MAIN = (217, 119, 87)
CL_LIGHT = (238, 152, 116)
CL_SHADE = (176, 86, 62)
CL_OUT = (70, 30, 26)
EYE = (26, 18, 22)
BLUSH = (246, 120, 128)
TEAR = (110, 190, 255)

_char_cache = {}


def make_clawd(expr="normal", walk=0, squash=0, blush=False, grey=False, arms="side"):
    key = ("clawd", expr, walk, squash, blush, grey, arms)
    if key in _char_cache:
        return _char_cache[key]
    Wc, Hc = 44, 32
    a = np.zeros((Hc, Wc, 4), np.uint8)
    bw = 28 + 2 * squash
    bh = 18 - 2 * squash
    cx = Wc // 2
    bx0 = cx - bw // 2
    bx1 = bx0 + bw - 1
    by1 = Hc - 1 - 1 - 4  # body bottom row (leave 4 rows legs + outline)
    by0 = by1 - bh + 1

    def fill(x0, y0, x1, y1, col):
        x0, x1 = max(0, x0), min(Wc - 1, x1)
        y0, y1 = max(0, y0), min(Hc - 1, y1)
        if x1 < x0 or y1 < y0:
            return
        a[y0:y1 + 1, x0:x1 + 1, :3] = col
        a[y0:y1 + 1, x0:x1 + 1, 3] = 255

    main, light, shade = CL_MAIN, CL_LIGHT, CL_SHADE
    if grey:
        main, light, shade = (120, 118, 128), (146, 144, 152), (94, 92, 104)
    fill(bx0, by0, bx1, by1, main)
    fill(bx0, by0, bx1, by0 + 1, light)
    fill(bx0, by1 - 1, bx1, by1, shade)
    # arms
    ay0 = by0 + bh // 2 - 2
    if arms == "side":
        fill(bx0 - 4, ay0, bx0 - 1, ay0 + 4, main)
        fill(bx1 + 1, ay0, bx1 + 4, ay0 + 4, main)
        fill(bx0 - 4, ay0 + 4, bx0 - 1, ay0 + 4, shade)
        fill(bx1 + 1, ay0 + 4, bx1 + 4, ay0 + 4, shade)
    elif arms == "up":  # cheering
        fill(bx0 - 4, ay0 - 8, bx0 - 1, ay0 - 4, main)
        fill(bx0 - 2, ay0 - 4, bx0 - 1, ay0, main)
        fill(bx1 + 1, ay0 - 8, bx1 + 4, ay0 - 4, main)
        fill(bx1 + 1, ay0 - 4, bx1 + 2, ay0, main)
    elif arms == "down":
        fill(bx0 - 3, ay0 + 3, bx0 - 1, ay0 + 8, main)
        fill(bx1 + 1, ay0 + 3, bx1 + 3, ay0 + 8, main)
    elif arms == "type":  # both arms forward/down a bit
        fill(bx0 - 4, ay0 + 2, bx0 - 1, ay0 + 6, main)
        fill(bx1 + 1, ay0 + 2, bx1 + 4, ay0 + 6, main)
    # legs
    legs = [bx0 + 3, bx0 + 8, bx1 - 9, bx1 - 4]
    for i, lx in enumerate(legs):
        lift = 0
        if walk == 1 and i in (0, 2):
            lift = 2
        if walk == 2 and i in (1, 3):
            lift = 2
        fill(lx, by1 + 1, lx + 1, by1 + 4 - lift, shade)
    a = outline_rgba(a, CL_OUT if not grey else (50, 50, 60))
    # eyes
    ecl = cx - 7  # left eye left col
    ecr = cx + 4
    ey = by0 + 4
    e = EYE

    def px(x, y, col):
        if 0 <= x < Wc and 0 <= y < Hc:
            a[y, x, :3] = col
            a[y, x, 3] = 255

    for ex in (ecl, ecr):
        if expr in ("normal", "talk", "sweat", "worried", "determined", "sad", "cry"):
            for yy in range(ey, ey + 5):
                for xx in range(ex, ex + 3):
                    px(xx, yy, e)
            if expr not in ("sad", "cry"):
                px(ex, ey, (255, 255, 255))
        elif expr == "blink":
            for xx in range(ex, ex + 3):
                px(xx, ey + 4, e)
        elif expr == "sleep":
            for xx in range(ex - 1, ex + 4):
                px(xx, ey + 3, e)
        elif expr == "happy":
            px(ex + 1, ey + 1, e)
            px(ex, ey + 2, e); px(ex + 2, ey + 2, e)
            px(ex - 1, ey + 3, e); px(ex + 3, ey + 3, e)
        elif expr == "shock":
            for yy in range(ey - 1, ey + 6):
                for xx in range(ex - 1, ex + 4):
                    px(xx, yy, e)
            for yy in range(ey, ey + 2):
                for xx in range(ex, ex + 2):
                    px(xx, yy, (255, 255, 255))
        elif expr == "dot":
            px(ex + 1, ey + 2, e); px(ex + 1, ey + 3, e)
        elif expr == "dead":
            for i in range(5):
                px(ex - 1 + i, ey + i, e)
                px(ex + 3 - i, ey + i, e)
        elif expr == "squint":  # > <
            pass
    if expr == "squint":
        for i, (dx, dy) in enumerate([(0, 0), (1, 1), (2, 2), (1, 3), (0, 4)]):
            px(ecl + dx, ey + dy, e)
            px(ecr + 2 - dx, ey + dy, e)
    if expr == "determined":
        for i in range(4):
            px(ecl - 1 + i, ey - 3 + i // 2 + (1 if i > 1 else 0) - 1, e)
            px(ecr + 3 - i, ey - 3 + i // 2 + (1 if i > 1 else 0) - 1, e)
    if expr in ("worried", "sad", "cry"):
        for i in range(4):
            px(ecl - 1 + i, ey - 1 - (i // 2), e) if False else None
        # brows rising toward centre
        for i in range(3):
            px(ecl + i, ey - 1 - i // 2 - (1 if i == 2 else 0), e)
            px(ecr + 2 - i, ey - 1 - i // 2 - (1 if i == 2 else 0), e)
    if expr == "cry":
        for yy in range(ey + 5, by1 + 1):
            px(ecl + 1, yy, TEAR)
            px(ecr + 1, yy, TEAR)
    if blush or expr in ("happy",):
        for xx in range(ecl - 3, ecl):
            px(xx, ey + 6, BLUSH)
        for xx in range(ecr + 3, ecr + 6):
            px(xx, ey + 6, BLUSH)
    img = Image.fromarray(a, "RGBA")
    _char_cache[key] = img
    return img


# Codex: a soft cloud with a little terminal for a face
CX_MAIN = (234, 238, 255)
CX_LIGHT = (255, 255, 255)
CX_SHADE = (186, 194, 232)
CX_OUT = (44, 46, 82)
CX_SCREEN = (26, 28, 44)
CX_TXT = (120, 245, 160)

MICRO = {
    ">": ["X..", ".X.", "..X", ".X.", "X.."],
    "<": ["..X", ".X.", "X..", ".X.", "..X"],
    "_": ["...", "...", "...", "...", "XXX"],
    "^": [".X.", "X.X", "...", "...", "..."],
    "T": ["XXX", ".X.", ".X.", ".X.", "..."],
    "O": ["XXX", "X.X", "X.X", "X.X", "XXX"],
    "o": ["...", "XXX", "X.X", "XXX", "..."],
    "x": ["X.X", "X.X", ".X.", "X.X", "X.X"],
    "-": ["...", "...", "XXX", "...", "..."],
    "*": ["...", "X.X", ".X.", "X.X", "..."],
    ".": ["...", "...", "...", "...", ".X."],
    "w": ["......", "......", "X.X.X.", "X.X.X.", ".X.X.."],
    "v": ["...", "...", "X.X", ".X.", "..."],
    "$": [".X.", "XXX", "X..", "XXX", "..X", "XXX", ".X."],
    "?": ["XXX", "..X", ".XX", "...", ".X."],
    "!": [".X.", ".X.", ".X.", "...", ".X."],
    "E": ["XXX", "X..", "XXX", "X..", "XXX"],
    "R": ["XX.", "X.X", "XX.", "X.X", "X.X"],
    "=": ["...", "XXX", "...", "XXX", "..."],
    "Q": ["XXX", "X.X", "X.X", "XXX", "..X"],
    "U": ["X.X", "X.X", "X.X", "XXX", "..."],
    "n": ["...", "XXX", "X.X", "X.X", "..."],
    "@": ["XXX", "..X", "XXX", "X.X", "XXX"],
    " ": ["..", "..", "..", "..", ".."],
}

CODEX_FACES = {
    "normal": (">_", CX_TXT), "talk": (">_", CX_TXT), "happy": ("^w^", CX_TXT),
    "excited": (">w<", CX_TXT), "sad": ("T_T", (140, 200, 255)), "shock": ("O_O", CX_TXT),
    "dizzy": ("@_@", CX_TXT), "dead": ("x_x", (180, 180, 190)), "flat": ("-_-", CX_TXT),
    "money": ("$_$", (255, 214, 72)), "think": ("...", CX_TXT), "error": ("ERR", (240, 80, 80)),
    "sweat": ("-_-", CX_TXT), "blink": ("-_-", CX_TXT), "sleep": ("-.-", CX_TXT),
    "q": ("?_?", CX_TXT), "cool": ("", CX_TXT), "uwu": ("UwU", CX_TXT), "cry": ("T_T", (140, 200, 255)),
}


def micro_text_rgba(a, x, y, s, col):
    cx = x
    for ch in s:
        g = MICRO.get(ch, MICRO[" "])
        gh = len(g)
        oy = y - (gh - 5) // 2
        for yy, row in enumerate(g):
            for xx, c in enumerate(row):
                if c == "X":
                    X, Y = cx + xx, oy + yy
                    if 0 <= X < a.shape[1] and 0 <= Y < a.shape[0]:
                        a[Y, X, :3] = col
                        a[Y, X, 3] = 255
        cx += len(g[0]) + 1


def micro_width(s):
    return sum(len(MICRO.get(c, MICRO[" "])[0]) + 1 for c in s) - 1


def make_codex(expr="normal", walk=0, cursor=True, grey=False, shades=False, squash=0):
    key = ("codex", expr, walk, cursor, grey, shades, squash)
    if key in _char_cache:
        return _char_cache[key]
    Wc, Hc = 42, 36
    yy, xx = np.mgrid[0:Hc, 0:Wc]
    base = Hc - 6
    cx = Wc / 2 - 0.5
    sy = 1.0 + 0.08 * squash
    circles = [
        (cx, base - 11, 12.5), (cx - 9, base - 7, 8.0), (cx + 9, base - 7, 8.0),
        (cx - 5, base - 18, 7.5), (cx + 5.5, base - 19, 8.0),
    ]
    m = np.zeros((Hc, Wc), bool)
    for (ccx, ccy, r) in circles:
        m |= ((xx - ccx) / sy) ** 2 + ((yy - (base - (base - ccy) / sy))) ** 2 <= r * r
    m &= yy <= base
    a = np.zeros((Hc, Wc, 4), np.uint8)
    main, light, shade = CX_MAIN, CX_LIGHT, CX_SHADE
    if grey:
        main, light, shade = (150, 150, 162), (170, 170, 180), (120, 120, 134)
    a[m, :3] = main
    a[m, 3] = 255
    # shading: pixels whose up-left neighbour is empty get light, bottom-right rim shade
    up = np.zeros_like(m); up[1:, :] = m[:-1, :]
    left = np.zeros_like(m); left[:, 1:] = m[:, :-1]
    dn = np.zeros_like(m); dn[:-1, :] = m[1:, :]
    rt = np.zeros_like(m); rt[:, :-1] = m[:, 1:]
    hl = m & (~up)
    a[hl, :3] = light
    sh = m & ((~dn) | (yy >= base - 1))
    a[sh, :3] = shade
    sh2 = m & (~rt) & (yy > base - 14)
    a[sh2, :3] = shade
    # feet
    for fx in (int(cx) - 7, int(cx) + 4):
        lift = 0
        if walk == 1 and fx < cx:
            lift = 1
        if walk == 2 and fx > cx:
            lift = 1
        a[base + 1:base + 3 - lift, fx:fx + 4, :3] = shade
        a[base + 1:base + 3 - lift, fx:fx + 4, 3] = 255
    a = outline_rgba(a, CX_OUT if not grey else (60, 60, 70))
    # face screen
    sx0, sx1 = int(cx) - 9, int(cx) + 10
    sy0, sy1 = base - 15, base - 5
    scr = CX_SCREEN if not grey else (50, 50, 58)
    a[sy0:sy1 + 1, sx0 + 1:sx1, :3] = scr
    a[sy0 + 1:sy1, sx0:sx1 + 1, :3] = scr
    a[sy0:sy1 + 1, sx0 + 1:sx1, 3] = 255
    a[sy0 + 1:sy1, sx0:sx1 + 1, 3] = 255
    # small glare
    a[sy0 + 1, sx1 - 3:sx1 - 1, :3] = (70, 76, 110)
    face, col = CODEX_FACES.get(expr, CODEX_FACES["normal"])
    if grey:
        col = (120, 120, 130)
    if expr in ("normal", "talk"):
        s = ">" + ("_" if cursor else " ")
        micro_text_rgba(a, sx0 + 4, sy0 + 3, s, col)
    elif expr == "cool" or shades:
        # sunglasses
        a[sy0 + 3:sy0 + 6, sx0 + 2:sx0 + 8, :3] = (10, 10, 14)
        a[sy0 + 3:sy0 + 6, sx1 - 7:sx1 - 1, :3] = (10, 10, 14)
        a[sy0 + 3, sx0 + 2:sx1 - 1, :3] = (10, 10, 14)
        a[sy0 + 3, sx0 + 3:sx0 + 5, :3] = (200, 200, 230)
        a[sy0 + 3, sx1 - 6:sx1 - 4, :3] = (200, 200, 230)
        micro_text_rgba(a, int(cx) - 1, sy0 + 3, "v" if expr != "cool" else "", col)
    else:
        wdt = micro_width(face)
        micro_text_rgba(a, int(cx) - wdt // 2 + 1, sy0 + 3, face, col)
    img = Image.fromarray(a, "RGBA")
    _char_cache[key] = img
    return img


# --------------------------------------------------------------- emotes
EMOTES = {
    "!": ascii_sprite([".RR.", ".RR.", ".RR.", ".RR.", "....", ".RR."], {"R": (255, 80, 80)}),
    "?": ascii_sprite(["YYYY", "...Y", "..YY", ".YY.", "....", ".YY."], {"Y": (255, 220, 90)}),
    "sweat": ascii_sprite(["..L.", ".LL.", "LLLL", "LLWL", ".LL."], {"L": (120, 190, 255), "W": (230, 245, 255)}),
    "anger": ascii_sprite(["R.R.R", ".RRR.", "RR.RR", ".RRR.", "R.R.R"], {"R": (240, 70, 70)}),
    "heart": ICONS["heart"],
    "z": ascii_sprite(["WWW", "..W", ".W.", "WWW"], {"W": (220, 220, 255)}),
    "Z": ascii_sprite(["WWWW", "...W", "..W.", ".W..", "WWWW"], {"W": (220, 220, 255)}),
    "note": ascii_sprite(["..WW", "..WW", "..W.", "..W.", "WWW.", "WWW."], {"W": (255, 255, 255)}),
    "spark": ascii_sprite(["..Y..", "..Y..", "YYYYY", "..Y..", "..Y.."], {"Y": (255, 230, 120)}),
}


def emote(img, kind, x, y, t=0.0, s=1):
    e = EMOTES[kind]
    bob = int(round(math.sin(t * 8) * 1))
    paste(img, e, x, y + bob, s)


# --------------------------------------------------------------- UI widgets
def rrect(img, x, y, w, h, col):
    d = dr(img)
    x, y, w, h = int(x), int(y), int(w), int(h)
    if w <= 2 or h <= 2:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=col)
        return
    d.rectangle([x + 1, y, x + w - 2, y + h - 1], fill=col)
    d.rectangle([x, y + 1, x + w - 1, y + h - 2], fill=col)


def panel(img, x, y, w, h, fill, border=P["black"], hi=None, shadow=True):
    if shadow:
        rrect(img, x + 2, y + 2, w, h, (0, 0, 0))
    rrect(img, x, y, w, h, border)
    rrect(img, x + 1, y + 1, w - 2, h - 2, fill)
    if hi:
        d = dr(img)
        d.line([x + 2, y + 1, x + w - 3, y + 1], fill=hi)


def window(img, x, y, w, h, title, bar=(70, 90, 160), fill=(245, 245, 250), title_col=P["white"], icon=None):
    x, y, w, h = int(x), int(y), int(w), int(h)
    rrect(img, x + 3, y + 3, w, h, (0, 0, 0))
    rrect(img, x, y, w, h, (20, 20, 30))
    d = dr(img)
    d.rectangle([x + 1, y + 1, x + w - 2, y + 14], fill=bar)
    d.line([x + 2, y + 2, x + w - 3, y + 2], fill=mixc(bar, (255, 255, 255), 0.35))
    d.rectangle([x + 1, y + 15, x + w - 2, y + h - 2], fill=fill)
    tx = x + 5
    if icon is not None:
        paste(img, icon, x + 4, y + 3)
        tx += icon.width + 3
    text(img, tx, y + 2, title, title_col)
    # buttons
    for i, c in enumerate([(240, 90, 90), (250, 200, 70), (100, 200, 110)]):
        bx = x + w - 10 - i * 9
        d.rectangle([bx, y + 5, bx + 5, y + 10], fill=c)
    return (x + 1, y + 15, w - 2, h - 17)


def bar(img, x, y, w, h, frac, col, bg=(40, 40, 56), border=P["black"]):
    d = dr(img)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=border)
    d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], fill=bg)
    fw = int((w - 2) * clamp(frac))
    if fw > 0:
        d.rectangle([x + 1, y + 1, x + fw, y + h - 2], fill=col)
        d.line([x + 1, y + 1, x + fw, y + 1], fill=mixc(col, (255, 255, 255), 0.4))


def bubble(img, x, y, s, side="l", fill=(255, 255, 255), col=P["ink"], maxw=150, border=(40, 40, 50)):
    lines = wrap(s, maxw)
    w = max(tw(l) for l in lines) + 10
    h = len(lines) * 14 + 6
    if side == "r":
        x = x - w
    rrect(img, x, y, w, h, border)
    rrect(img, x + 1, y + 1, w - 2, h - 2, fill)
    d = dr(img)
    if side == "l":
        d.polygon([(x - 3, y + 6), (x + 1, y + 4), (x + 1, y + 9)], fill=border)
    else:
        d.polygon([(x + w + 2, y + 6), (x + w - 2, y + 4), (x + w - 2, y + 9)], fill=border)
    for i, l in enumerate(lines):
        text(img, x + 5, y + 4 + i * 14, l, col)
    return w, h


def stamp(img, cx, cy, s, col=(220, 40, 40), t=1.0, scale=2, rot=-8):
    """big rubber stamp text with a frame; t: 0..1 slam-in progress"""
    if t <= 0:
        return
    sc = scale
    tw0 = tw(s, FH12) * sc + 16
    th0 = 12 * sc + 12
    im = Image.new("RGBA", (tw0 + 8, th0 + 8), (0, 0, 0, 0))
    d = dr(im)
    d.rectangle([2, 2, tw0 + 5, th0 + 5], outline=col + (255,), width=2)
    big_text(im, (tw0 + 8) // 2, 8, s, col, scale=sc, outline=None)
    k = 1.0 + (1 - ease_out(t)) * 1.5
    nw, nh = int(im.width * k), int(im.height * k)
    im = im.resize((nw, nh), Image.NEAREST).rotate(rot, resample=Image.NEAREST, expand=True)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


# --------------------------------------------------------------- effects
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16.0 + 1 / 32.0
BAYER_FULL = np.tile(BAYER4, (H // 4 + 1, W // 4 + 1))[:H, :W]


def dither_fade(img, k, col=(0, 0, 0)):
    """k=0 untouched, k=1 fully col. ordered dither."""
    if k <= 0:
        return img
    if k >= 1:
        return Image.new("RGB", (W, H), col)
    a = np.asarray(img).copy()
    m = BAYER_FULL < k
    a[m] = col
    return Image.fromarray(a)


def dither_mix(img_a, img_b, k):
    if k <= 0:
        return img_a
    if k >= 1:
        return img_b
    a = np.asarray(img_a).copy()
    b = np.asarray(img_b)
    m = BAYER_FULL < k
    a[m] = b[m]
    return Image.fromarray(a)


def tint(img, col, k):
    a = np.asarray(img).astype(np.float32)
    a = a * (1 - k) + np.array(col, np.float32) * k
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def darken(img, k):
    a = np.asarray(img).astype(np.float32) * (1 - k)
    return Image.fromarray(a.astype(np.uint8))


def glitch(img, amt, rng):
    a = np.asarray(img).copy()
    n = int(amt * 14)
    for _ in range(n):
        y = rng.randint(0, H - 8)
        hh = rng.randint(2, 10)
        sh = rng.randint(-int(30 * amt) - 1, int(30 * amt) + 1)
        a[y:y + hh] = np.roll(a[y:y + hh], sh, axis=1)
    if amt > 0.3:
        ch = rng.randint(0, 2)
        a[:, :, ch] = np.roll(a[:, :, ch], rng.randint(-3, 3), axis=1)
    return Image.fromarray(a)


def iris(img, k, cx=W // 2, cy=H // 2):
    """k=1 fully open, 0 closed"""
    if k >= 1:
        return img
    yy, xx = np.mgrid[0:H, 0:W]
    r = k * math.hypot(W, H) * 0.55
    # pixelate the circle edge to 2px blocks
    m = ((xx // 2 * 2 - cx) ** 2 + (yy // 2 * 2 - cy) ** 2) > r * r
    a = np.asarray(img).copy()
    a[m] = (0, 0, 0)
    return Image.fromarray(a)


def scanlines(img, k=0.12):
    a = np.asarray(img).astype(np.float32)
    a[1::2] *= (1 - k)
    return Image.fromarray(a.astype(np.uint8))


# --------------------------------------------------------------- timeline
SPEAKERS = {
    "clawd": dict(name="Claude", col=(217, 119, 87), blip="clawd"),
    "codex": dict(name="GPT", col=(150, 170, 255), blip="codex"),
    "me": dict(name="我", col=(170, 200, 170), blip="me"),
    "N": dict(name="", col=(255, 255, 255), blip=None),
    "buyer": dict(name="买家", col=(255, 200, 80), blip="buyer"),
    "sys": dict(name="系统", col=(240, 90, 90), blip="sys"),
    "both": dict(name="Claude & GPT", col=(255, 200, 150), blip="clawd"),
}


class Scene:
    def __init__(self, name, music=None):
        self.name = name
        self.cur = 0.0
        self.m = {}
        self.lines = []
        self.sfx = []
        self.music = []  # (local_t, track, opts)
        self.hud = None  # function(t)->dict or None
        self.draw = None
        self.dur = None
        self.box = "bottom"  # dialogue box style
        self.fade_in = 0.0
        self.fade_out = 0.0

    def mark(self, name):
        self.m[name] = self.cur
        return self.cur

    def wait(self, s):
        self.cur += s
        return self.cur

    def at(self, name):
        return self.m[name]

    def say(self, who, txt, hold=None, cps=16.0, expr=None, box=None, blips=True):
        start = self.cur
        n = len(txt)
        tt = n / cps
        if hold is None:
            hold = 0.75 + 0.065 * n
        ln = dict(t0=start, tt=tt, t1=start + tt + hold, who=who, text=T(txt), expr=expr, box=box or self.box)
        self.lines.append(ln)
        sp = SPEAKERS.get(who, {})
        if blips and sp.get("blip"):
            for i, ch in enumerate(txt):
                if i % 2 == 0 and ch not in " ，。…？！、：；.,!?~—":
                    self.sfx.append((start + i / cps, "blip_" + sp["blip"], {"pitch": (i // 2) % 4}))
        self.cur = start + tt + hold
        return start

    def sfx_at(self, name, t=None, **kw):
        self.sfx.append((self.cur if t is None else t, name, kw))

    def mus(self, track, t=None, **kw):
        self.music.append((self.cur if t is None else t, track, kw))

    def end(self, extra=0.0):
        self.dur = self.cur + extra

    def line_at(self, t):
        for ln in self.lines:
            if ln["t0"] <= t < ln["t1"]:
                return ln
        return None

    def talking(self, who, t):
        ln = self.line_at(t)
        return ln is not None and ln["who"] in (who, "both") and t < ln["t0"] + ln["tt"]

    def expr_of(self, who, t, default="normal"):
        ln = self.line_at(t)
        if ln is not None and ln["who"] in (who, "both") and ln["expr"]:
            return ln["expr"]
        return default


# --------------------------------------------------------------- portraits
def face_me(expr="normal"):
    """front-facing pixel face of '我' (24x24 native)."""
    key = ("me", expr)
    if key in _char_cache:
        return _char_cache[key]
    rows = [
        "........................",
        "........HHHHHHHH........",
        "......HHHHHHHHHHHH......",
        ".....HHHHHHHHHHHHHH.....",
        "....HHHHHHHHHHHHHHHH....",
        "....HHHHHHHHHHHHHHHH....",
        "...HHHHHHHHHHHHHHHHHH...",
        "...HHHSSHHHHHHHHSSHHH...",
        "...HHSSSSSSSSSSSSSSHH...",
        "...HSSSSSSSSSSSSSSSSH...",
        "...SSSSSSSSSSSSSSSSSS...",
        "..sSSSSSSSSSSSSSSSSSSs..",
        "..sSSSSSSSSSSSSSSSSSSs..",
        "...SSSSSSSSSSSSSSSSSS...",
        "...SSSSSSSSSSSSSSSSSS...",
        "....SSSSSSSSSSSSSSSS....",
        ".....SSSSSSSSSSSSSS.....",
        "......ssSSSSSSSSss......",
        "........ssssssss........",
        ".........SSSSSS.........",
        "......HHHHSSSSHHHH......",
        "....HHHHHHHHHHHHHHHH....",
        "...HHHHHHHHHHHHHHHHHH...",
        "...HHHHHHHHHHHHHHHHHH...",
    ]
    cmap = {"H": (40, 36, 52), "S": (248, 214, 182), "s": (220, 176, 146)}
    spr = ascii_sprite(rows, cmap)
    a = np.array(spr)
    # hoodie colour for bottom rows
    for y in range(20, 24):
        for x in range(24):
            if a[y, x, 3] and tuple(a[y, x, :3]) == (40, 36, 52):
                a[y, x, :3] = (92, 108, 140)
    a = outline_rgba(a, (20, 16, 26))
    E = (30, 24, 34)

    def px(x, y, c=E):
        a[y, x, :3] = c
        a[y, x, 3] = 255

    if expr in ("normal", "talk"):
        for y in (11, 12):
            px(8, y); px(15, y)
        px(11, 15); px(12, 15)
    elif expr == "tired":
        for x in (7, 8, 9):
            px(x, 12)
        for x in (14, 15, 16):
            px(x, 12)
        for x in (7, 8, 9, 14, 15, 16):
            px(x, 13, (170, 140, 170))
        px(11, 16); px(12, 16)
    elif expr == "sleep":
        for x in (7, 8, 9):
            px(x, 12)
        for x in (14, 15, 16):
            px(x, 12)
        px(11, 15); px(12, 15); px(11, 16); px(12, 16)
    elif expr == "shock":
        for y in (10, 11, 12, 13):
            for x in (7, 8, 9):
                px(x, y, (255, 255, 255))
            for x in (14, 15, 16):
                px(x, y, (255, 255, 255))
        px(8, 11); px(8, 12); px(15, 11); px(15, 12)
        for y in (15, 16, 17):
            px(11, y); px(12, y)
        for y in (9, 10, 11, 12):
            px(20, y, (120, 190, 255))
    elif expr == "cry":
        for x in (7, 8, 9, 14, 15, 16):
            px(x, 12)
        for y in range(13, 19):
            px(8, y, (120, 190, 255)); px(15, y, (120, 190, 255))
        px(10, 16); px(11, 15); px(12, 15); px(13, 16)
    elif expr == "smile":
        px(7, 12); px(8, 11); px(9, 12)
        px(14, 12); px(15, 11); px(16, 12)
        px(10, 15); px(11, 16); px(12, 16); px(13, 15)
        for x in (5, 6):
            px(x, 14, (255, 160, 160))
        for x in (17, 18):
            px(x, 14, (255, 160, 160))
    elif expr == "blank":
        px(8, 12); px(15, 12)
        px(11, 16); px(12, 16)
    img = Image.fromarray(a, "RGBA")
    _char_cache[key] = img
    return img


def avatar(col, kind=0):
    key = ("av", col, kind)
    if key in _char_cache:
        return _char_cache[key]
    rows = [
        "..........",
        "...XXXX...",
        "..XXXXXX..",
        "..XXXXXX..",
        "..XXXXXX..",
        "...XXXX...",
        ".XXXXXXXX.",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
    ]
    spr = ascii_sprite(rows, {"X": col})
    _char_cache[key] = spr
    return spr


def portrait(who, expr, t, talking):
    """returns RGBA image for the dialogue box portrait (approx 40x40)."""
    if who == "clawd":
        e = expr or "normal"
        if e == "normal" and (t * 0.7) % 3.0 < 0.1:
            e = "blink"
        return make_clawd(e), 1
    if who == "codex":
        e = expr or "normal"
        return make_codex(e, cursor=(t * 2) % 1 < 0.5), 1
    if who == "me":
        return face_me(expr or "normal"), 1
    return None, 1
