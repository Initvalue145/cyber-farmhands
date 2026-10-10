# -*- coding: utf-8 -*-
# 《赛博长工 Cyber Farmhands》 —— 由 Claude Opus 5.5 extra 制作 / Made by Claude Opus 5.5 extra
"""渲染 / Render:  python main_主程序.py [times | sheet <秒...> | audio | full [输出文件名 / out name]]"""
import sys, os, shutil, subprocess, time, random
import numpy as np
from engine_引擎 import *
from common_通用组件 import draw_hud, draw_dialogue, taskbar_clock, hhmm
import scenes_剧本分镜 as S
import audio_音频合成 as audio

# ffmpeg 路径：环境变量 FFMPEG，或系统 PATH / ffmpeg from $FFMPEG or PATH
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "输出_output")
os.makedirs(os.path.join(OUT_DIR, "preview"), exist_ok=True)


def timeline():
    scenes = S.build()
    starts, t = [], 0.0
    for sc in scenes:
        starts.append(t)
        t += sc.dur
    return scenes, starts, t


def render(sc, lt):
    img = Image.new("RGB", (W, H))
    out = sc.draw(img, lt) or img
    if sc.name == "wake" and lt < 0.7:
        out = dither_mix(S.wake_blocky(), out, lt / 0.7)
    h = None
    if callable(sc.hud):
        h = sc.hud(lt)
    elif getattr(sc, "hud_from", None) is not None and lt >= sc.hud_from:
        h = dict(money=0.0, flow=12.0, clock=178)
    if h is not None:
        x = 376
        if getattr(sc, "hud_from", None) is not None:
            x = int(376 + (1 - ease_out(clamp((lt - sc.hud_from) / 0.35))) * 110)
        taskbar_clock(out, hhmm(h["clock"]))
        draw_hud(out, h["money"], h["flow"], h["clock"], lt, locked=h.get("locked", False), x=x,
                 flash_money=h.get("flash", False))
    draw_dialogue(out, sc, lt)
    shake = getattr(sc, "shake", None)
    if shake and shake(lt):
        r = random.Random(int(lt * 40))
        a = np.asarray(out)
        a = np.roll(a, (r.randint(-3, 3), r.randint(-3, 3)), axis=(0, 1))
        out = Image.fromarray(a)
    if sc.fade_in and lt < sc.fade_in:
        out = dither_fade(out, 1 - lt / sc.fade_in)
    if sc.fade_out and lt > sc.dur - sc.fade_out:
        out = dither_fade(out, (lt - (sc.dur - sc.fade_out)) / sc.fade_out)
    return out


def frame_at(scenes, starts, t):
    i = 0
    while i + 1 < len(scenes) and t >= starts[i + 1]:
        i += 1
    return render(scenes[i], t - starts[i])


def build_audio(scenes, starts, total, path):
    cues, events = [], []
    for sc, st in zip(scenes, starts):
        for (t, name, opts) in sc.music:
            cues.append((st + t, name, opts))
        for (t, name, opts) in sc.sfx:
            events.append((st + t, name, opts))
    mix = audio.mixdown(total, cues, events)
    audio.write_wav(path, mix)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    scenes, starts, total = timeline()
    print("total %.1fs (%d:%02d)" % (total, int(total) // 60, int(total) % 60))
    for sc, st in zip(scenes, starts):
        print("  %-8s %6.1f  +%5.1f" % (sc.name, st, sc.dur))
    if mode == "times":
        return
    if mode == "sheet":
        args = sys.argv[2:]
        if args and args[0] == "every":
            step = float(args[1])
            t0 = float(args[2]) if len(args) > 2 else 0
            t1 = float(args[3]) if len(args) > 3 else total
            ts = list(np.arange(t0, t1, step))
        else:
            ts = [float(a) for a in args]
        name = os.environ.get("SHEET", "sheet")
        cols = 3
        for k in range(0, len(ts), 9):
            chunk = ts[k:k + 9]
            rows = (len(chunk) + cols - 1) // cols
            sheet = Image.new("RGB", (W * cols, H * rows), (0, 0, 0))
            for j, t in enumerate(chunk):
                im = frame_at(scenes, starts, t)
                text(im, 2, 2, "%.1f" % t, (255, 255, 0), outline=(0, 0, 0))
                sheet.paste(im, ((j % cols) * W, (j // cols) * H))
            sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
            p = os.path.join(OUT_DIR, "preview", "%s_%02d.png" % (name, k // 9))
            sheet.save(p)
            print("wrote", p)
        return
    wav = os.path.join(OUT_DIR, "soundtrack.wav")
    t0 = time.time()
    build_audio(scenes, starts, total, wav)
    print("audio done %.1fs" % (time.time() - t0))
    if mode == "audio":
        return
    outname = sys.argv[2] if len(sys.argv) > 2 else "赛博长工_Cyber-Farmhands_1080p.mp4"
    out = os.path.join(OUT_DIR, outname)
    tmp = os.path.join(OUT_DIR, "render_tmp.mp4")
    nframes = int(total * FPS)
    cmd = [FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS),
           "-i", "-", "-i", wav, "-vf", "scale=1920:1080:flags=neighbor", "-c:v", "libx264", "-preset", "slow",
           "-crf", "15", "-tune", "animation", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-shortest", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(nframes):
        im = frame_at(scenes, starts, f / FPS)
        p.stdin.write(im.tobytes())
        if f % 480 == 0:
            print("frame %d/%d  %.0fs elapsed" % (f, nframes, time.time() - t0), flush=True)
    p.stdin.close()
    p.wait()
    if os.path.exists(out):
        os.remove(out)
    os.replace(tmp, out)
    print("done", out, "%.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
