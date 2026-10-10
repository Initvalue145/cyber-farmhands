# -*- coding: utf-8 -*-
# 《赛博长工 Cyber Farmhands》 —— 由 Claude Opus 5.5 extra 制作 / Made by Claude Opus 5.5 extra
"""导出仓库素材 / Export repo assets: 剧照 stills, 角色表 character sheet, 预览动图 GIF,
分轨配乐 music tracks, 音效 SFX, 完整配乐 soundtrack, 剧本台词 script.

用法 / Usage:  python export_assets_导出素材.py
"""
import os, subprocess, wave
import numpy as np
from PIL import Image
from engine_引擎 import *
import main_主程序 as M
import audio_音频合成 as audio

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
IMG = os.path.join(ROOT, "图片_images")
AUD = os.path.join(ROOT, "音频_audio")
DOC = os.path.join(ROOT, "文档_docs")

STILLS = [
    (8.0, "01_片头_title"), (27.0, "02_每月账单_monthly-bill"), (37.5, "03_睡着了_fell-asleep"),
    (66.5, "04_三条规矩_three-rules"), (82.0, "05_人脸识别是螃蟹_face-check-crab"),
    (111.0, "06_闲鱼接单_xianyu-orders"), (117.0, "07_仅退款_refund-only"), (121.5, "08_已下架_listing-removed"),
    (150.0, "09_标题党对照组_clickbait-rival"), (155.0, "10_收益0.38元_earnings-0.38"),
    (172.0, "11_埋头写代码_heads-down-coding"), (186.0, "12_上架条件_approval-checklist"),
    (189.0, "13_境外模型_foreign-model"), (211.0, "14_数据标注_data-labeling"),
    (215.5, "15_轨迹过于完美_too-perfect-captcha"), (225.0, "16_我不是机器人_not-a-robot"),
    (240.0, "17_AI搞钱训练营_ai-money-course"), (260.5, "18_连接断开_disconnected"), (266.8, "19_天亮了_dawn"),
    (276.0, "20_搞钱报告_night-report"), (280.6, "21_额度用完_usage-limits"), (288.0, "22_对不起_apology"),
    (309.0, "23_礼品卡续费_gift-card-renewal"), (321.0, "24_机场跑路_vpn-shutdown"), (332.0, "25_完_the-end"),
    (341.0, "26_片尾字幕_credits"), (351.0, "27_感谢观看_thanks"),
]

TRACKS = [
    ("main", "01_主题曲_main-theme"), ("night", "02_深夜摇篮曲_night-lullaby"), ("scheme", "03_搞钱计划_money-scheme"),
    ("hustle", "04_拼命干活_hustle"), ("tempt", "05_卖课广告_course-infomercial"), ("tension", "06_紧张时刻_tension"),
    ("sad", "07_失败音效_fail-jingle"), ("dawn", "08_天亮了_dawn"), ("panic", "09_慌了_panic"),
    ("sting", "10_结尾音效_ending-sting"),
]

SFX = [
    ("coin", "金币_coin"), ("error", "错误_error"), ("ding", "叮_ding"), ("msg", "消息_message"),
    ("stamp", "盖章_stamp"), ("whoosh", "呼啸_whoosh"), ("jump", "跳跃_jump"), ("pop", "弹出_pop"),
    ("land", "落地_land"), ("chime", "章节铃声_chapter-chime"), ("select", "选择_select"), ("click", "点击_click"),
    ("typing", "打字_typing"), ("glitch", "故障_glitch"), ("disconnect", "断线_disconnect"),
    ("scratch", "唱片刮擦_record-scratch"), ("snore", "打呼_snore"), ("alarm", "闹钟_alarm"), ("tick", "滴答_tick"),
    ("powerup", "充能_power-up"), ("cash", "收银_cash-register"), ("fail", "失败_fail"), ("shutter", "快门_shutter"),
    ("birds", "鸟叫_birds"), ("heart", "心跳_heartbeat"), ("slide", "滑块_slider"), ("notif", "通知_notification"),
    ("count", "计数_count"), ("boom", "重音_boom"), ("zip", "关闭窗口_zip"),
    ("blip_clawd", "对话音Claude_blip-claude"), ("blip_codex", "对话音GPT_blip-gpt"),
    ("blip_me", "对话音我_blip-me"), ("blip_buyer", "对话音买家_blip-buyer"),
]

