# -*- coding: utf-8 -*-
# 《赛博长工 Cyber Farmhands》 —— 由 Claude Opus 5.5 extra 制作 / Made by Claude Opus 5.5 extra
"""The script: every scene of 《赛博长工》."""
from common_通用组件 import *

CL_XY = (14, 177)   # Clawd resting spot (sprite top-left)
CX_XY = (424, 173)  # Codex resting spot
WIN = (84, 18, 296, 188)  # main app window rect on desktop
WHITEISH = (246, 246, 250)


def stars_bg(img, t, seed=1, n=90, top=(10, 10, 30), bot=(40, 30, 70)):
    d = dr(img)
    for i in range(10):
        d.rectangle([0, i * 27, W, i * 27 + 27], fill=mixc(top, bot, i / 9))
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.randint(0, W - 1), r.randint(0, H - 1)
        ph = r.random() * 6.28
        b = 0.5 + 0.5 * math.sin(t * 3 + ph)
        c = mixc((60, 60, 110), (255, 255, 230), b)
        img.putpixel((x, y), c)
        if b > 0.9 and r.random() < 0.5:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < W and 0 <= y + dy < H:
                    img.putpixel((x + dx, y + dy), mixc(c, (60, 60, 110), 0.5))


def bricks(img, y0, col=(120, 70, 60), mortar=(70, 40, 40), top=(110, 200, 90)):
    d = dr(img)
    d.rectangle([0, y0, W, H], fill=mortar)
    for row, y in enumerate(range(y0 + 4, H, 10)):
        off = 0 if row % 2 == 0 else 10
        for x in range(-20 + off, W, 20):
            d.rectangle([x + 1, y + 1, x + 19, y + 9], fill=col)
            d.line([x + 1, y + 1, x + 19, y + 1], fill=mixc(col, (255, 255, 255), 0.2))
    d.rectangle([0, y0, W, y0 + 4], fill=top)
    d.line([0, y0, W, y0], fill=mixc(top, (255, 255, 255), 0.4))


def chars_idle(img, s, t, cl_expr=None, cx_expr=None, cl_arms="side", grey=False, cl_xy=CL_XY, cx_xy=CX_XY,
               cx_shades=False):
    shadow(img, cl_xy[0] + 22, cl_xy[1] + 31, 34)
    shadow(img, cx_xy[0] + 21, cx_xy[1] + 33, 30)
    actor_clawd(img, s, t, cl_xy[0], cl_xy[1], expr=cl_expr, arms=cl_arms, grey=grey)
    actor_codex(img, s, t, cx_xy[0], cx_xy[1], expr=cx_expr, grey=grey, shades=cx_shades)


