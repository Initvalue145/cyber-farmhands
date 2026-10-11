# -*- coding: utf-8 -*-
# 《赛博长工 Cyber Farmhands》 —— 由 Claude Opus 5.5 extra 制作 / Made by Claude Opus 5.5 extra
"""Shared scene pieces: backgrounds, actors, HUD, dialogue box."""
from engine_引擎 import *

INK = (30, 28, 40)


def kf(keys, t, step=False):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t < t1:
            if step:
                return v0
            return v0 + (v1 - v0) * clamp((t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


def typed(s, t, t0, cps=18.0):
    s = T(s)
    if LANG == "en":
        cps *= 2.2  # English strings are ~2x longer; keep the same reveal time
    if t < t0:
        return ""
    return s[: int((t - t0) * cps)]


def pop_rect(img, t, t0, x, y, w, h, dur=0.14):
    """returns True when the window should be drawn fully; draws a zoom-rect while opening."""
    if t < t0:
        return False
    p = (t - t0) / dur
    if p >= 1:
        return True
    cx, cy = x + w / 2, y + h / 2
    ww, hh = w * (0.2 + 0.8 * p), h * (0.2 + 0.8 * p)
    d = dr(img)
    d.rectangle([cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2], outline=(255, 255, 255))
    d.rectangle([cx - ww / 2 + 1, cy - hh / 2 + 1, cx + ww / 2 - 1, cy + hh / 2 - 1], outline=(40, 40, 60))
    return False


def shadow(img, cx, y, w, k=0.55):
    x0, x1 = int(cx - w / 2), int(cx + w / 2)
    box = (x0, int(y) - 2, x1, int(y) + 3)
    reg = img.crop(box)
    darkr = Image.eval(reg, lambda v: int(v * k))
    m = Image.new("L", reg.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, reg.size[0] - 1, reg.size[1] - 1], fill=255)
    img.paste(darkr, box[:2], m)


# ---------------------------------------------------------------- actors
def actor_clawd(img, sc, t, x, y, expr=None, arms="side", walk=0, grey=False, s=1, flip=False, talk=True,
                squash=0, blush=False):
    e = expr or (sc.expr_of("clawd", t, "normal") if sc else "normal")
    if e == "normal" and (t + x * 0.013) % 3.3 < 0.12:
        e = "blink"
    dy = 0
    if talk and sc is not None and sc.talking("clawd", t):
        dy = -1 if int(t * 8) % 2 == 0 else 0
    else:
        dy = -1 if int((t + 0.3) * 1.6) % 2 == 0 else 0
    spr = make_clawd(e, walk=walk, squash=squash, grey=grey, arms=arms, blush=blush)
    paste(img, spr, x, y + dy * s, s, flip)
    return spr


def actor_codex(img, sc, t, x, y, expr=None, walk=0, grey=False, s=1, talk=True, shades=False, squash=0):
    e = expr or (sc.expr_of("codex", t, "normal") if sc else "normal")
    dy = 0
    if talk and sc is not None and sc.talking("codex", t):
        dy = -1 if int(t * 8) % 2 == 0 else 0
    else:
        dy = -1 if int((t + 0.8) * 1.4) % 2 == 0 else 0
    spr = make_codex(e, walk=walk, cursor=(t * 2.2) % 1 < 0.55, grey=grey, shades=shades, squash=squash)
    paste(img, spr, x, y + dy * s, s)
    return spr


def jump_pos(t, t0, dur, p0, p1, height=30):
    p = clamp((t - t0) / dur)
    x = lerp(p0[0], p1[0], p)
    y = lerp(p0[1], p1[1], p) - math.sin(p * math.pi) * height
    return x, y, p


# ---------------------------------------------------------------- desktop
_bgc = {}


def bg_desktop(tod="day"):
    key = ("desk", tod)
    if key in _bgc:
        return _bgc[key].copy()
    img = Image.new("RGB", (W, H))
    d = dr(img)
    if tod == "day":
        top, hor = (92, 160, 250), (172, 214, 255)
        hill_far, hill, hill_hi = (120, 196, 120), (84, 176, 72), (122, 208, 92)
        cloud = (255, 255, 255)
    else:
        top, hor = (16, 18, 48), (52, 46, 100)
        hill_far, hill, hill_hi = (34, 54, 70), (26, 46, 52), (40, 70, 66)
        cloud = (70, 70, 120)
    bands = 12
    for i in range(bands):
        y0 = int(i * 170 / bands)
        d.rectangle([0, y0, W, y0 + 170 // bands + 1], fill=mixc(top, hor, i / (bands - 1)))
    d.rectangle([0, 170, W, H], fill=hor)
    r = random.Random(3)
    if tod != "day":
        for _ in range(70):
            sx, sy = r.randint(0, W - 1), r.randint(0, 150)
            img.putpixel((sx, sy), (200, 200, 255) if r.random() < 0.7 else (255, 240, 180))
        d.ellipse([388, 24, 408, 44], fill=(240, 236, 200))
        d.ellipse([394, 22, 412, 40], fill=top)
    # clouds
    for (cx, cy, sc) in [(70, 40, 1.0), (300, 26, 1.3), (420, 70, 0.8), (190, 86, 0.7)]:
        for (dx, dy, rr) in [(0, 0, 10), (12, -5, 12), (26, 0, 9), (-10, 3, 7), (36, 4, 6)]:
            rx = rr * sc
            d.ellipse([cx + dx * sc - rx, cy + dy * sc - rx * 0.7, cx + dx * sc + rx, cy + dy * sc + rx * 0.7], fill=cloud)
        d.rectangle([cx - 14 * sc, cy + 2 * sc, cx + 42 * sc, cy + 6 * sc], fill=cloud)
    # hills
    for x in range(W):
        yf = 150 + 14 * math.sin(x / 70.0 + 1.0) + 6 * math.sin(x / 23.0)
        d.line([x, int(yf), x, H], fill=hill_far)
    for x in range(W):
        yh = 182 + 22 * math.sin(x / 95.0 - 0.6) + 5 * math.sin(x / 31.0 + 2)
        d.line([x, int(yh), x, H], fill=hill)
        d.line([x, int(yh), x, int(yh) + 2], fill=hill_hi)
    # flowers / grass specks
    for _ in range(90):
        x = r.randint(0, W - 1)
        yh = 182 + 22 * math.sin(x / 95.0 - 0.6) + 5 * math.sin(x / 31.0 + 2)
        y = r.randint(int(yh) + 4, H - 1)
        img.putpixel((x, y), hill_hi if tod == "day" else (50, 80, 70))
    # desktop icons
    icons = [("此电脑", "pc"), ("回收站", "bin"), ("方案v9", "ppt"), ("简历终版", "doc"), ("机场", "plane")]
    for i, (lab, kind) in enumerate(icons):
        ix, iy = 22, 8 + i * 32
        draw_icon16(img, ix, iy, kind)
        text(img, ix + 8, iy + 17, lab, (255, 255, 255), shadow=(0, 0, 0), anchor="c")
    # taskbar
    d.rectangle([0, 256, W, H], fill=(30, 34, 56))
    d.line([0, 256, W, 256], fill=(80, 90, 130))
    rrect(img, 3, 258, 38, 11, (217, 119, 87))
    text(img, 9, 257, "开始", (255, 255, 255))
    paste(img, ICONS["plane"], 384, 259)
    paste(img, ICONS["wifi"], 400, 260)
    paste(img, ICONS["speaker"], 411, 259)
    _bgc[key] = img
    return img.copy()


def draw_icon16(img, x, y, kind):
    d = dr(img)
    if kind == "pc":
        d.rectangle([x, y + 1, x + 15, y + 11], fill=(40, 44, 60))
        d.rectangle([x + 1, y + 2, x + 14, y + 10], fill=(110, 190, 255))
        d.rectangle([x + 6, y + 12, x + 9, y + 13], fill=(40, 44, 60))
        d.rectangle([x + 3, y + 14, x + 12, y + 15], fill=(40, 44, 60))
    elif kind == "bin":
        d.rectangle([x + 3, y + 3, x + 12, y + 15], fill=(200, 210, 225))
        d.rectangle([x + 2, y + 1, x + 13, y + 3], fill=(150, 160, 180))
        for xx in (5, 8, 11):
            d.line([x + xx, y + 5, x + xx, y + 13], fill=(140, 150, 170))
    elif kind in ("ppt", "doc", "txt"):
        col = {"ppt": (230, 110, 60), "doc": (60, 120, 220), "txt": (200, 200, 210)}[kind]
        d.rectangle([x + 2, y, x + 13, y + 15], fill=(250, 250, 250))
        d.rectangle([x + 2, y, x + 13, y + 15], outline=(60, 60, 70))
        d.rectangle([x, y + 5, x + 9, y + 11], fill=col)
        for yy in (3, 13):
            d.line([x + 4, y + yy, x + 11, y + yy], fill=(170, 170, 180))
    elif kind == "plane":
        d.rectangle([x, y, x + 15, y + 15], fill=(60, 120, 220))
        paste(img, ICONS["plane"], x + 2, y + 3)


def taskbar_clock(img, hhmm):
    text(img, 458, 257, hhmm, (255, 255, 255), anchor="c")


def hhmm(minutes):
    m = int(minutes) % (24 * 60)
    return "%02d:%02d" % (m // 60, m % 60)


def terminal(img, x, y, w, h, title, lines, accent, t=0, cursor=True):
    c = window(img, x, y, w, h, title, bar=accent, fill=(20, 22, 32))
    cx, cy, cw, ch = c
    for i, (s, col) in enumerate(lines):
        text(img, cx + 4, cy + 3 + i * 13, s, col)
    if cursor and (t * 2) % 1 < 0.5:
        n = len(lines)
        last = lines[-1][0] if lines else ""
        d = dr(img)
        bx = cx + 4 + tw(last) + 1
        d.rectangle([bx, cy + 3 + (n - 1) * 13 + 1, bx + 5, cy + 3 + (n - 1) * 13 + 11], fill=(200, 200, 210))
    return c


# ---------------------------------------------------------------- HUD
def draw_hud(img, money, flow, clock, t=0, locked=False, x=376, y=4, flash_money=False):
    panel(img, x, y, 100, 44, (24, 22, 40), border=(10, 10, 16))
    paste(img, ICONS["coin"], x + 4, y + 4)
    col = (255, 220, 90)
    if flash_money and int(t * 8) % 2 == 0:
        col = (255, 255, 255)
    ms = "¥%.2f" % money if money < 1000 else "¥%d" % int(money)
    text(img, x + 17, y + 3, ms, col)
    text(img, x + 17 + tw(ms) + 2, y + 3, "/280", (150, 150, 170))
    paste(img, ICONS["plane"], x + 3, y + 17)
    fcol = (255, 255, 255) if flow > 1 else ((255, 80, 80) if int(t * 6) % 2 == 0 else (255, 200, 200))
    text(img, x + 17, y + 16, "%.1fGB" % max(0, flow), fcol)
    bar(img, x + 58, y + 19, 36, 6, flow / 12.0, (110, 200, 255) if flow > 1 else (240, 80, 80))
    paste(img, ICONS["clock"], x + 4, y + 30)
    text(img, x + 17, y + 29, hhmm(clock), (220, 220, 240))
    if locked:
        paste(img, ICONS["lock"], x + 89, y + 4)


# ---------------------------------------------------------------- dialogue box
BOX_Y = 212


def draw_dialogue(img, sc, t):
    ln = sc.line_at(t)
    if not ln:
        return
    lt = t - ln["t0"]
    txt = ln["text"]
    nshow = len(txt) if ln["tt"] <= 0 else int(clamp(lt / ln["tt"]) * len(txt))
    who = ln["who"]
    sp = SPEAKERS[who]
    popin = clamp(lt / 0.08)
    if who == "N":
        x, y, w, h = 6, BOX_Y + 2, 468, 54
        panel(img, x, y, w, h, (16, 14, 28), border=(230, 230, 240))
        lines = wrap(txt, w - 24)
        shown = 0
        total_h = len(lines) * 16
        y0 = y + (h - total_h) // 2 + 1
        for i, l in enumerate(lines):
            part = l[: max(0, nshow - shown)]
            shown += len(l)
            lw = tw(l)
            text(img, x + w // 2 - lw // 2, y0 + i * 16, part, (255, 255, 255))
        return
    x, y, w, h = 6, BOX_Y, 468, 56
    panel(img, x, y, w, h, (20, 18, 34), border=(240, 240, 250))
    d = dr(img)
    d.rectangle([x + 2, y + 2, x + w - 3, y + 2], fill=(52, 48, 80))
    # portrait frame
    px0, py0 = x + 5, y + 5
    d.rectangle([px0, py0, px0 + 45, py0 + 45], fill=(46, 42, 72))
    d.rectangle([px0, py0, px0 + 45, py0 + 45], outline=sp["col"])
    talking = lt < ln["tt"]
    bob = -1 if talking and int(t * 8) % 2 == 0 else 0
    expr = ln["expr"]
    pi = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
    if who in ("clawd", "both"):
        e = expr or "normal"
        if e == "normal" and (t % 3.1) < 0.12:
            e = "blink"
        if who == "both":
            spr2 = make_codex(CODEX_FOR.get(e, "normal"), cursor=True)
            pi.paste(spr2, (12, -2 + bob), spr2)
            spr = make_clawd(e if e in _CL_OK else "normal")
            pi.paste(spr, (-8, 14 + bob), spr)
        else:
            spr = make_clawd(e if e in _CL_OK else "normal")
            pi.paste(spr, (0, 7 + bob), spr)
    elif who == "codex":
        e = expr or "normal"
        spr = make_codex(e, cursor=(t * 2) % 1 < 0.5, shades=(e == "cool"))
        pi.paste(spr, (1, 5 + bob), spr)
    elif who == "me":
        spr = scaled(face_me(expr or "normal"), 2)
        pi.paste(spr, (-2, -2 + bob), spr)
    img.paste(pi, (px0 + 1, py0 + 1), pi)
    # name tag
    name = sp["name"]
    nw = tw(name, FH12) + 12
    rrect(img, x + 56, y - 9, nw, 15, (240, 240, 250))
    rrect(img, x + 57, y - 8, nw - 2, 13, sp["col"])
    text(img, x + 62, y - 8, name, (20, 18, 30), font=FH12)
    lines = wrap(txt, w - 72)
    shown = 0
    for i, l in enumerate(lines[:3]):
        part = l[: max(0, nshow - shown)]
        shown += len(l)
        text(img, x + 58, y + 11 + i * 16 if len(lines) < 3 else y + 7 + i * 15, part, (255, 255, 255))
    if not talking and int(t * 3) % 2 == 0:
        d.polygon([(x + w - 14, y + h - 10), (x + w - 8, y + h - 10), (x + w - 11, y + h - 7)], fill=(255, 255, 255))


_CL_OK = {"normal", "blink", "happy", "shock", "sad", "cry", "determined", "worried", "sweat", "dead", "sleep",
          "squint", "dot", "talk"}
CODEX_FOR = {"shock": "shock", "happy": "happy", "sad": "sad", "normal": "normal"}


# ---------------------------------------------------------------- room
ROOM_PAL = {
    "night": dict(wall0=(28, 26, 56), wall1=(44, 40, 80), floor=(46, 34, 44), floor2=(36, 26, 36),
                  wood=(112, 74, 58), wood_d=(78, 50, 42), wood_l=(140, 96, 74), sky0=(14, 16, 44), sky1=(40, 38, 92),
                  city=(16, 16, 34), chair=(36, 36, 50), chair_l=(56, 56, 74), glow=True),
    "dawn": dict(wall0=(96, 70, 98), wall1=(130, 92, 108), floor=(110, 74, 70), floor2=(92, 60, 60),
                 wood=(172, 112, 80), wood_d=(124, 78, 60), wood_l=(204, 142, 100), sky0=(250, 150, 120),
                 sky1=(255, 214, 160), city=(110, 70, 100), chair=(60, 56, 72), chair_l=(90, 84, 104), glow=False),
    "day": dict(wall0=(150, 152, 186), wall1=(170, 168, 196), floor=(150, 108, 86), floor2=(130, 92, 74),
                wood=(196, 136, 94), wood_d=(150, 100, 70), wood_l=(222, 166, 118), sky0=(100, 170, 250),
                sky1=(180, 220, 255), city=(120, 140, 170), chair=(70, 70, 90), chair_l=(100, 100, 124), glow=False),
}
SCREEN = (240, 62, 120, 68)  # x,y,w,h of monitor screen in room


def bg_room(tod="night"):
    key = ("room", tod)
    if key in _bgc:
        return _bgc[key].copy()
    p = ROOM_PAL[tod]
    img = Image.new("RGB", (W, H))
    d = dr(img)
    for i in range(8):
        d.rectangle([0, i * 23, W, i * 23 + 23], fill=mixc(p["wall0"], p["wall1"], i / 7))
    # skirting + floor
    d.rectangle([0, 184, W, H], fill=p["floor"])
    for y in range(190, H, 12):
        d.line([0, y, W, y], fill=p["floor2"])
    r = random.Random(5)
    for y in range(184, H, 12):
        for k in range(4):
            x = r.randint(0, W)
            d.line([x, y, x, y + 11], fill=p["floor2"])
    d.rectangle([0, 180, W, 184], fill=p["wood_d"])
    # window
    wx, wy, ww, wh = 24, 20, 104, 92
    d.rectangle([wx - 4, wy - 4, wx + ww + 3, wy + wh + 3], fill=p["wood_d"])
    for i in range(10):
        d.rectangle([wx, wy + i * wh // 10, wx + ww - 1, wy + (i + 1) * wh // 10], fill=mixc(p["sky0"], p["sky1"], i / 9))
    if tod == "night":
        for _ in range(26):
            img.putpixel((r.randint(wx, wx + ww - 1), r.randint(wy, wy + 50)), (220, 220, 255))
        d.ellipse([wx + 66, wy + 8, wx + 84, wy + 26], fill=(244, 238, 200))
        d.ellipse([wx + 72, wy + 6, wx + 88, wy + 22], fill=mixc(p["sky0"], p["sky1"], 0.1))
    elif tod == "dawn":
        d.ellipse([wx + 30, wy + 58, wx + 62, wy + 90], fill=(255, 240, 190))
    else:
        for (cx, cy) in [(wx + 26, wy + 22), (wx + 76, wy + 40)]:
            d.ellipse([cx - 12, cy - 5, cx + 12, cy + 5], fill=(255, 255, 255))
            d.ellipse([cx - 4, cy - 9, cx + 10, cy + 3], fill=(255, 255, 255))
    # skyline
    bx = wx
    while bx < wx + ww:
        bw = r.randint(9, 18)
        bh = r.randint(18, 44)
        d.rectangle([bx, wy + wh - bh, min(bx + bw, wx + ww - 1), wy + wh - 1], fill=p["city"])
        if tod == "night":
            for yy in range(wy + wh - bh + 3, wy + wh - 2, 5):
                for xx in range(bx + 2, min(bx + bw, wx + ww - 2), 4):
                    if r.random() < 0.35:
                        d.rectangle([xx, yy, xx + 1, yy + 1], fill=(255, 214, 110))
        bx += bw + 1
    d.rectangle([wx + ww // 2 - 1, wy, wx + ww // 2 + 1, wy + wh], fill=p["wood_d"])
    d.rectangle([wx, wy + wh // 2 - 1, wx + ww, wy + wh // 2 + 1], fill=p["wood_d"])
    d.rectangle([wx - 8, wy + wh + 3, wx + ww + 7, wy + wh + 7], fill=p["wood"])
    # poster 搞钱
    d.rectangle([150, 26, 196, 88], fill=(200, 50, 50))
    d.rectangle([152, 28, 194, 86], outline=(250, 200, 80))
    big_text(img, 173, 32, "搞", (255, 214, 80), scale=2, outline=None)
    big_text(img, 173, 58, "钱", (255, 214, 80), scale=2, outline=None)
    # shelf with noodles + books
    d.rectangle([378, 64, 470, 68], fill=p["wood"])
    d.rectangle([378, 68, 470, 70], fill=p["wood_d"])
    bxs = 382
    for i, c in enumerate([(200, 80, 80), (80, 120, 200), (230, 190, 80), (90, 160, 110), (160, 100, 180)]):
        hgt = 18 + (i * 7) % 9
        d.rectangle([bxs, 64 - hgt, bxs + 6, 63], fill=c)
        bxs += 8
    for i in range(6):  # stacked instant noodle cups
        cx = 428 + (i % 3) * 13
        cy = 52 - (i // 3) * 13
        d.polygon([(cx, cy), (cx + 11, cy), (cx + 10, cy + 11), (cx + 1, cy + 11)], fill=(240, 236, 226))
        d.rectangle([cx, cy + 3, cx + 11, cy + 6], fill=(220, 60, 50))
        d.line([cx, cy, cx + 11, cy], fill=(250, 200, 60))
    # desk
    d.rectangle([120, 150, 476, 160], fill=p["wood_l"])
    d.rectangle([120, 160, 476, 167], fill=p["wood"])
    d.rectangle([120, 167, 476, 168], fill=p["wood_d"])
    d.rectangle([126, 168, 132, 230], fill=p["wood_d"])
    d.rectangle([464, 168, 470, 230], fill=p["wood_d"])
    # pc tower (under right)
    d.rectangle([410, 178, 452, 236], fill=(30, 30, 40))
    d.rectangle([412, 180, 450, 234], fill=(44, 44, 58))
    # monitor
    sx, sy, sw, sh = SCREEN
    d.rectangle([sx - 5, sy - 5, sx + sw + 4, sy + sh + 4], fill=(28, 28, 36))
    d.rectangle([sx - 4, sy - 4, sx + sw + 3, sy + sh + 3], fill=(48, 48, 60))
    d.rectangle([sx + sw // 2 - 6, sy + sh + 5, sx + sw // 2 + 5, sy + sh + 16], fill=(40, 40, 50))
    d.rectangle([sx + sw // 2 - 22, sy + sh + 16, sx + sw // 2 + 21, sy + sh + 19], fill=(40, 40, 50))
    # keyboard + mouse
    d.rectangle([252, 151, 336, 156], fill=(50, 50, 62))
    for xx in range(254, 334, 4):
        d.line([xx, 152, xx + 2, 152], fill=(90, 90, 110))
    d.rectangle([346, 151, 352, 156], fill=(60, 60, 74))
    # noodle cup on desk
    d.polygon([(370, 136), (386, 136), (384, 152), (372, 152)], fill=(240, 236, 226))
    d.rectangle([370, 140, 386, 144], fill=(220, 60, 50))
    d.line([382, 126, 378, 138], fill=(200, 200, 210))
    d.line([384, 126, 380, 138], fill=(200, 200, 210))
    # mug
    d.rectangle([208, 140, 218, 152], fill=(240, 240, 240))
    d.rectangle([219, 143, 221, 148], fill=(240, 240, 240))
    d.rectangle([209, 141, 217, 142], fill=(110, 70, 50))
    # desk clock body
    d.rectangle([404, 136, 452, 152], fill=(24, 24, 30))
    if p["glow"]:
        a = np.asarray(img).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        cx, cy = sx + sw / 2, sy + sh / 2 + 30
        dist = np.sqrt(((xx - cx) / 1.25) ** 2 + (yy - cy) ** 2)
        dist = dist + (BAYER_FULL - 0.5) * 14
        k = np.zeros_like(dist)
        k[dist < 160] = 0.06
        k[dist < 115] = 0.12
        k[dist < 80] = 0.2
        glowc = np.array([110, 160, 255], np.float32)
        a = a * (1 - k[..., None]) + glowc * k[..., None] + a * k[..., None] * 0.4
        img = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    _bgc[key] = img
    return img.copy()


HAIR = (34, 30, 46)
HOOD = (88, 104, 142)
HOOD_D = (62, 74, 106)
SKIN = (236, 196, 166)


def draw_person(img, pose="type", t=0.0, tod="night", k=0.0):
    """back view of '我' sitting at desk. k: interpolation param for transitions (0..1)."""
    p = ROOM_PAL[tod]
    d = dr(img)
    cx = 200
    breath = int(round(math.sin(t * 1.6) * 1)) if pose == "sleep" else 0
    if pose in ("type", "sit", "shock", "wake", "stretch", "nod"):
        hy = 98
        if pose == "nod":
            hy = 98 + int(lerp(0, 26, k))
        # torso
        d.polygon([(cx - 28, 124 + breath), (cx + 28, 124 + breath), (cx + 32, 176), (cx - 32, 176)], fill=HOOD)
        d.polygon([(cx - 28, 124 + breath), (cx - 10, 124 + breath), (cx - 14, 176), (cx - 32, 176)], fill=HOOD_D)
        # hood
        d.ellipse([cx - 16, 112 + breath, cx + 16, 128 + breath], fill=HOOD_D)
        # arms
        if pose in ("type", "sit", "nod"):
            j = (int(t * 10) % 2) if pose == "type" else 0
            d.polygon([(cx + 18, 128), (cx + 28, 128), (cx + 66, 150 - j), (cx + 58, 154)], fill=HOOD)
            d.polygon([(cx - 26, 130), (cx - 16, 130), (cx + 54, 152 + j), (cx + 48, 156)], fill=HOOD_D)
            d.rectangle([cx + 60, 148 - j, cx + 66, 152 - j], fill=SKIN)
            d.rectangle([cx + 50, 150 + j, cx + 56, 154 + j], fill=SKIN)
        elif pose == "stretch":
            d.polygon([(cx + 16, 126), (cx + 26, 128), (cx + 40, 78), (cx + 32, 76)], fill=HOOD)
            d.polygon([(cx - 16, 126), (cx - 26, 128), (cx - 40, 78), (cx - 32, 76)], fill=HOOD_D)
            d.rectangle([cx + 32, 70, cx + 40, 77], fill=SKIN)
            d.rectangle([cx - 40, 70, cx - 32, 77], fill=SKIN)
        elif pose in ("shock", "wake"):
            d.polygon([(cx + 18, 128), (cx + 28, 128), (cx + 44, 150), (cx + 36, 154)], fill=HOOD)
            d.polygon([(cx - 26, 130), (cx - 16, 130), (cx + 30, 152), (cx + 24, 156)], fill=HOOD_D)
        # head
        d.ellipse([cx - 15, hy - 15, cx + 15, hy + 15], fill=HAIR)
        d.rectangle([cx - 17, hy - 1, cx - 14, hy + 5], fill=SKIN)
        d.rectangle([cx + 14, hy - 1, cx + 17, hy + 5], fill=SKIN)
        d.line([cx - 6, hy - 12, cx + 4, hy - 13], fill=(60, 54, 76))
        if pose == "shock":
            for i in range(3):
                d.line([cx - 22 - i * 4, hy - 20 + i, cx - 26 - i * 4, hy - 26 + i], fill=(255, 255, 255))
                d.line([cx + 22 + i * 4, hy - 20 + i, cx + 26 + i * 4, hy - 26 + i], fill=(255, 255, 255))
    elif pose == "sleep":
        d.polygon([(cx - 28, 130 + breath), (cx + 28, 128 + breath), (cx + 32, 176), (cx - 32, 176)], fill=HOOD)
        d.polygon([(cx - 28, 130 + breath), (cx - 10, 129 + breath), (cx - 14, 176), (cx - 32, 176)], fill=HOOD_D)
        # folded arms on desk
        d.rectangle([cx - 30, 142, cx + 52, 154], fill=HOOD_D)
        d.rectangle([cx - 26, 140, cx + 48, 146], fill=HOOD)
        d.ellipse([cx - 14, 120 + breath, cx + 16, 146 + breath], fill=HAIR)
        d.rectangle([cx + 14, 132 + breath, cx + 17, 137 + breath], fill=SKIN)
    # chair back
    cy0 = 150
    d.rectangle([cx - 34, cy0, cx + 34, cy0 + 50], fill=p["chair"])
    d.rectangle([cx - 32, cy0 + 2, cx + 32, cy0 + 4], fill=p["chair_l"])
    d.rectangle([cx - 3, cy0 + 50, cx + 3, 236], fill=p["chair"])
    d.rectangle([cx - 30, 236, cx + 30, 240], fill=p["chair"])
    for wxp in (cx - 30, cx, cx + 30):
        d.rectangle([wxp - 3, 240, wxp + 3, 244], fill=(20, 20, 26))


def desk_clock(img, s, col=(255, 70, 60), blink=False, t=0):
    if blink and int(t * 4) % 2 == 0:
        return
    text(img, 428, 138, s, col, anchor="c")


def pc_rgb(img, t):
    d = dr(img)
    for i in range(6):
        hue = (t * 0.4 + i / 6) % 1
        c = hsv(hue, 0.8, 1)
        d.rectangle([416, 186 + i * 7, 418, 190 + i * 7], fill=c)
    d.rectangle([440, 186, 446, 192], fill=(30, 200, 255) if int(t * 2) % 2 else (20, 120, 180))


def hsv(h, s, v):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def code_screen(img, t, speed=1.0, rect=SCREEN):
    """scrolling code on the room monitor"""
    sx, sy, sw, sh = rect
    d = dr(img)
    d.rectangle([sx, sy, sx + sw - 1, sy + sh - 1], fill=(24, 26, 38))
    r = random.Random(11)
    scroll = int(t * 6 * speed)
    cols = [(198, 120, 221), (97, 175, 239), (152, 195, 121), (229, 192, 123), (224, 108, 117), (171, 178, 191)]
    for i in range(sh // 4):
        li = i + scroll
        rr = random.Random(li * 7 + 3)
        x = sx + 3 + rr.randint(0, 3) * 4
        y = sy + 2 + i * 4
        for _ in range(rr.randint(1, 4)):
            ln = rr.randint(4, 18)
            if x + ln > sx + sw - 3:
                break
            d.line([x, y, x + ln, y], fill=cols[rr.randint(0, 5)])
            x += ln + 3