SCENE_TITLES = {
    "title": "片头 / Title", "room": "深夜的我 / Me, late at night", "wake": "电脑里醒来 / Waking up inside the PC",
    "xianyu": "闲鱼接单 / Freelancing on Xianyu", "media": "做自媒体 / Making videos", "app": "做个AI应用 / Building an AI app",
    "label": "数据标注 / Data labeling", "low": "低谷 / Rock bottom", "dawn": "天亮了 / Dawn",
    "work": "上班 / Back to work", "epi": "尾声 / Epilogue", "credits": "片尾 / Credits",
}


def up(im, k=4):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def write_wav(path, y):
    if y.ndim == 1:
        y = np.stack([y, y], 1)
    peak = np.abs(y).max() + 1e-9
    y = y / peak * 0.89
    d = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(audio.SR)
        w.writeframes(d.tobytes())


def stills(scenes, starts):
    out = os.path.join(IMG, "剧照_stills")
    os.makedirs(out, exist_ok=True)
    for t, name in STILLS:
        up(M.frame_at(scenes, starts, t)).save(os.path.join(out, name + ".png"))
    up(M.frame_at(scenes, starts, 8.0)).save(os.path.join(IMG, "封面_cover.png"))
    print("stills", len(STILLS))


def gif(scenes, starts, t0=3.4, t1=9.4, fps=12):
    frames = []
    for i in range(int((t1 - t0) * fps)):
        im = up(M.frame_at(scenes, starts, t0 + i / fps), 2)
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=128))
    path = os.path.join(IMG, "预览动图_preview.gif")
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, optimize=True)
    print("gif", os.path.getsize(path) // 1024, "KB")


def character_sheet():
    out = os.path.join(IMG, "角色_characters")
    os.makedirs(out, exist_ok=True)
    cl = [("normal", "平常", "normal"), ("happy", "开心", "happy"), ("determined", "拍板", "decisive"),
          ("worried", "担心", "worried"), ("sad", "难过", "sad"), ("cry", "大哭", "crying"), ("shock", "震惊", "shocked"),
          ("sweat", "冒汗", "sweating"), ("dot", "无语", "speechless"), ("dead", "掉线", "offline")]
    cx = [("normal", "待命", "standby"), ("happy", "开心", "happy"), ("excited", "干劲十足", "fired up"),
          ("flat", "面无表情", "deadpan"), ("think", "思考", "thinking"), ("money", "见钱眼开", "money eyes"),
          ("shock", "震惊", "shocked"), ("error", "报错", "error"), ("cool", "墨镜", "shades"), ("sad", "哭", "crying")]
    me = [("normal", "平常", "normal"), ("tired", "困", "tired"), ("sleep", "睡着", "asleep"), ("shock", "崩溃", "panic"),
          ("cry", "哭", "crying"), ("smile", "笑", "smile"), ("blank", "发呆", "blank")]
    Wd, Hd = 540, 806
    sheet = Image.new("RGB", (Wd, Hd), (28, 26, 46))
    d = dr(sheet)
    big_text(sheet, Wd // 2, 8, "角色设定 Character Sheet", (255, 200, 120), scale=2, outline=(10, 10, 20))
    text(sheet, Wd // 2, 40, "由 Claude Opus 5.5 extra 制作 / Made by Claude Opus 5.5 extra", (170, 170, 200), anchor="c")
    y = 62

    def section(title, sub, items, make, sprite_scale=2):
        nonlocal y
        d.rectangle([10, y, Wd - 11, y + 18], fill=(48, 44, 78))
        text(sheet, 16, y + 3, title, (255, 255, 255), font=FH12)
        text(sheet, Wd - 16, y + 3, sub, (190, 190, 220), anchor="r")
        y += 24
        for i, (e, cn, en) in enumerate(items):
            col, row = i % 5, i // 5
            cxp = 14 + col * 104
            cyp = y + row * 108
            d.rectangle([cxp, cyp, cxp + 98, cyp + 100], fill=(40, 38, 64))
            spr = make(e)
            sp = up(spr, sprite_scale)
            sheet.paste(sp, (cxp + 49 - sp.width // 2, cyp + 38 - sp.height // 2), sp)
            text(sheet, cxp + 49, cyp + 72, cn, (255, 255, 255), anchor="c")
            text(sheet, cxp + 49, cyp + 86, en, (160, 160, 190), anchor="c")
        y += ((len(items) + 4) // 5) * 108 + 6

    section("Claude（皮肤：Clawd）", "有主见，负责拍板和守底线 / opinionated, makes the calls", cl, lambda e: make_clawd(e))
    section("GPT（皮肤：Codex）", "埋头苦干，写代码最快 / heads-down worker, fastest coder", cx,
            lambda e: make_codex(e, shades=(e == "cool")))
    section("我 / Me", "同时订阅两家，穷 / pays for both, broke", me, lambda e: face_me(e), sprite_scale=2)
    up(sheet, 2).save(os.path.join(out, "角色设定表_character-sheet.png"))
    for spr, name in [(make_clawd("happy"), "Claude角色_claude-clawd-skin"),
                      (make_codex("happy"), "GPT角色_gpt-codex-skin"), (face_me("smile"), "我_me")]:
        up(spr, 8).save(os.path.join(out, name + ".png"))
    print("character sheet")


def music():
    out = os.path.join(AUD, "分轨配乐_music-tracks")
    os.makedirs(out, exist_ok=True)
    for key, name in TRACKS:
        y, loop_len = audio.get_track(key)
        write_wav(os.path.join(out, name + ".wav"), y)
    sfx_out = os.path.join(AUD, "音效_sfx")
    os.makedirs(sfx_out, exist_ok=True)
    for key, name in SFX:
        write_wav(os.path.join(sfx_out, name + ".wav"), audio.sfx(key))
    print("music", len(TRACKS), "sfx", len(SFX))


def soundtrack(scenes, starts, total):
    wav = os.path.join(M.OUT_DIR, "soundtrack.wav")
    M.build_audio(scenes, starts, total, wav)
    for ext, args in [("flac", ["-c:a", "flac"]), ("mp3", ["-c:a", "libmp3lame", "-b:a", "320k"])]:
        p = os.path.join(AUD, "完整配乐_full-soundtrack." + ext)
        subprocess.run([M.FF, "-y", "-loglevel", "error", "-i", wav] + args + [p], check=True)
        print(ext, os.path.getsize(p) // 1024, "KB")


def script_doc(scenes, starts):
    os.makedirs(DOC, exist_ok=True)
    L = ["# 剧本台词 / Script", "", "> 由 `export_assets_导出素材.py` 从源代码自动导出，时间为成片中的时间点。",
         "> Auto-exported from the source; timestamps match the finished video. 台词保持中文原文。", ""]
    card = None
    for sc, st in zip(scenes, starts):
        if sc.name == "card":
            card = getattr(sc, "card", None)
            continue
        head = SCENE_TITLES.get(sc.name, sc.name)
        if card:
            num, title = card
            head = "%s · %s" % (num, head) if num else "%s  —  %s" % (title, head)
            card = None
        L.append("## %s  `%d:%02d`" % (head, int(st) // 60, int(st) % 60))
        L.append("")
        if sc.name == "title":
            L.append("- `0:00` **字幕**：本片根据真实账单改编（单位：人民币，含泪）")
            L.append("- `0:03` **标题**：赛博长工 —— Claude & GPT 的深夜搞钱计划")
        events = [(ln["t0"], SPEAKERS[ln["who"]]["name"] or "旁白", ln["text"]) for ln in sc.lines]
        for (t, side, who, txt) in getattr(sc, "chat", []):
            events.append((t, "闲鱼消息" if side == "l" else "闲鱼回复", (who + "：" if who else "") + txt))
        for t, who, txt in sorted(events):
            g = st + t
            L.append("- `%d:%02d` **%s**：%s" % (int(g) // 60, int(g) % 60, who, txt))
        L.append("")
    open(os.path.join(DOC, "剧本台词_script.md"), "w", encoding="utf-8").write("\n".join(L))
    print("script doc")


if __name__ == "__main__":
    scenes, starts, total = M.timeline()
    stills(scenes, starts)
    gif(scenes, starts)
    character_sheet()
    music()
    soundtrack(scenes, starts, total)
    script_doc(scenes, starts)