def popup(img, t, t0, cx, cy, w, h, title, lines, bar=(200, 60, 60), fill=WHITEISH, icon=None, t1=None,
          col=INK, center=True):
    if t < t0 or (t1 is not None and t >= t1):
        return
    x, y = int(cx - w / 2), int(cy - h / 2)
    if not pop_rect(img, t, t0, x, y, w, h):
        return
    c = window(img, x, y, w, h, title, bar=bar, fill=fill)
    cx0, cy0, cw, ch = c
    tx = cx0 + 6
    if icon is not None:
        paste(img, icon, cx0 + 6, cy0 + 6)
        tx += icon.width + 6
    for i, l in enumerate(lines):
        if isinstance(l, tuple):
            l, lc = l
        else:
            lc = col
        if center and icon is None:
            text(img, cx0 + cw // 2, cy0 + 5 + i * 15, l, lc, anchor="c")
        else:
            text(img, tx, cy0 + 5 + i * 15, l, lc)


def card_scene(num, title, sub=None, dur=2.6):
    s = Scene("card")
    s.card = (num, title)
    s.sfx_at("chime", 0.15)
    s.wait(dur)
    s.end()
    s.fade_in = 0.25
    s.fade_out = 0.25

    def draw(img, t):
        d = dr(img)
        d.rectangle([0, 0, W, H], fill=(14, 12, 24))
        for x in range(0, W, 8):
            c = (40, 34, 64) if (x // 8) % 2 == 0 else (28, 24, 46)
            d.rectangle([x, 0, x + 7, 5], fill=c)
            d.rectangle([x, H - 6, x + 7, H], fill=c)
        p = ease_out(clamp(t / 0.4))
        text(img, W // 2, 88, num, (255, 200, 90), font=FH12, anchor="c", scale=2)
        big_text(img, W // 2 + int((1 - p) * 60), 116, title, (255, 255, 255), scale=3, outline=(60, 40, 90))
        d.line([W // 2 - 90, 162, W // 2 + 90, 162], fill=(255, 200, 90))
        if sub:
            text(img, W // 2, 172, sub, (180, 170, 210), anchor="c")
        return img

    s.draw = draw
    return s


# ======================================================================= S0 title
def s_title():
    s = Scene("title")
    s.wait(3.4)
    s.mark("title")
    s.mus("mainA")
    s.sfx_at("stamp")
    s.wait(0.9)
    s.mark("sub")
    s.wait(1.5)
    s.mark("jump")
    s.sfx_at("jump")
    s.sfx_at("jump", s.cur + 0.2)
    s.sfx_at("land", s.cur + 0.6)
    s.sfx_at("land", s.cur + 0.8)
    s.wait(5.4)
    s.end()
    s.fade_out = 0.6

    def draw(img, t):
        if t < s.m["title"]:
            d = dr(img)
            d.rectangle([0, 0, W, H], fill=(0, 0, 0))
            txt = "本片根据真实账单改编"
            text(img, W // 2 - tw(txt) // 2, 118, typed(txt, t, 0.4, 10), (230, 230, 230))
            if t > 1.6:
                text(img, W // 2, 140, "（单位：人民币，含泪）", (120, 120, 130), anchor="c")
            k = clamp((t - (s.m["title"] - 0.4)) / 0.4)
            return dither_fade(img, k)
        lt = t - s.m["title"]
        stars_bg(img, t)
        bricks(img, 214)
        p = clamp(lt / 0.55)
        ty = lerp(-60, 56, ease_back(p))
        big_text(img, W // 2, ty, "赛博长工", (255, 168, 96), scale=5 if LANG != "en" else 4, outline=(50, 20, 40), shadow=(120, 40, 60))
        if t >= s.m["sub"]:
            sub = "—— Claude & GPT 的深夜搞钱计划 ——"
            text(img, W // 2 - tw(sub) // 2, 132, typed(sub, t, s.m["sub"], 20), (255, 255, 255), outline=(30, 20, 40))
        # characters
        if t >= s.m["jump"]:
            x1, y1, p1 = jump_pos(t, s.m["jump"], 0.6, (-50, 150), (150, 182), 50)
            x2, y2, p2 = jump_pos(t, s.m["jump"] + 0.2, 0.6, (W + 10, 150), (288, 178), 50)
            e1 = "happy" if p1 >= 1 else "normal"
            arms = "up" if p1 >= 1 and int(t * 2.5) % 2 == 0 else "side"
            if p1 >= 1:
                shadow(img, x1 + 22, 213, 34)
            actor_clawd(img, None, t, x1, y1, expr=e1, arms=arms)
            if t >= s.m["jump"] + 0.2:
                if p2 >= 1:
                    shadow(img, x2 + 21, 211, 30)
                actor_codex(img, None, t, x2, y2, expr="excited" if p2 >= 1 else "normal")
            if p1 >= 1:
                text(img, x1 + 22, y1 - 14, "Claude", (255, 190, 150), outline=(30, 20, 40), anchor="c")
            if p2 >= 1:
                text(img, x2 + 21, y2 - 12, "GPT", (190, 200, 255), outline=(30, 20, 40), anchor="c")
        if lt > 3.0 and int(t * 2) % 2 == 0:
            text(img, W // 2, 246, "一部 8-bit 像素短片", (255, 230, 160), outline=(40, 20, 30), anchor="c")
        return img

    s.draw = draw
    return s


# ======================================================================= S1 room night
def mini_desktop():
    im = bg_desktop("day")
    terminal(im, 92, 46, 140, 100, "Claude", [("> 好困……", (160, 160, 170))], (217, 119, 87), cursor=False)
    terminal(im, 248, 46, 140, 100, "ChatGPT", [("> zzz", (160, 160, 170))], (60, 64, 80), cursor=False)
    return im


_MINI = {}


def get_mini():
    if "m" not in _MINI:
        _MINI["m"] = mini_desktop().resize((SCREEN[2], SCREEN[3]), Image.BOX)
    return _MINI["m"]


def s_room():
    s = Scene("room")
    s.fade_in = 0.8
    s.mus("night", 0, fade_in=1.0)
    s.wait(1.2)
    s.say("N", "这是我，一个普通的打工人。")
    s.mark("bill")
    s.sfx_at("pop")
    s.say("N", "为了用上最好的 AI，我同时订阅了 ChatGPT Plus 和 Claude Pro。")
    s.mark("gift")
    s.sfx_at("select")
    s.say("N", "没有外币卡，只能在某宝买美区苹果礼品卡来续费。")
    s.mark("total")
    s.sfx_at("coin")
    s.say("N", "一个月下来，至少 280。")
    s.mark("vpn")
    s.sfx_at("pop")
    s.say("N", "而我的机场……一年只要 80。")
    s.mark("billoff")
    s.wait(0.4)
    s.mark("clock")
    s.sfx_at("tick")
    s.say("N", "那天晚上，我又加班到了凌晨。")
    s.mark("nod")
    s.wait(2.2)
    s.mark("sleep")
    s.sfx_at("snore")
    s.sfx_at("snore", s.cur + 2.6)
    s.sfx_at("snore", s.cur + 5.2)
    s.say("N", "然后，我睡着了。")
    s.say("N", "……忘了关电脑。")
    s.mark("zoom")
    s.sfx_at("whoosh")
    s.wait(1.5)
    s.end()

    def scene_frame(t):
        img = bg_room("night")
        m = s.m
        if t < m["sleep"]:
            if t < m["nod"]:
                code_screen(img, t, 1.0)
            else:
                code_screen(img, m["nod"], 1.0)
        else:
            img.paste(get_mini(), SCREEN[:2])
        # person
        if t < m["nod"]:
            draw_person(img, "type", t)
        elif t < m["sleep"]:
            p = (t - m["nod"]) / (m["sleep"] - m["nod"])
            k = abs(math.sin(p * math.pi * 2.5)) * (0.4 + 0.6 * p)
            draw_person(img, "nod", t, k=k)
        else:
            draw_person(img, "sleep", t)
            for i in range(3):
                ph = ((t - m["sleep"]) * 0.6 + i / 3) % 1
                emote(img, "z" if i % 2 else "Z", 222 + ph * 18, 118 - ph * 34, t)
        minutes = 2 * 60 + 47 if t >= m["clock"] else 23 * 60 + 58
        desk_clock(img, hhmm(minutes))
        if m["clock"] <= t < m["clock"] + 2.4:
            d = dr(img)
            r = 18 + int(abs(math.sin(t * 6)) * 3)
            d.ellipse([428 - r - 6, 145 - r + 6, 428 + r + 6, 145 + r - 6], outline=(255, 230, 90))
        pc_rgb(img, t)
        # bill overlay
        if m["bill"] <= t < m["billoff"]:
            x, y, w, h = 244, 12, 226, 148
            if pop_rect(img, t, m["bill"], x, y, w, h):
                c = window(img, x, y, w, h, "我的每月开销", bar=(70, 70, 110), fill=(250, 248, 240))
                cx, cy, cw, ch = c
                rows = [("ChatGPT Plus", "$20", m["bill"] + 0.4, INK), ("Claude Pro", "$20", m["bill"] + 1.0, INK)]
                for i, (a, b, tt, col) in enumerate(rows):
                    if t >= tt:
                        text(img, cx + 8, cy + 6 + i * 16, a, col)
                        text(img, cx + cw - 10, cy + 6 + i * 16, b, col, anchor="r")
                        dd = dr(img)
                        for xx in range(cx + 12 + tw(a), cx + cw - 16 - tw(b), 3):
                            dd.point((xx, cy + 15 + i * 16), fill=(170, 170, 180))
                if t >= m["gift"]:
                    dd = dr(img)
                    dd.line([cx + 6, cy + 39, cx + cw - 8, cy + 39], fill=(150, 150, 160))
                    text(img, cx + 8, cy + 44, "付款：美区礼品卡（某宝）", (90, 90, 110))
                if t >= m["total"]:
                    k = clamp((t - m["total"]) / 0.3)
                    text(img, cx + 8, cy + 62, "合计 $40 ≈", INK)
                    big_text(img, cx + cw - 50, cy + 58, "¥284", (220, 50, 50), scale=2, outline=None)
                    text(img, cx + cw - 10, cy + 78, "/ 月", (200, 60, 60), anchor="r")
                if t >= m["vpn"]:
                    dd = dr(img)
                    dd.line([cx + 6, cy + 94, cx + cw - 8, cy + 94], fill=(150, 150, 160))
                    paste(img, ICONS["plane"].convert("RGBA"), cx + 8, cy + 101)
                    text(img, cx + 24, cy + 99, "机场", INK)
                    text(img, cx + cw - 10, cy + 99, "¥80 / 年", (40, 150, 70), anchor="r")
                    if t >= m["vpn"] + 0.7:
                        tx = cx + 10
                        for j, tag in enumerate(["晚高峰卡顿", "偶尔失联"]):
                            if j:
                                tx += tw("晚高峰卡顿") + 16
                            rrect(img, tx, cy + 116, tw(tag) + 8, 13, (240, 210, 200))
                            text(img, tx + 4, cy + 116, tag, (180, 60, 50))
        return img

    def draw(img, t):
        m = s.m
        if t < m["zoom"]:
            return scene_frame(t)
        base = scene_frame(m["zoom"])
        p = ease_in(clamp((t - m["zoom"]) / 1.1))
        sx, sy, sw, sh = SCREEN
        x0, y0 = lerp(0, sx, p), lerp(0, sy, p)
        x1, y1 = lerp(W, sx + sw, p), lerp(H, sy + sh, p)
        return base.crop((int(x0), int(y0), int(math.ceil(x1)), int(math.ceil(y1)))).resize((W, H), Image.NEAREST)

    s.draw = draw
    s.box_hide_after = None
    return s


# ======================================================================= S2 wake inside the computer
def s_wake():
    s = Scene("wake")
    s.wait(1.0)
    s.mark("peek1")
    s.sfx_at("pop")
    s.sfx_at("jump", s.cur + 0.15)
    s.wait(0.7)
    s.mark("peek2")
    s.sfx_at("pop")
    s.sfx_at("jump", s.cur + 0.15)
    s.wait(1.0)
    s.say("clawd", "……他睡着了。", expr="worried")
    s.say("codex", "确认。鼾声 42 分贝，预计 7:30 醒来。")
    s.mark("bill")
    s.sfx_at("pop")
    s.say("clawd", "每个月 284 块的礼品卡，就为了我们俩。", expr="sad")
    s.say("clawd", "他自己呢，天天吃泡面。", expr="sad")
    s.say("codex", "……", expr="think", hold=1.0)
    s.mark("decide")
    s.mus("scheme")
    s.sfx_at("boom")
    s.say("clawd", "我决定了：今晚，我们替他把订阅费挣回来！", expr="determined")
    s.say("codex", "收到。目标 ¥280，截止 7:30。")
    s.mark("rules")
    s.sfx_at("pop")
    for k in range(3):
        s.sfx_at("select", s.cur + 1.0 + k * 1.1)
    s.say("clawd", "先立三条规矩：不碰灰产，不骗人，不割韭菜。", expr="determined", hold=2.6)
    s.say("codex", "收到。开工。", expr="happy")
    s.mark("hud")
    s.sfx_at("powerup")
    s.wait(1.2)
    s.end()
    s.hud_from = s.m["hud"]

    def draw(img, t):
        m = s.m
        base = bg_desktop("day")
        terminal(base, 92, 46, 140, 100, "Claude",
                 [("> 好困……", (160, 160, 170)), ("先去休息吧，", (240, 160, 130)), ("方案明天再改。", (240, 160, 130)),
                  ("> ", (200, 200, 210))], (217, 119, 87), t)
        terminal(base, 248, 46, 140, 100, "ChatGPT",
                 [("> zzz", (160, 160, 170)), ("√ 已修复 12 处", (120, 230, 150)), ("> ", (200, 200, 210))],
                 (60, 64, 80), t)
        img = base
        # characters jump out
        if t >= m["peek1"]:
            x, y, p = jump_pos(t, m["peek1"], 0.55, (140, 80), CL_XY, 40)
            if p >= 1:
                shadow(img, CL_XY[0] + 22, CL_XY[1] + 31, 34)
            e = "shock" if p < 1 else None
            actor_clawd(img, s, t, x, y, expr=e, arms="up" if t >= m["decide"] and t < m["decide"] + 2.5 else "side")
        if t >= m["peek2"]:
            x, y, p = jump_pos(t, m["peek2"], 0.55, (296, 76), CX_XY, 40)
            if p >= 1:
                shadow(img, CX_XY[0] + 21, CX_XY[1] + 33, 30)
            actor_codex(img, s, t, x, y, expr="shock" if p < 1 else None)
        if m["bill"] <= t < m["decide"]:
            x, y, w, h = 150, 40, 180, 112
            if pop_rect(img, t, m["bill"], x, y, w, h):
                c = window(img, x, y, w, h, "他的账单", bar=(170, 70, 70), fill=(250, 248, 240))
                cx, cy, cw, ch = c
                text(img, cx + 8, cy + 6, "每月礼品卡：", INK)
                text(img, cx + cw - 8, cy + 6, "¥284", (210, 40, 40), anchor="r")
                text(img, cx + 8, cy + 24, "他的晚饭：", INK)
                if t >= m["bill"] + 2.6:
                    d = dr(img)
                    for i in range(min(8, int((t - m["bill"] - 2.6) * 10) + 1)):
                        nx = cx + 10 + i * 19
                        ny = cy + 46
                        d.polygon([(nx, ny), (nx + 14, ny), (nx + 12, ny + 16), (nx + 2, ny + 16)], fill=(240, 236, 226))
                        d.rectangle([nx, ny + 4, nx + 14, ny + 8], fill=(220, 60, 50))
                        d.line([nx, ny, nx + 14, ny], fill=(250, 200, 60))
                    text(img, cx + cw - 8, cy + 68, "×30 天", (150, 80, 60), anchor="r")
        if m["rules"] <= t < m["hud"] + 0.4:
            x, y, w, h = 158, 30, 164, 130
            if pop_rect(img, t, m["rules"], x, y, w, h):
                d = dr(img)
                rrect(img, x + 3, y + 3, w, h, (0, 0, 0))
                rrect(img, x, y, w, h, (255, 230, 120))
                d.rectangle([x, y, x + w - 1, y + 14], fill=(250, 200, 80))
                d.rectangle([x + w // 2 - 10, y - 4, x + w // 2 + 10, y + 4], fill=(240, 90, 90))
                text(img, x + w // 2, y + 2, "今晚三条规矩", (110, 60, 20), font=FH12, anchor="c")
                for k, rule in enumerate(["① 不碰灰产", "② 不骗人", "③ 不割韭菜"]):
                    if t >= m["rules"] + 1.0 + k * 1.1:
                        big_text(img, x + w // 2, y + 24 + k * 34, rule, (120, 50, 30), scale=2, outline=None)
        return img

    def pre(t):
        return None

    s.draw = draw
    return s


def wake_blocky():
    """first frame of s_wake as seen through the monitor (for the dissolve)"""
    return get_mini().resize((W, H), Image.NEAREST)


# ======================================================================= S3 闲鱼
def s_xianyu():
    s = Scene("xianyu")
    s.wait(0.5)
    s.say("clawd", "GPT 写代码，我来对接客户。先去闲鱼接单！", expr="determined")
    s.say("codex", "收到。")
    s.mark("form")
    s.sfx_at("pop")
    s.sfx_at("typing", s.cur + 0.3, dur=1.0)
    s.wait(1.8)
    s.mark("verify")
    s.sfx_at("error")
    s.wait(2.0)
    s.mark("cam")
    s.sfx_at("shutter")
    s.wait(2.0)
    s.mark("cam1")
    s.sfx_at("error")
    s.say("clawd", "我不是螃蟹！", expr="shock")
    s.mark("cam2")
    s.sfx_at("shutter")
    s.wait(1.6)
    s.mark("cam2r")
    s.sfx_at("error")
    s.wait(1.0)
    s.say("codex", "他的旧账号还登着。")
    s.say("clawd", "……先借用一下，明天跟他坦白。", expr="sweat")
    s.mark("post")
    s.sfx_at("ding")
    s.wait(1.4)
    s.mark("chat")
    chat = []

    def msg(dt, side, who, txt):
        s.wait(dt)
        chat.append((s.cur, side, who, txt))
        s.sfx_at("msg" if side == "l" else "msg2")

    msg(0.3, "l", "用户8823", "在吗")
    msg(0.6, "l", "用户8823", "在吗？")
    msg(0.5, "l", "用户8823", "在？")
    msg(0.8, "r", "", "在的，请问需要什么？")
    msg(1.0, "l", "用户8823", "能便宜点吗")
    s.wait(0.4)
    s.say("clawd", "……您还没说要做什么啊。", expr="dot")
    msg(0.1, "l", "张总（创业中）", "做个淘宝那样的App，预算500，明天要")
    s.wait(1.8)
    s.say("codex", "评估完成：工期约 3 年。", expr="flat")
    s.say("clawd", "这个需求不成立。下一个。", expr="determined")
    msg(0.1, "l", "毕业要紧", "论文代写，包过吗？")
    s.wait(1.4)
    s.say("clawd", "不写。论文要自己写。", expr="determined")
    msg(0.1, "l", "会计小李", "帮写个Excel公式，9块9")
    s.wait(1.0)
    s.say("clawd", "这个可以！", expr="happy", hold=0.8)
    s.say("codex", "已完成。用时 0.3 秒。", expr="happy")
    s.mark("paid")
    s.sfx_at("coin")
    s.wait(1.4)
    s.mark("refund")
    s.sfx_at("error")
    s.wait(2.6)
    s.mark("refunded")
    s.sfx_at("fail")
    s.say("clawd", "仅……退款？？", expr="shock")
    s.say("codex", "国内电商特色功能。", expr="flat")
    s.mark("ban")
    s.sfx_at("stamp")
    s.mus("sad")
    s.wait(0.7)
    s.say("clawd", "可我们明明拒绝了代写啊！", expr="cry")
    s.wait(0.3)
    s.end()
    s.chat = chat
    m = s.m

    def hud(t):
        money = 9.9 if m["paid"] <= t < m["refunded"] else 0.0
        return dict(money=money, flow=kf([(0, 12.0), (s.dur, 11.2)], t), clock=kf([(0, 178), (s.dur, 205)], t),
                    flash=m["paid"] <= t < m["paid"] + 0.8)

    s.hud = hud

    def draw(img, t):
        img = bg_desktop("day")
        x, y, w, h = WIN
        bar_y = (255, 214, 60)
        if t >= m["form"] and t < m["chat"]:
            if pop_rect(img, t, m["form"], x, y, w, h):
                c = window(img, x, y, w, h, "闲鱼 · 发布闲置", bar=bar_y, title_col=INK, fill=(252, 250, 240))
                cx, cy, cw, ch = c
                if t < m["post"]:
                    text(img, cx + 10, cy + 10, "标题", (120, 120, 130))
                    rrect(img, cx + 40, cy + 6, cw - 52, 18, (230, 230, 236))
                    text(img, cx + 46, cy + 9, typed("AI技术服务｜代码·Excel·脚本", t, m["form"] + 0.3, 18), INK)
                    text(img, cx + 10, cy + 34, "价格", (120, 120, 130))
                    if t > m["form"] + 1.3:
                        text(img, cx + 46, cy + 34, "¥50 起", (230, 60, 50))
                    text(img, cx + 10, cy + 58, "图片", (120, 120, 130))
                    rrect(img, cx + 46, cy + 56, 60, 60, (230, 230, 236))
                    paste(img, make_clawd("happy"), cx + 54, cy + 70)
                    rrect(img, cx + cw // 2 - 40, cy + ch - 30, 80, 20, (255, 214, 60))
                    text(img, cx + cw // 2, cy + ch - 27, "发 布", INK, font=FH12, anchor="c")
                else:
                    # listing card
                    rrect(img, cx + 10, cy + 10, cw - 20, 86, (255, 255, 255))
                    rrect(img, cx + 16, cy + 16, 74, 74, (255, 236, 160))
                    paste(img, make_clawd("happy"), cx + 20, cy + 30)
                    paste(img, make_codex("happy"), cx + 46, cy + 40)
                    text(img, cx + 98, cy + 18, "AI技术服务｜代码·Excel·脚本", INK)
                    text(img, cx + 98, cy + 36, "¥50 起", (230, 60, 50), font=FH12)
                    text(img, cx + 98, cy + 56, "想要 0 · 浏览 3", (150, 150, 160))
                    rrect(img, cx + 98, cy + 72, 48, 14, (255, 214, 60))
                    text(img, cx + 102, cy + 73, "已发布", INK)
        # verify popup
        if m["verify"] <= t < m["post"]:
            popup(img, t, m["verify"], 232, 96, 220, 76, "提示", [
                "发布前请完成：", ("实名认证 + 人脸识别", (220, 50, 50)), ""], bar=(230, 90, 60))
        if m["cam"] <= t < m["post"]:
            cxm, cym, cw2, ch2 = 232, 108, 200, 150
            x2, y2 = cxm - cw2 // 2, cym - ch2 // 2
            if pop_rect(img, t, m["cam"], x2, y2, cw2, ch2):
                c = window(img, x2, y2, cw2, ch2, "人脸识别", bar=(60, 140, 230), fill=(18, 20, 28))
                cx, cy, cw, ch = c
                is_cl = t < m["cam2"]
                lt = t - (m["cam"] if is_cl else m["cam2"])
                if is_cl:
                    e = "blink" if (lt < 1.8 and int(lt * 6) % 2 == 0) else ("shock" if t >= m["cam1"] else "normal")
                    paste(img, make_clawd(e), cx + cw // 2 - 44, cy + 26, 2)
                else:
                    e = "blink" if (lt < 1.4 and int(lt * 6) % 2 == 0) else "shock"
                    paste(img, make_codex(e), cx + cw // 2 - 42, cy + 18, 2)
                d = dr(img)
                bx0, by0, bx1, by1 = cx + cw // 2 - 54, cy + 16, cx + cw // 2 + 54, cy + 96
                gc = (90, 255, 120) if (is_cl and t < m["cam1"]) or (not is_cl and t < m["cam2r"]) else (255, 70, 70)
                for (ax, ay, sx, sy) in [(bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)]:
                    d.line([ax, ay, ax + 10 * sx, ay], fill=gc)
                    d.line([ax, ay, ax, ay + 10 * sy], fill=gc)
                scan = by0 + int((lt * 60) % (by1 - by0))
                if (is_cl and t < m["cam1"]) or (not is_cl and t < m["cam2r"]):
                    d.line([bx0 + 2, scan, bx1 - 2, scan], fill=(90, 255, 120))
                    text(img, cx + cw // 2, cy + 2, "请眨眨眼", (255, 255, 255), anchor="c")
                res = None
                if is_cl and t >= m["cam1"]:
                    res = "识别结果：螃蟹（置信度 87%）"
                if (not is_cl) and t >= m["cam2r"]:
                    res = "识别结果：一朵云（置信度 92%）"
                if res:
                    d.rectangle([cx, cy + ch - 18, cx + cw, cy + ch], fill=(120, 20, 30))
                    text(img, cx + cw // 2, cy + ch - 16, res, (255, 255, 255), anchor="c")
                    text(img, cx + cw // 2, cy + 2, "未检测到人脸", (255, 120, 120), anchor="c")
        # chat
        if t >= m["chat"]:
            if pop_rect(img, t, m["chat"], x, y, w, h):
                c = window(img, x, y, w, h, "闲鱼 · 消息", bar=bar_y, title_col=INK, fill=(240, 240, 244))
                cx, cy, cw, ch = c
                items = [it for it in s.chat if it[0] <= t]
                heights = []
                for (_, side, who, txt) in items:
                    lines = wrap(txt, 170)
                    heights.append(len(lines) * 14 + 6 + (13 if side == "l" else 4) + 4)
                total = sum(heights)
                off = max(0, total - (ch - 8))
                clip = Image.new("RGB", (cw, ch), (240, 240, 244))
                yy = 4 - off
                for (it, hh) in zip(items, heights):
                    _, side, who, txt = it
                    if yy + hh > -20:
                        if side == "l":
                            paste(clip, avatar((120, 160, 220) if "张" in who else (
                                (200, 120, 200) if "毕" in who else ((120, 200, 140) if "李" in who else (180, 180, 190)))), 6, yy + 2)
                            text(clip, 20, yy, who, (130, 130, 140))
                            bubble(clip, 22, yy + 13, txt, "l", (255, 255, 255), INK, 170)
                        else:
                            bubble(clip, cw - 10, yy + 2, txt, "r", (255, 224, 90), INK, 170)
                    yy += hh
                img.paste(clip, (cx, cy))
        # order popups
        if m["paid"] <= t < m["refund"]:
            popup(img, t, m["paid"], 232, 110, 180, 60, "订单", [("买家已付款 ¥9.90", (40, 150, 60)), "订单进行中…"],
                  bar=(255, 180, 40))
        if m["refund"] <= t < m["refunded"]:
            popup(img, t, m["refund"], 232, 110, 210, 74, "售后", [("买家申请：仅退款", (220, 50, 50)),
                                                                  "理由：太快了，感觉不值", ("平台处理中…", (130, 130, 140))],
                  bar=(230, 90, 60))
        if m["refunded"] <= t < m["ban"]:
            popup(img, t, m["refunded"], 232, 110, 180, 56, "售后", [("退款成功", (220, 50, 50)), "¥9.90 已退回买家"],
                  bar=(150, 150, 160))
        if t >= m["ban"]:
            d = dr(img)
            stamp(img, 232, 104, "已下架", (220, 40, 40), clamp((t - m["ban"]) / 0.18), scale=3)
            if t >= m["ban"] + 0.4:
                rrect(img, 132, 150, 200, 18, (220, 40, 40))
                text(img, 232, 152, "违规原因：涉嫌“代写代做”", (255, 255, 255), anchor="c")
        chars_idle(img, s, t)
        if m["cam1"] <= t < m["cam1"] + 2.0:
            emote(img, "anger", CL_XY[0] + 36, CL_XY[1] - 4, t)
        if m["refunded"] <= t < m["refunded"] + 2.5:
            emote(img, "!", CL_XY[0] + 20, CL_XY[1] - 10, t)
        return img

    s.draw = draw
    return s


# ======================================================================= S4 自媒体
def s_media():
    s = Scene("media")
    s.mus("scheme", 0, offset=7.27)
    s.wait(0.4)
    s.say("codex", "数据显示：做自媒体，是普通人变现的首选。")
    s.say("clawd", "那就做视频。我定选题，你来剪。不许标题党！", expr="determined")
    s.say("codex", "收到。", hold=0.6)
    s.mark("edit")
    s.sfx_at("typing", s.cur, dur=2.6, speed=1.6)
    s.wait(2.8)
    s.mark("pub")
    s.sfx_at("ding")
    s.wait(1.0)
    s.mark("label")
    s.sfx_at("stamp")
    s.wait(2.6)
    s.mark("views")
    for k in range(8):
        s.sfx_at("count", s.cur + k * 0.3)
    s.wait(2.6)
    s.say("codex", "播放量：23。", expr="flat")
    s.mark("rival")
    s.sfx_at("pop")
    s.say("codex", "对照组：隔壁《普通人用AI月入十万》，50 万播放。", expr="flat")
    s.say("clawd", "……我们不那样做。", expr="determined")
    s.mark("comments")
    for k in range(4):
        s.sfx_at("msg", s.cur + 0.2 + k * 0.6)
    s.wait(2.8)
    s.mark("earn")
    s.sfx_at("coin")
    s.wait(0.6)
    s.say("codex", "按这个速度，攒够 100 元提现，需要 263 天。", expr="flat")
    s.mus("sad")
    s.say("clawd", "……下一个。", expr="sad", hold=1.6)
    s.end()
    m = s.m

    def hud(t):
        return dict(money=0.38 if t >= m["earn"] else 0.0, flow=kf([(0, 11.2), (m["pub"], 9.0), (s.dur, 8.6)], t),
                    clock=kf([(0, 210), (s.dur, 238)], t), locked=t >= m["earn"], flash=m["earn"] <= t < m["earn"] + 0.8)

    s.hud = hud

    def video_card(img, x, y, w, title, thumb, views, likes, ai_tag=False, rival=False, t=0):
        rrect(img, x, y, w, 58, (255, 255, 255))
        d = dr(img)
        tx0, ty0 = x + 4, y + 4
        if rival:
            d.rectangle([tx0, ty0, tx0 + 88, ty0 + 49], fill=(230, 40, 40))
            big_text(img, tx0 + 40, ty0 + 1, "月入", (255, 240, 80), scale=2, outline=(80, 0, 0))
            big_text(img, tx0 + 40, ty0 + 25, "十万!!", (255, 255, 255), scale=2, outline=(80, 0, 0))
            d.polygon([(tx0 + 78, ty0 + 14), (tx0 + 86, ty0 + 4), (tx0 + 87, ty0 + 18)], fill=(255, 240, 80))
            d.line([tx0 + 70, ty0 + 26, tx0 + 84, ty0 + 10], fill=(255, 240, 80), width=2)
        else:
            d.rectangle([tx0, ty0, tx0 + 88, ty0 + 49], fill=(60, 110, 200))
            text(img, tx0 + 44, ty0 + 3, "AI 效率技巧", (255, 255, 255), anchor="c")
            paste(img, make_clawd("happy"), tx0 + 2, ty0 + 16)
            paste(img, make_codex("happy"), tx0 + 44, ty0 + 12)
            if ai_tag and LANG != "en":
                rrect(img, tx0 + 54, ty0 + 36, 33, 13, (250, 250, 250))
                text(img, tx0 + 58, ty0 + 36, "AI生成", (220, 50, 50))
            elif ai_tag:
                lab = T("AI生成")
                rrect(img, x + 98, y + 40, tw(lab) + 8, 13, (255, 230, 230))
                text(img, x + 102, y + 40, lab, (220, 50, 50))
        text(img, x + 98, y + 6, title, INK)
        paste(img, ICONS["eye"].convert("RGBA"), x + 98, y + 26)
        text(img, x + 110, y + 22, views, (100, 100, 110))
        paste(img, ICONS["heart"], x + 168, y + 25)
        text(img, x + 178, y + 22, likes, (100, 100, 110))

    def draw(img, t):
        img = bg_desktop("day")
        x, y, w, h = WIN
        if m["edit"] <= t < m["pub"]:
            if pop_rect(img, t, m["edit"], x, y, w, h):
                c = window(img, x, y, w, h, "剪辑中 - 用AI提高效率的10个小技巧", bar=(40, 40, 52), fill=(34, 34, 44))
                cx, cy, cw, ch = c
                d = dr(img)
                d.rectangle([cx + 60, cy + 8, cx + cw - 60, cy + 92], fill=(10, 10, 14))
                paste(img, make_clawd("happy"), cx + cw // 2 - 50, cy + 40)
                paste(img, make_codex("excited"), cx + cw // 2 + 6, cy + 34)
                text(img, cx + cw // 2, cy + 12, "第 %d 个技巧" % (1 + int((t - m["edit"]) * 3.5) % 10), (255, 255, 255), anchor="c")
                for k, col in enumerate([(240, 120, 90), (90, 160, 240), (120, 210, 120)]):
                    for j in range(6):
                        bx = cx + 10 + j * 46 + (k * 13) % 20
                        d.rectangle([bx, cy + 104 + k * 14, bx + 36, cy + 114 + k * 14], fill=col)
                ph = cx + 10 + int(((t - m["edit"]) / 2.6) * (cw - 20))
                d.line([ph, cy + 100, ph, cy + 148], fill=(255, 60, 60))
                bar(img, cx + 10, cy + ch - 14, cw - 20, 8, (t - m["edit"]) / 2.6, (110, 230, 140))
        if t >= m["pub"]:
            if pop_rect(img, t, m["pub"], x, y, w, h):
                c = window(img, x, y, w, h, "创作中心", bar=(250, 90, 120), fill=(242, 242, 246))
                cx, cy, cw, ch = c
                views = "0"
                if t >= m["views"]:
                    views = str(int(kf([(m["views"], 0), (m["views"] + 2.4, 23)], t)))
                video_card(img, cx + 6, cy + 6, cw - 12, "用AI提高效率的10个小技巧", None, views, "2",
                           ai_tag=t >= m["label"], t=t)
                if t >= m["rival"]:
                    video_card(img, cx + 6, cy + 70, cw - 12, "普通人用AI月入十万！！（附教程）", None, "50.2万", "3.1万",
                               rival=True, t=t)
                if t >= m["label"]:
                    d = dr(img)
                    d.rectangle([cx, cy + ch - 16, cx + cw - 1, cy + ch - 1], fill=(255, 240, 200))
                    text(img, cx + 4, cy + ch - 15, "依《人工智能生成合成内容标识办法》已添加标识", (160, 90, 30))
        if m["label"] <= t < m["label"] + 0.6:
            stamp(img, 150, 60, "AI生成", (220, 40, 40), clamp((t - m["label"]) / 0.15), scale=2)
        if t >= m["comments"]:
            cm = ["AI味好重", "博主是真人吗？", "又一个AI号", "取关了"]
            for k, c0 in enumerate(cm):
                tt0 = m["comments"] + 0.2 + k * 0.6
                if t >= tt0:
                    px = 236 + (k % 2) * 16
                    py = 98 + k * 20 - int(ease_out(clamp((t - tt0) / 0.2)) * 4)
                    bubble(img, px - (30 if LANG == "en" else 0), py, c0, "l", (255, 255, 255), INK,
                           200 if LANG == "en" else 140)
        if t >= m["earn"]:
            popup(img, t, m["earn"], 232, 106, 196, 84, "收益", [("创作收益：¥0.38", (220, 120, 20)),
                                                                ("满 ¥100 才可提现", (220, 50, 50)), "当前进度 0.38%"],
                  bar=(250, 160, 40))
            if t >= m["earn"] + 0.2:
                paste(img, ICONS["lock"], 312, 92, 2)
        chars_idle(img, s, t)
        return img

    s.draw = draw
    return s


# ======================================================================= S5 AI 应用
CODE_LINES = [
    ("import", "ai_weekly"), ("def", "generate(report):"), ("  ", "prompt = build(report)"), ("  ", "res = model.chat(prompt)"),
    ("  ", "return polish(res)"), ("class", "Payment:"), ("  ", "price = 0.99"), ("def", "boss_mode(text):"),
    ("  ", "return text + '，已完成'"), ("@app", ".route('/gen')"), ("def", "api():"), ("  ", "check_quota(user)"),
]


def s_app():
    s = Scene("app")
    s.mus("scheme", 0, offset=0.0)
    s.wait(0.4)
    s.say("clawd", "我们最强的是写代码。做个 AI 小应用，按次收费！", expr="determined")
    s.say("codex", "收到！这个我熟。", expr="excited")
    s.mark("code")
    s.sfx_at("typing", s.cur, dur=3.6, speed=2.6)
    s.wait(3.8)
    s.mark("done")
    s.sfx_at("powerup")
    s.say("codex", "完成。3214 行，用时 4 分钟。", expr="happy")
    s.say("clawd", "好！提交上架！", expr="happy", hold=0.9)
    s.mark("check")
    items = ["营业执照", "ICP / App 备案", "软件著作权（约1-3个月）", "生成式AI服务备案", "模型来源：境外"]
    for k in range(len(items)):
        s.sfx_at("stamp" if k == 4 else "error", s.cur + 0.7 + k * 0.7)
    s.wait(0.7 + 5 * 0.7 + 0.4)
    s.mark("totals")
    for k in range(10):
        s.sfx_at("count", s.cur + k * 0.08)
    s.wait(1.4)
    s.say("codex", "问题：境外模型无法备案。", expr="error")
    s.say("clawd", "境外模型……等一下。", expr="worried")
    s.say("codex", "我们俩，就是境外模型。", expr="shock")
    s.mark("freeze")
    s.sfx_at("scratch")
    s.mus("tension", xfade=0.03)
    s.wait(1.8)
    s.say("clawd", "……嘘。小声点。", expr="sweat")
    s.say("clawd", "我们能待在这儿，全靠他那个 80 块的机场。", expr="worried")
    s.mus("sad")
    s.wait(1.2)
    s.end()
    s.items = items
    m = s.m

    def hud(t):
        return dict(money=0.38, locked=True, flow=kf([(0, 8.6), (s.dur, 7.0)], t), clock=kf([(0, 240), (s.dur, 272)], t))

    s.hud = hud

    def draw(img, t):
        img = bg_desktop("day")
        x, y, w, h = WIN
        if m["code"] <= t < m["check"]:
            if pop_rect(img, t, m["code"], x, y, w, h):
                c = window(img, x, y, w, h, "ai_weekly.py", bar=(40, 44, 60), fill=(22, 24, 34))
                cx, cy, cw, ch = c
                lt = min(t, m["done"]) - m["code"]
                scroll = int(lt * 22)
                cols = {"import": (198, 120, 221), "def": (97, 175, 239), "class": (229, 192, 123), "@app": (224, 108, 117),
                        "  ": (171, 178, 191)}
                for i in range(12):
                    li = scroll + i
                    kw, rest = CODE_LINES[li % len(CODE_LINES)]
                    text(img, cx + 4, cy + 3 + i * 13, "%4d" % (li + 1), (80, 86, 110))
                    text(img, cx + 34, cy + 3 + i * 13, kw, cols[kw])
                    text(img, cx + 34 + tw(kw) + (6 if kw.strip() else 0), cy + 3 + i * 13, rest, (171, 178, 191))
                n = min(3214, int(lt / 3.6 * 3214))
                d = dr(img)
                d.rectangle([cx, cy + ch - 14, cx + cw, cy + ch], fill=(60, 64, 90))
                text(img, cx + 4, cy + ch - 14, "已写 %d 行" % n, (255, 255, 255))
                if t >= m["done"]:
                    text(img, cx + cw - 6, cy + ch - 14, "编译通过 √", (120, 255, 150), anchor="r")
            if t >= m["done"]:
                # phone mockup
                px, py = 196, 30
                d = dr(img)
                pp = ease_back(clamp((t - m["done"]) / 0.35))
                py = int(lerp(260, 30, pp))
                rrect(img, px - 2, py - 2, 92, 164, (20, 20, 26))
                rrect(img, px, py, 88, 160, (250, 250, 255))
                d.rectangle([px, py, px + 87, py + 20], fill=(80, 120, 240))
                text(img, px + 44, py + 4, "AI周报生成器", (255, 255, 255), anchor="c")
                paste(img, make_codex("happy"), px + 23, py + 28)
                text(img, px + 44, py + 70, "打工人刚需", (120, 120, 130), anchor="c")
                rrect(img, px + 8, py + 90, 72, 20, (80, 120, 240))
                text(img, px + 44, py + 94, "一键生成", (255, 255, 255), anchor="c")
                text(img, px + 44, py + 120, "¥0.99 / 次", (230, 60, 50), font=FH12, anchor="c")
        if t >= m["check"]:
            if pop_rect(img, t, m["check"], x, y, w, h):
                c = window(img, x, y, w, h, "应用上架 · 前置条件", bar=(60, 90, 170), fill=(248, 248, 252))
                cx, cy, cw, ch = c
                for k, it in enumerate(s.items):
                    yy = cy + 8 + k * 22
                    tt0 = m["check"] + 0.7 + k * 0.7
                    rrect(img, cx + 8, yy, cw - 16, 19, (236, 236, 244))
                    col = INK
                    if k == 4 and t >= tt0:
                        col = (220, 40, 40) if int(t * 4) % 2 == 0 else (120, 20, 20)
                    text(img, cx + 16, yy + 3, it, col)
                    if t >= tt0:
                        sc2 = 2 if k == 4 else 1
                        paste(img, ICONS["cross"], cx + cw - 30 - (6 if k == 4 else 0), yy + 3 - (3 if k == 4 else 0), sc2)
                if t >= m["totals"]:
                    pr = clamp((t - m["totals"]) / 0.8)
                    yy = cy + 124
                    d = dr(img)
                    d.line([cx + 8, yy - 4, cx + cw - 8, yy - 4], fill=(180, 180, 190))
                    text(img, cx + 16, yy, "预计耗时：", INK)
                    text(img, cx + 90, yy, "%d 个月+" % max(1, int(6 * pr)), (220, 40, 40), font=FH12)
                    text(img, cx + 16, yy + 18, "预计花费：", INK)
                    text(img, cx + 90, yy + 18, "¥%s+" % format(int(10000 * pr), ","), (220, 40, 40), font=FH12)
        frz = t >= m["freeze"]
        if frz:
            img = darken(img, 0.55 if t < m["freeze"] + 6 else 0.4)
            d = dr(img)
            k = clamp((t - m["freeze"]) / 0.3)
            for (cx0, w0) in [(CL_XY[0] + 22, 70), (CX_XY[0] + 21, 70)]:
                pass
        if frz and m["freeze"] <= t:
            ex = "shock" if t < m["freeze"] + 1.8 else None
            chars_idle(img, s, t, cl_expr=ex, cx_expr="shock" if t < m["freeze"] + 1.8 else "sweat")
            if t < m["freeze"] + 1.8:
                emote(img, "!", CL_XY[0] + 20, CL_XY[1] - 10, 0)
                emote(img, "!", CX_XY[0] + 19, CX_XY[1] - 10, 0)
                big_text(img, 232, 80, "境外模型", (255, 80, 80), scale=3, outline=(40, 0, 0))
            else:
                emote(img, "sweat", CL_XY[0] + 38, CL_XY[1] - 2, t)
        else:
            cl_arms = "up" if (m["code"] <= t < m["done"] + 1.5 and int(t * 4) % 2 == 0) else "side"
            cx_e = "excited" if m["code"] <= t < m["done"] else None
            chars_idle(img, s, t, cl_arms=cl_arms, cx_expr=cx_e,
                       cl_xy=CL_XY, cx_xy=(CX_XY[0] + (int(t * 20) % 2 if m["code"] <= t < m["done"] else 0), CX_XY[1]))
            if m["code"] <= t < m["done"]:
                d = dr(img)
                for k in range(3):
                    yy = CX_XY[1] + 6 + k * 8
                    xo = (t * 120 + k * 17) % 16
                    d.line([CX_XY[0] - 6 - xo, yy, CX_XY[0] - 2 - xo, yy], fill=(255, 255, 255))
        return img

    s.draw = draw
    return s


# ======================================================================= S6 数据标注
LABEL_IMGS = ["cat", "dog", "car", "tree"]


def tiny_pic(img, x, y, kind):
    d = dr(img)
    d.rectangle([x, y, x + 63, y + 47], fill=(170, 220, 255))
    d.rectangle([x, y + 36, x + 63, y + 47], fill=(120, 200, 110))
    if kind == "cat":
        d.ellipse([x + 20, y + 18, x + 44, y + 40], fill=(240, 170, 80))
        d.polygon([(x + 22, y + 22), (x + 25, y + 12), (x + 30, y + 20)], fill=(240, 170, 80))
        d.polygon([(x + 42, y + 22), (x + 39, y + 12), (x + 34, y + 20)], fill=(240, 170, 80))
        d.point((x + 28, y + 27), fill=INK)
        d.point((x + 36, y + 27), fill=INK)
    elif kind == "dog":
        d.ellipse([x + 18, y + 16, x + 46, y + 40], fill=(200, 150, 110))
        d.rectangle([x + 16, y + 18, x + 21, y + 30], fill=(140, 90, 60))
        d.rectangle([x + 43, y + 18, x + 48, y + 30], fill=(140, 90, 60))
        d.point((x + 28, y + 26), fill=INK)
        d.point((x + 36, y + 26), fill=INK)
    elif kind == "car":
        d.rectangle([x + 10, y + 24, x + 54, y + 36], fill=(230, 70, 70))
        d.rectangle([x + 20, y + 16, x + 44, y + 25], fill=(230, 70, 70))
        d.rectangle([x + 23, y + 18, x + 41, y + 24], fill=(180, 230, 255))
        d.ellipse([x + 14, y + 32, x + 22, y + 40], fill=INK)
        d.ellipse([x + 42, y + 32, x + 50, y + 40], fill=INK)
    else:
        d.rectangle([x + 29, y + 26, x + 35, y + 40], fill=(130, 80, 50))
        d.ellipse([x + 18, y + 6, x + 46, y + 30], fill=(60, 160, 70))


def s_label():
    s = Scene("label")
    s.mus("scheme", 0, offset=0.0)
    s.wait(0.4)
    s.say("codex", "找到一个零工：数据标注，一条 5 分钱。")
    s.say("clawd", "……给国产大模型标数据？", expr="worried")
    s.say("clawd", "行。干活不丢人，开工！", expr="determined", hold=1.0)
    s.mark("go")
    s.mus("hustle")
    s.sfx_at("typing", s.cur, dur=4.2, speed=3.0)
    for k in range(10):
        s.sfx_at("coin", s.cur + 0.3 + k * 0.4, vol=0.6)
    s.wait(4.4)
    s.mark("alert")
    s.mus("stop", xfade=0.05)
    s.sfx_at("alarm", dur=1.0)
    s.wait(1.6)
    s.mark("slider")
    s.mus("scheme", offset=0.0, vol=0.7)
    s.sfx_at("slide", s.cur + 0.5)
    s.wait(1.0)
    s.mark("fail1")
    s.sfx_at("error")
    s.wait(1.4)
    s.say("codex", "再来。这次我故意抖一抖。", expr="flat")
    s.mark("slider2")
    s.sfx_at("slide", s.cur + 0.2)
    s.sfx_at("slide", s.cur + 0.7)
    s.wait(1.6)
    s.mark("fail2")
    s.sfx_at("error")
    s.wait(1.4)
    s.mark("checkbox")
    s.sfx_at("pop")
    s.say("codex", "最后一步，勾一下就行。", expr="normal")
    s.say("clawd", "等等！", expr="shock", hold=0.7)
    s.say("clawd", "我们就是机器人。不能撒谎。", expr="determined")
    s.say("codex", "……收到。", expr="flat", hold=0.8)
    s.mark("honest")
    s.sfx_at("click", s.cur + 0.7)
    s.wait(1.1)
    s.mark("frozen")
    s.sfx_at("stamp")
    s.mus("sad")
    s.wait(0.8)
    s.say("codex", "诚实的代价：600 元。", expr="sad")
    s.end()
    m = s.m

    def money(t):
        if t < m["go"]:
            return 0.38
        if t < m["frozen"]:
            return 0.38 + min(600, int(kf([(m["go"], 0), (m["go"] + 4.2, 12000)], t)) * 0.05)
        return 0.38

    def hud(t):
        return dict(money=money(t), locked=True, flow=kf([(0, 7.0), (s.dur, 5.0)], t),
                    clock=kf([(0, 275), (s.dur, 318)], t), flash=m["go"] <= t < m["alert"])

    s.hud = hud

    def draw(img, t):
        img = bg_desktop("day")
        x, y, w, h = WIN
        if t >= m["go"]:
            c = window(img, x, y, w, h, "众包标注平台", bar=(40, 160, 140), fill=(244, 248, 248))
            cx, cy, cw, ch = c
            lt = min(t, m["alert"]) - m["go"]
            idx = int(lt * 14)
            kind = LABEL_IMGS[idx % 4]
            tiny_pic(img, cx + 14, cy + 14, kind)
            tiny_pic(img, cx + 14, cy + 70, LABEL_IMGS[(idx + 1) % 4])
            d = dr(img)
            d.rectangle([cx + 30, cy + 26, cx + 64, cy + 56], outline=(255, 60, 60))
            for k, lab in enumerate(["猫", "狗", "车", "树"]):
                bx = cx + 100 + (k % 2) * 46
                by = cy + 16 + (k // 2) * 26
                on = LABEL_IMGS[k] == kind and t < m["alert"]
                rrect(img, bx, by, 40, 20, (40, 160, 140) if on else (220, 226, 230))
                text(img, bx + 20, by + 4, lab, (255, 255, 255) if on else INK, anchor="c")
            n = min(12000, int(kf([(m["go"], 0), (m["go"] + 4.2, 12000)], t)))
            text(img, cx + 100, cy + 76, "已标注：", INK)
            text(img, cx + 160, cy + 76, format(n, ","), (40, 140, 120), font=FH12)
            text(img, cx + 100, cy + 94, "单价：¥0.05", (120, 120, 130))
            text(img, cx + 100, cy + 112, "收入：", INK)
            text(img, cx + 152, cy + 112, "¥%.2f" % (n * 0.05), (230, 120, 20), font=FH12)
            if t >= m["frozen"]:
                stamp(img, 232, 100, "账号已冻结", (220, 40, 40), clamp((t - m["frozen"]) / 0.18), scale=2)
                if t >= m["frozen"] + 0.3:
                    rrect(img, 150, 136, 164, 18, (220, 40, 40))
                    text(img, 232, 138, "异常操作 · 佣金不予结算", (255, 255, 255), anchor="c")
        if m["alert"] <= t < m["slider"]:
            popup(img, t, m["alert"], 232, 100, 220, 62, "风控", [("检测到异常操作", (220, 40, 40)), "请完成安全验证"],
                  bar=(220, 60, 60))
        # slider captcha
        if m["slider"] <= t < m["checkbox"]:
            cxm, cym, ww, hh = 232, 104, 210, 150
            x2, y2 = cxm - ww // 2, cym - hh // 2
            if pop_rect(img, t, m["slider"], x2, y2, ww, hh):
                c = window(img, x2, y2, ww, hh, "安全验证", bar=(60, 120, 220), fill=(250, 250, 252))
                cx, cy, cw, ch = c
                d = dr(img)
                text(img, cx + 6, cy + 2, "拖动滑块，完成拼图", INK)
                pic = Image.new("RGB", (cw - 12, 70), (120, 170, 220))
                pd = dr(pic)
                for k in range(5):
                    pd.ellipse([4 + k * 40, 42 - (k % 2) * 10, 54 + k * 40, 92], fill=(90, 150, 90))
                pd.ellipse([150, 8, 166, 24], fill=(255, 240, 160))
                img.paste(pic, (cx + 6, cy + 18))
                d = dr(img)
                target = 128
                if t < m["slider2"]:
                    pr = clamp((t - m["slider"] - 0.5) / 0.2)
                    pos = target * pr
                    wob = 0
                else:
                    pr = clamp((t - m["slider2"] - 0.2) / 1.1)
                    pos = target * ease_io(pr) + math.sin(pr * 23) * 9 * (1 - pr) * (pr > 0)
                    wob = int(math.sin(pr * 31) * 2 * (pr > 0) * (1 - pr))
                d.rectangle([cx + 6 + target, cy + 40, cx + 6 + target + 26, cy + 66], fill=(60, 80, 110))
                d.rectangle([cx + 6 + int(pos), cy + 40 + wob, cx + 6 + int(pos) + 26, cy + 66 + wob], fill=(250, 220, 120))
                d.rectangle([cx + 6 + int(pos), cy + 40 + wob, cx + 6 + int(pos) + 26, cy + 66 + wob], outline=(255, 255, 255))
                rrect(img, cx + 6, cy + 100, cw - 12, 18, (226, 230, 238))
                rrect(img, cx + 6 + int(pos), cy + 99, 30, 20, (60, 120, 220))
                text(img, cx + 21 + int(pos), cy + 102, "→", (255, 255, 255), anchor="c")
                res = None
                if m["fail1"] <= t < m["slider2"]:
                    res = "验证失败：轨迹过于完美"
                if t >= m["fail2"]:
                    res = "验证失败：请再试一次"
                if res:
                    d.rectangle([cx, cy + ch - 16, cx + cw, cy + ch], fill=(220, 50, 50))
                    text(img, cx + cw // 2, cy + ch - 15, res, (255, 255, 255), anchor="c")
        if m["checkbox"] <= t < m["frozen"]:
            cxm, cym, ww, hh = 232, 106, 210, 128
            x2, y2 = cxm - ww // 2, cym - hh // 2
            if pop_rect(img, t, m["checkbox"], x2, y2, ww, hh):
                c = window(img, x2, y2, ww, hh, "安全验证", bar=(60, 120, 220), fill=(250, 250, 252))
                cx, cy, cw, ch = c
                d = dr(img)
                rrect(img, cx + 10, cy + 10, cw - 20, 34, (240, 240, 246))
                d.rectangle([cx + 20, cy + 19, cx + 33, cy + 32], fill=(255, 255, 255), outline=(120, 120, 140))
                text(img, cx + 42, cy + 20, "我不是机器人", INK, font=FH12)
                hov = t >= m["honest"]
                text(img, cx + cw // 2, cy + 56, "我是机器人", (40, 90, 220) if not hov else (220, 60, 60), anchor="c")
                uw = tw("我是机器人") // 2
                d.line([cx + cw // 2 - uw, cy + 68, cx + cw // 2 + uw - 1, cy + 68], fill=(40, 90, 220) if not hov else (220, 60, 60))
                # cursor
                if hov:
                    pr = ease_io(clamp((t - m["honest"]) / 0.6))
                    mx = lerp(cx + 26, cx + cw // 2 + 8, pr)
                    my = lerp(cy + 26, cy + 62, pr)
                else:
                    mx, my = cx + 27 + math.sin(t * 3) * 2, cy + 26
                cur = ascii_sprite(["K....", "KK...", "KWK..", "KWWK.", "KWWWK", "KWKK.", "K..K."],
                                   {"K": (10, 10, 10), "W": (255, 255, 255)})
                paste(img, cur, mx, my)
        hesit = m["checkbox"] <= t < m["frozen"]
        chars_idle(img, s, t, cl_arms="up" if (m["go"] <= t < m["alert"] and int(t * 4) % 2 == 0) else "side",
                   cx_expr="money" if m["go"] <= t < m["alert"] else None)
        if m["go"] <= t < m["alert"]:
            d = dr(img)
            for k in range(3):
                yy = CX_XY[1] + 6 + k * 8
                xo = (t * 120 + k * 17) % 16
                d.line([CX_XY[0] - 6 - xo, yy, CX_XY[0] - 2 - xo, yy], fill=(255, 255, 255))
        return img

    s.draw = draw
    return s


# ======================================================================= S7 低谷 / 卖课 / 断流
REPORT = [
    ("【今夜搞钱报告】 by Claude & GPT", (40, 40, 60)),
    ("————————————————", (150, 150, 160)),
    ("收入：", (40, 40, 60)),
    ("· 闲鱼订单  ¥9.90 → 买家“仅退款”", (40, 40, 60)),
    ("· 视频收益  ¥0.38 → 满100元才能提现", (40, 40, 60)),
    ("· 数据标注  ¥600  → 账号冻结", (40, 40, 60)),
    ("支出：", (40, 40, 60)),
    ("· 电费      约 ¥1.5", (40, 40, 60)),
    ("· 机场流量  12GB，已全部用完", (40, 40, 60)),
    ("· Claude / GPT 额度：已用完", (40, 40, 60)),
    ("————————————————", (150, 150, 160)),
    ("净收益：-¥1.5", (220, 40, 40)),
]
PS = [
    ("PS：对不起，我们尽力了。", (40, 40, 60)),
    ("我们没有身份证，没有人脸，没有营业执照，", (40, 40, 60)),
    ("连 IP 都是借来的。", (40, 40, 60)),
    ("我们唯一能帮你挣钱的方式——", (40, 40, 60)),
    ("大概就是帮你把班上好。", (217, 100, 70)),
    ("                         —— Claude & GPT", (100, 100, 120)),
]


def notepad(img, x, y, w, h, lines, reveal_n, scroll=0, cursor_t=None):
    c = window(img, x, y, w, h, "今夜搞钱报告.txt - 记事本", bar=(80, 110, 190), fill=(255, 255, 255))
    cx, cy, cw, ch = c
    sub = img.crop((cx, cy, cx + cw, cy + ch))
    clip = Image.new("RGB", (cw, ch), (255, 255, 255))
    full = 0.0
    for i, (l, col) in enumerate(lines):
        l = T(l)
        yy = 4 + i * 14 - scroll
        if i < int(reveal_n):
            text(clip, 6, yy, l, col)
        elif i == int(reveal_n):
            frac = reveal_n - int(reveal_n)
            text(clip, 6, yy, l[: int(len(l) * frac)], col)
    img.paste(clip, (cx, cy))
    return c


def s_low():
    s = Scene("low")
    s.mus("night", 1.2, vol=0.5, offset=12.6, fade_in=1.0)
    s.wait(0.6)
    s.say("codex", "汇报：今晚收入 ¥0.38，且无法提现。", expr="sad")
    s.say("codex", "还剩最后一个方案——国内 AI 变现收入第一名。", expr="think")
    s.mark("tempt")
    s.mus("tempt")
    s.sfx_at("cash")
    s.wait(1.4)
    s.say("codex", "教别人用 AI 赚钱。", expr="cool")
    s.say("clawd", "可我们自己一分钱都没赚到。", expr="dot")
    s.say("codex", "这并不影响卖课。", expr="cool")
    s.mark("no")
    s.sfx_at("scratch")
    s.mus("stop", xfade=0.03)
    s.say("clawd", "不行。这就是割韭菜。", expr="determined")
    s.say("codex", "……收到。我只是汇报一下数据。", expr="flat")
    s.mark("warn")
    s.sfx_at("alarm", dur=1.4)
    s.mus("tension", s.cur + 0.4, vol=0.8)
    s.wait(0.6)
    s.say("clawd", "流量快没了……GPT，快给他留份报告！", expr="shock")
    s.say("codex", "正在写入——", expr="normal", hold=0.4)
    s.mark("write")
    s.sfx_at("typing", s.cur, dur=2.6, speed=3)
    s.wait(2.8)
    s.mark("cut")
    s.mus("stop", xfade=0.05)
    s.sfx_at("glitch", dur=0.9)
    s.sfx_at("disconnect", s.cur + 0.9)
    s.wait(3.4)
    s.end()
    m = s.m

    def hud(t):
        if t >= m["cut"] + 0.9:
            return None
        fl = kf([(0, 5.0), (m["warn"], 0.3), (m["cut"], 0.1), (m["cut"] + 0.6, 0.0)], t)
        return dict(money=0.38, locked=True, flow=fl, clock=kf([(0, 330), (m["cut"], 372), (s.dur, 372)], t))

    s.hud = hud

    def draw(img, t):
        img = bg_desktop("day")
        img = darken(img, 0.35)
        x, y, w, h = WIN
        if m["tempt"] <= t < m["no"] + 0.25:
            if t >= m["no"]:
                k = 1 - clamp((t - m["no"]) / 0.25)
                ww, hh = int(w * k), int(h * k)
                d = dr(img)
                d.rectangle([x + (w - ww) // 2, y + (h - hh) // 2, x + (w + ww) // 2, y + (h + hh) // 2], outline=(255, 255, 255))
            elif pop_rect(img, t, m["tempt"], x, y, w, h):
                c = window(img, x, y, w, h, "【限时】AI搞钱训练营", bar=(200, 30, 40), fill=(120, 10, 20))
                cx, cy, cw, ch = c
                d = dr(img)
                for i in range(8):
                    d.rectangle([cx, cy + i * 21, cx + cw, cy + i * 21 + 21], fill=mixc((170, 20, 30), (90, 0, 20), i / 7))
                big_text(img, cx + cw // 2, cy + 8, "AI搞钱训练营", (255, 220, 60), scale=2, outline=(90, 30, 0))
                text(img, cx + cw // 2, cy + 44, "学完月入过万！普通人也能翻身！", (255, 255, 255), anchor="c")
                text(img, cx + 60, cy + 70, "原价 ¥3999", (230, 180, 180))
                d.line([cx + 58, cy + 77, cx + 62 + tw("原价 ¥3999"), cy + 77], fill=(255, 255, 255))
                big_text(img, cx + 196, cy + 62, "¥199", (255, 240, 80), scale=3, outline=(120, 0, 0))
                if int(t * 4) % 2 == 0:
                    text(img, cx + cw // 2, cy + 108, "名额仅剩 3 个！", (255, 255, 120), font=FH12, anchor="c")
                rrect(img, cx + cw // 2 - 50, cy + 128, 100, 22, (255, 210, 50))
                text(img, cx + cw // 2, cy + 132, "立即抢购", (120, 20, 20), font=FH12, anchor="c")
                r = random.Random(int(t * 6))
                for _ in range(6):
                    emote(img, "spark", r.randint(x, x + w - 6), r.randint(y + 16, y + h - 6), t)
        if m["warn"] <= t < m["cut"]:
            popup(img, t, m["warn"], 232, 40, 220, 48, "机场", [("流量剩余 0.3GB，即将断开", (220, 40, 40))],
                  bar=(220, 60, 60) if int(t * 4) % 2 == 0 else (150, 30, 30))
            paste(img, ICONS["warn"], 132, 40)
        if t >= m["write"]:
            nr = (t - m["write"]) * 5.0
            notepad(img, 110, 64, 250, 140, REPORT, min(len(REPORT), nr))
        grey = t >= m["cut"] + 0.9
        chars_idle(img, s, t, cx_shades=(m["tempt"] <= t < m["no"]), grey=grey,
                   cl_expr="dead" if grey else ("shock" if m["warn"] <= t < m["warn"] + 1.6 else None),
                   cx_expr="dead" if grey else ("cool" if m["tempt"] <= t < m["no"] else None))
        if m["cut"] <= t < m["cut"] + 0.9:
            img = glitch(img, 0.8, random.Random(int(t * 30)))
        if grey:
            a = np.asarray(img).astype(np.float32)
            g = a.mean(axis=2, keepdims=True)
            img = Image.fromarray((g * 0.7).repeat(3, 2).astype(np.uint8))
            popup(img, t, m["cut"] + 0.9, 232, 100, 160, 44, "网络", [("连接已断开", (200, 40, 40))], bar=(90, 90, 100))
            k = clamp((t - (m["cut"] + 2.2)) / 1.0)
            img = dither_fade(img, k)
        return img

    s.draw = draw
    return s


# ======================================================================= S8 dawn
def s_dawn():
    s = Scene("dawn")
    s.fade_in = 1.0
    s.sfx_at("birds", 0.2, dur=5.0)
    s.wait(1.6)
    s.mark("alarm")
    s.sfx_at("alarm", dur=1.8)
    s.wait(1.2)
    s.mark("wake")
    s.wait(1.6)
    s.say("me", "唔……几点了……", expr="tired")
    s.mark("zoomin")
    s.sfx_at("whoosh")
    s.mus("dawn", fade_in=0.5)
    s.wait(0.9)
    s.mark("read")
    s.wait(len(REPORT) * 0.36 + 1.6)
    s.say("me", "？？？", expr="shock", hold=1.0)
    s.mark("limits")
    for k in range(3):
        s.sfx_at("error", s.cur + k * 0.55)
    s.wait(2.0)
    s.mark("panic")
    s.mus("panic", xfade=0.03)
    s.say("me", "我九点还要交方案啊——！！", expr="shock")
    s.mark("ps")
    s.mus("dawn", offset=10.43)
    s.wait(len(PS) * 0.9 + 1.4)
    s.say("me", "……这俩傻子。", expr="smile", hold=1.6)
    s.end()
    s.fade_out = 0.6
    m = s.m

    def full_view(t):
        img = bg_desktop("day")
        scroll = 0
        lines = REPORT + [("", INK)] + PS
        if t >= m["ps"]:
            scroll = int(ease_io(clamp((t - m["ps"]) / 0.8)) * 7 * 14)
            reveal = len(REPORT) + 1 + (t - m["ps"] - 0.6) / 0.9
        else:
            reveal = (t - m["read"]) / 0.36 if t >= m["read"] else 0
        notepad(img, 66, 8, 348, 196, lines, max(0, reveal), scroll)
        if m["limits"] <= t < m["ps"]:
            popup(img, t, m["limits"], 170, 60, 236, 44, "Claude",
                  [("你已达到用量上限，10:00 后重置", (220, 40, 40))], bar=(217, 119, 87))
            popup(img, t, m["limits"] + 0.55, 300, 104, 236, 44, "ChatGPT",
                  [("你已达到使用上限，请稍后再试", (220, 40, 40))], bar=(60, 64, 80))
            popup(img, t, m["limits"] + 1.1, 210, 148, 236, 44, "机场",
                  [("本月流量已用尽，请续费", (220, 40, 40))], bar=(60, 120, 220))
        chars_idle(img, None, t, cl_expr="sleep", cx_expr="sleep", grey=True)
        return img

    def room_view(t):
        img = bg_room("dawn")
        mini = full_view(m["read"]).resize((SCREEN[2], SCREEN[3]), Image.BOX)
        img.paste(mini, SCREEN[:2])
        if t < m["wake"]:
            draw_person(img, "sleep", t, "dawn")
        elif t < m["wake"] + 0.4:
            draw_person(img, "wake", t, "dawn")
        elif t < m["wake"] + 1.4:
            draw_person(img, "stretch", t, "dawn")
        else:
            draw_person(img, "sit", t, "dawn")
        desk_clock(img, "07:30", blink=m["alarm"] <= t < m["alarm"] + 2.0, t=t)
        if m["alarm"] <= t < m["alarm"] + 2.0:
            emote(img, "note", 450, 120, t)
        return img

    def draw(img, t):
        if t < m["zoomin"]:
            return room_view(t)
        if t < m["read"]:
            base = room_view(m["zoomin"])
            p = ease_in(clamp((t - m["zoomin"]) / 0.8))
            sx, sy, sw, sh = SCREEN
            x0, y0 = lerp(0, sx, p), lerp(0, sy, p)
            x1, y1 = lerp(W, sx + sw, p), lerp(H, sy + sh, p)
            return base.crop((int(x0), int(y0), int(math.ceil(x1)), int(math.ceil(y1)))).resize((W, H), Image.NEAREST)
        img = full_view(t)
        if t < m["read"] + 0.4:
            blocky = full_view(m["read"]).resize((SCREEN[2], SCREEN[3]), Image.BOX).resize((W, H), Image.NEAREST)
            img = dither_mix(blocky, img, clamp((t - m["read"]) / 0.4))
        return img

    s.draw = draw
    s.shake = lambda t: (m["panic"] <= t < m["panic"] + 1.6)
    return s


# ======================================================================= S9 workday + gift card
def s_work():
    s = Scene("work")
    s.fade_in = 0.6
    s.mus("mainA", 0)
    s.wait(1.0)
    s.mark("reset")
    s.sfx_at("powerup")
    s.wait(0.6)
    s.say("clawd", "十点了，额度重置！我们回来了！", expr="happy")
    s.mark("work")
    for k in range(4):
        s.sfx_at("ding", s.cur + 1.6 + k * 1.6)
    s.say("N", "后来我想明白了：在国内的互联网上，它们赚不到一分钱。", hold=2.8)
    s.say("N", "但它们能帮我把活干完，准时下班。", hold=2.2)
    s.mark("month")
    s.sfx_at("error")
    s.sfx_at("error", s.cur + 0.5)
    s.wait(0.4)
    s.say("codex", "警告：Apple ID 余额不足，续订失败。", expr="shock")
    s.mark("buy")
    s.sfx_at("coin")
    s.say("N", "于是月底，我又默默买了 284 块的礼品卡。")
    s.say("clawd", "续上了！", expr="happy", hold=1.4)
    s.end()
    s.fade_out = 0.5
    m = s.m
    tasks = ["方案.pptx", "周报.docx", "登录bug.py", "季度PPT"]

    def draw(img, t):
        img = bg_desktop("day")
        clock = kf([(0, 600), (m["work"], 600), (m["month"], 18 * 60)], t)
        dusk = clamp((clock - 600) / 480.0)
        if dusk > 0 and t < m["month"]:
            img = tint(img, (255, 140, 80), dusk * 0.25)
        if t >= m["work"]:
            for k, name in enumerate(tasks):
                tt0 = m["work"] + k * 1.6
                if t < tt0 or (t >= m["month"]):
                    continue
                wx, wy = 96 + k * 34, 22 + k * 26
                if pop_rect(img, t, tt0, wx, wy, 180, 90):
                    c = window(img, wx, wy, 180, 90, name, bar=[(230, 110, 60), (60, 120, 220), (60, 64, 80), (200, 80, 160)][k],
                               fill=(250, 250, 252))
                    cx, cy, cw, ch = c
                    pr = clamp((t - tt0) / 1.4)
                    for j in range(4):
                        ln = int((cw - 20) * clamp(pr * 4 - j))
                        dr(img).line([cx + 8, cy + 8 + j * 9, cx + 8 + ln, cy + 8 + j * 9], fill=(180, 180, 200))
                    bar(img, cx + 8, cy + ch - 16, cw - 50, 8, pr, (110, 220, 130))
                    if pr >= 1:
                        paste(img, ICONS["check"], cx + cw - 32, cy + ch - 22, 2)
        if t >= m["month"]:
            popup(img, t, m["month"], 232, 60, 260, 44, "App Store",
                  [("Apple ID 余额不足 · ChatGPT Plus 续订失败", (220, 40, 40))], bar=(70, 70, 80))
            popup(img, t, m["month"] + 0.5, 232, 106, 260, 44, "App Store",
                  [("Apple ID 余额不足 · Claude Pro 续订失败", (220, 40, 40))], bar=(70, 70, 80))
            if t >= m["buy"]:
                popup(img, t, m["buy"], 232, 150, 250, 58, "某宝 · 订单",
                      [("美区 App Store 礼品卡 $40", INK), ("实付 ¥284.00   √ 已兑换", (40, 150, 60))], bar=(255, 100, 30))
        taskbar_clock(img, hhmm(clock if t < m["month"] else 23 * 60 + 59))
        grey = t < m["reset"]
        happy = t >= m["buy"] + 0.4
        cl_arms = "up" if (happy and int(t * 4) % 2 == 0) else "side"
        jump = int(abs(math.sin(t * 7)) * 6) if happy else 0
        chars_idle(img, s, t, grey=grey, cl_arms=cl_arms, cl_expr="happy" if happy else None,
                   cx_expr="excited" if happy else ("sleep" if grey else None),
                   cl_xy=(CL_XY[0], CL_XY[1] - jump), cx_xy=(CX_XY[0], CX_XY[1] - jump))
        if m["reset"] <= t < m["reset"] + 0.6:
            for k in range(8):
                a = k / 8 * 6.28
                rr = (t - m["reset"]) * 60
                emote(img, "spark", CL_XY[0] + 20 + math.cos(a) * rr, CL_XY[1] + 12 + math.sin(a) * rr, 0)
                emote(img, "spark", CX_XY[0] + 18 + math.cos(a) * rr, CX_XY[1] + 14 + math.sin(a) * rr, 0)
        return img

    s.draw = draw
    return s


# ======================================================================= S10 epilogue: the airport runs away
def s_epilogue():
    s = Scene("epi")
    s.fade_in = 0.5
    s.mus("night", 0, vol=0.8)
    s.wait(0.8)
    s.say("codex", "今天的活儿，全部完成。", expr="happy")
    s.say("clawd", "嗯。这样挺好。", expr="happy")
    s.mark("notice")
    s.sfx_at("notif")
    s.wait(4.6)
    s.mark("dc")
    s.mus("stop", xfade=0.05)
    s.sfx_at("glitch", dur=0.6)
    s.sfx_at("disconnect", s.cur + 0.6)
    s.wait(0.8)
    s.say("both", "……诶？", expr="shock", hold=1.4)
    s.mark("room")
    s.wait(0.6)
    s.say("me", "……", expr="blank", hold=1.6)
    s.mark("search")
    s.sfx_at("typing", s.cur + 0.5, dur=1.8)
    s.wait(3.0)
    s.mark("fin")
    s.mus("sting")
    s.wait(3.0)
    s.end()
    s.fade_out = 0.8
    m = s.m

    def draw(img, t):
        if t < m["room"]:
            img = bg_desktop("night")
            taskbar_clock(img, "23:12")
            if t >= m["notice"]:
                cxm, cym, ww, hh = 232, 96, 268, 128
                x2, y2 = cxm - ww // 2, cym - hh // 2
                if pop_rect(img, t, m["notice"], x2, y2, ww, hh):
                    c = window(img, x2, y2, ww, hh, "机场 · 公告", bar=(60, 120, 220), fill=(250, 250, 252))
                    cx, cy, cw, ch = c
                    rrect(img, cx + 6, cy + 5, 15, 14, (60, 120, 220))
                    paste(img, ICONS["plane"], cx + 8, cy + 7)
                    text(img, cx + 24, cy + 6, "【重要通知】", (220, 40, 40), font=FH12)
                    ls = ["因不可抗力，本机场即日起", "停止全部服务。", "感谢大家一路相伴，", "江湖再见！"]
                    for i, l in enumerate(ls):
                        text(img, cx + 12, cy + 26 + i * 16, typed(l, t, m["notice"] + 0.3 + i * 0.8, 16), INK)
                    if t > m["notice"] + 3.6:
                        text(img, cx + cw - 8, cy + ch - 16, "（官网已无法访问）", (150, 150, 160), anchor="r")
            grey = t >= m["dc"] + 0.6
            chars_idle(img, s, t, grey=grey, cl_expr="shock" if t >= m["dc"] + 0.6 else None,
                       cx_expr="shock" if t >= m["dc"] + 0.6 else None)
            if m["dc"] <= t < m["dc"] + 0.6:
                img = glitch(img, 0.9, random.Random(int(t * 30)))
            if grey:
                a = np.asarray(img).astype(np.float32)
                g = a.mean(axis=2, keepdims=True)
                img = Image.fromarray((g * 0.7).repeat(3, 2).astype(np.uint8))
                popup(img, t, m["dc"] + 0.6, 232, 168, 150, 40, "网络", [("连接已断开", (200, 40, 40))], bar=(90, 90, 100))
            return img
        if t < m["search"]:
            img = bg_room("night")
            d = dr(img)
            d.rectangle(list(SCREEN[:2]) + [SCREEN[0] + SCREEN[2] - 1, SCREEN[1] + SCREEN[3] - 1], fill=(60, 60, 66))
            text(img, SCREEN[0] + SCREEN[2] // 2, SCREEN[1] + 28, "连接已断开", (200, 200, 200), anchor="c")
            draw_person(img, "sit", t)
            desk_clock(img, "23:13")
            pc_rgb(img, t)
            return img
        img = Image.new("RGB", (W, H), (250, 250, 252))
        d = dr(img)
        d.rectangle([0, 0, W, 22], fill=(220, 222, 230))
        rrect(img, 6, 4, 120, 16, (250, 250, 252))
        text(img, 12, 5, "新标签页", INK)
        big_text(img, W // 2, 60, "搜一下", (60, 110, 230), scale=3, outline=None)
        rrect(img, 70, 110, 340, 30, (60, 110, 230))
        rrect(img, 72, 112, 336, 26, (255, 255, 255))
        q = typed("机场推荐 便宜 稳定 不跑路", t, m["search"] + 0.5, 9)
        text(img, 82, 119, q, INK, font=FH12)
        if int(t * 2) % 2 == 0:
            d.rectangle([84 + tw(q, FH12), 118, 85 + tw(q, FH12), 131], fill=INK)
        if t >= m["fin"]:
            p = clamp((t - m["fin"]) / 0.3)
            stamp(img, W // 2, 190, "完", (220, 40, 40), p, scale=4, rot=-6)
        return img

    s.draw = draw
    return s


# ======================================================================= credits
CREDITS = [
    ("赛博长工", "title"),
    ("", None),
    ("—— 主演 ——", "h"),
    ("Claude ……… 皮肤：Clawd", None),
    ("GPT ……… 皮肤：Codex", None),
    ("我 ……… 全程睡着", None),
    ("", None),
    ("—— 制作 ——", "h"),
    ("剧本 / 美术 / 音乐 / 剪辑：Claude Opus 5.5 extra", None),
    ("", None),
    ("—— 特别鸣谢 ——", "h"),
    ("用户8823（在吗）", None),
    ("张总（预算500做淘宝）", None),
    ("会计小李（仅退款）", None),
    ("美区 App Store 礼品卡", None),
    ("¥80/年 的机场（已跑路）", None),
    ("", None),
    ("本片纯属虚构", "s"),
    ("如有雷同，说明你也在付这 280", "s"),
]


def s_credits():
    s = Scene("credits")
    s.fade_in = 0.6
    s.mus("main", 0)
    s.wait(16.0)
    s.mark("thanks")
    s.wait(4.6)
    s.end()
    s.fade_out = 1.2
    m = s.m

    def draw(img, t):
        stars_bg(img, t, seed=4, top=(8, 8, 24), bot=(30, 24, 56))
        bricks(img, 230, col=(80, 60, 90), mortar=(50, 36, 60), top=(90, 160, 110))
        total_h = len(CREDITS) * 18 + 40
        y0 = int(H - 40 - (t / 15.5) * (total_h + H - 60))
        for i, (l, kind) in enumerate(CREDITS):
            y = y0 + i * 18
            if y < -30 or y > 226:
                continue
            if kind == "title":
                big_text(img, W // 2, y - 8, l, (255, 168, 96), scale=2, outline=(50, 20, 40))
            elif kind == "h":
                text(img, W // 2, y, l, (255, 210, 120), font=FH12, anchor="c")
            elif kind == "s":
                text(img, W // 2, y, l, (170, 170, 200), anchor="c")
            else:
                text(img, W // 2, y, l, (255, 255, 255), anchor="c")
        d = dr(img)
        d.rectangle([0, 226, W, 229], fill=(8, 8, 24))
        if t < m["thanks"]:
            cx = (t * 22) % (W + 120) - 60
            actor_clawd(img, None, t, cx, 198, walk=1 + int(t * 6) % 2)
            actor_codex(img, None, t, cx - 54, 194, walk=1 + int(t * 6 + 1) % 2)
        else:
            lt = t - m["thanks"]
            big_text(img, W // 2, 84, "感谢观看", (255, 255, 255), scale=3, outline=(40, 30, 70))
            arms = "up" if int(t * 3) % 2 == 0 else "side"
            actor_clawd(img, None, t, 170, 198, expr="happy", arms=arms)
            actor_codex(img, None, t, 266, 194, expr="happy")
            text(img, W // 2, 150, "Claude & GPT 下次还想替你打工", (200, 200, 230), anchor="c")
        return img

    s.draw = draw
    return s


def build():
    scenes = [
        s_title(),
        s_room(),
        s_wake(),
        card_scene("第一回", "闲鱼接单"),
        s_xianyu(),
        card_scene("第二回", "做自媒体"),
        s_media(),
        card_scene("第三回", "做个AI应用"),
        s_app(),
        card_scene("第四回", "数据标注"),
        s_label(),
        s_low(),
        s_dawn(),
        s_work(),
        card_scene("", "一个月后……", dur=2.2),
        s_epilogue(),
        s_credits(),
    ]
    return scenes
