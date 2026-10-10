# -*- coding: utf-8 -*-
# 《赛博长工 Cyber Farmhands》 —— 由 Claude Opus 5.5 extra 制作 / Made by Claude Opus 5.5 extra
"""Tiny 8-bit synth: pulse / stepped triangle / noise, a sequencer, tracks and SFX."""
import math
import numpy as np

SR = 44100
rng = np.random.RandomState(7)
NOISE = rng.uniform(-1, 1, SR * 4).astype(np.float32)

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(s):
    s = s.strip()
    n = NOTE[s[0]]
    i = 1
    while i < len(s) and s[i] in "#b":
        n += 1 if s[i] == "#" else -1
        i += 1
    octv = int(s[i:])
    return 12 * (octv + 1) + n


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


# ------------------------------------------------------------ oscillators
def _blep(t, dt):
    r = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    r[m] = x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    r[m] = x * x + x + x + 1
    return r


def pulse(freq, n, duty=0.5, phase0=0.0):
    f = np.broadcast_to(np.asarray(freq, np.float64), (n,)).copy()
    dt = f / SR
    ph = (phase0 + np.cumsum(dt)) % 1.0
    y = np.where(ph < duty, 1.0, -1.0)
    y += _blep(ph, dt)
    y -= _blep((ph - duty) % 1.0, dt)
    y -= (2 * duty - 1)
    return y.astype(np.float32)


def tri(freq, n, steps=16):
    f = np.broadcast_to(np.asarray(freq, np.float64), (n,))
    ph = np.cumsum(f / SR) % 1.0
    y = 4 * np.abs(ph - 0.5) - 1
    if steps:
        y = np.round((y + 1) * (steps - 1) / 2) / ((steps - 1) / 2) - 1
    return y.astype(np.float32)


def noise(n, rate=SR, seed=0):
    idx = (np.arange(n) * (rate / SR)).astype(np.int64) + seed * 977
    return NOISE[idx % len(NOISE)]


def env(n, a=0.004, d=0.08, s=0.7, r=0.03, gate=None):
    """ADSR. gate = samples of key-down; release afterwards to n."""
    if gate is None:
        gate = n
    e = np.ones(n, np.float32) * s
    A = max(1, int(a * SR))
    D = max(1, int(d * SR))
    t = np.arange(n)
    e[:A] = np.linspace(0, 1, A)[:min(A, n)] if n >= A else np.linspace(0, 1, A)[:n]
    if n > A:
        k = min(D, n - A)
        e[A:A + k] = 1 - (1 - s) * (np.arange(k) / D)
    if gate < n:
        R = n - gate
        lvl = e[gate - 1] if gate > 0 else 0
        e[gate:] = lvl * np.exp(-np.arange(R) / max(1, r * SR) * 3)
    return e


def expdecay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR)).astype(np.float32)


# ------------------------------------------------------------ sequencer
def parse(seq):
    """'C5:1 E5:.5 r:.5' -> [(midi|None, beats)]"""
    out = []
    for tok in seq.split():
        n, b = tok.split(":")
        b = float(b)
        out.append((None if n == "r" else midi(n), b))
    return out


def render_lead(buf, notes, bpm, t0=0.0, vol=0.2, duty=0.25, gate=0.9, vib=0.25, a=0.005, d=0.1, s=0.75,
                rel=0.05, wave="pulse", slide=False, transpose=0):
    spb = 60.0 / bpm
    t = t0
    for m, b in notes:
        if m is not None:
            m = m + transpose
            dur = b * spb
            n = int((dur * gate + rel * 3) * SR)
            gs = int(dur * gate * SR)
            f = np.full(n, hz(m))
            if vib and dur > 0.25:
                tt = np.arange(n) / SR
                depth = np.clip((tt - 0.18) / 0.2, 0, 1) * vib
                f = f * 2 ** (depth * np.sin(2 * math.pi * 5.5 * tt) / 12)
            if wave == "pulse":
                y = pulse(f, n, duty)
            else:
                y = tri(f, n)
            y *= env(n, a, d, s, rel, gs) * vol
            i0 = int(t * SR)
            if i0 < len(buf):
                k = min(n, len(buf) - i0)
                buf[i0:i0 + k] += y[:k]
        t += b * spb
    return t


def render_arp(buf, chords, bpm, t0=0.0, vol=0.07, duty=0.125, rate=24.0, octave_shift=0, pattern=None):
    """chords: [(['C4','E4','G4'], beats)]. fast arpeggio shimmer."""
    spb = 60.0 / bpm
    t = t0
    for ch, b in chords:
        if ch:
            ms = [midi(c) + 12 * octave_shift for c in ch]
            dur = b * spb
            n = int(dur * SR)
            idx = (np.arange(n) / SR * rate).astype(int) % len(ms)
            f = np.array([hz(m) for m in ms])[idx]
            y = pulse(f, n, duty) * env(n, 0.003, 0.2, 0.6, 0.02, n - int(0.01 * SR)) * vol
            i0 = int(t * SR)
            if i0 < len(buf):
                k = min(n, len(buf) - i0)
                buf[i0:i0 + k] += y[:k]
        t += b * spb


def render_broken(buf, chords, bpm, t0=0.0, vol=0.08, duty=0.25, step=0.5, decay=0.25, pat=(0, 1, 2, 3, 2, 1)):
    """music-box style broken chords in `step` beats"""
    spb = 60.0 / bpm
    t = t0
    for ch, b in chords:
        if ch:
            ms = [midi(c) for c in ch]
            nsteps = int(round(b / step))
            for i in range(nsteps):
                m = ms[pat[i % len(pat)] % len(ms)]
                n = int(step * spb * SR * 1.6)
                y = pulse(hz(m), n, duty) * expdecay(n, decay) * vol
                y[:40] *= np.linspace(0, 1, 40)
                i0 = int((t + i * step * spb) * SR)
                if i0 < len(buf):
                    k = min(n, len(buf) - i0)
                    buf[i0:i0 + k] += y[:k]
        t += b * spb


def render_bass(buf, notes, bpm, t0=0.0, vol=0.3, gate=0.85):
    spb = 60.0 / bpm
    t = t0
    for m, b in notes:
        if m is not None:
            dur = b * spb
            n = int((dur * gate + 0.02) * SR)
            y = tri(hz(m), n) * env(n, 0.002, 0.05, 0.9, 0.01, int(dur * gate * SR)) * vol
            i0 = int(t * SR)
            if i0 < len(buf):
                k = min(n, len(buf) - i0)
                buf[i0:i0 + k] += y[:k]
        t += b * spb


def drum(kind, vol=1.0):
    if kind == "k":
        n = int(0.16 * SR)
        tt = np.arange(n) / SR
        f = 55 + 140 * np.exp(-tt * 38)
        y = tri(f, n, steps=16) * expdecay(n, 0.07) * 0.9
        y[:300] += noise(300, 9000) * np.linspace(0.5, 0, 300)
        return y * vol
    if kind == "s":
        n = int(0.18 * SR)
        y = noise(n, 22000, 3) * expdecay(n, 0.05) * 0.55
        y += tri(np.linspace(240, 150, n), n) * expdecay(n, 0.03) * 0.5
        return y * vol
    if kind == "h":
        n = int(0.05 * SR)
        return noise(n, 44100, 5) * expdecay(n, 0.012) * 0.22 * vol
    if kind == "o":
        n = int(0.2 * SR)
        return noise(n, 44100, 8) * expdecay(n, 0.07) * 0.2 * vol
    if kind == "c":
        n = int(1.0 * SR)
        return noise(n, 30000, 11) * expdecay(n, 0.35) * 0.35 * vol
    if kind == "t":  # low tom
        n = int(0.2 * SR)
        tt = np.arange(n) / SR
        return tri(110 + 60 * np.exp(-tt * 20), n) * expdecay(n, 0.08) * 0.7 * vol
    return np.zeros(1, np.float32)


_dcache = {}


def render_drums(buf, bars, bpm, t0=0.0, vol=0.5):
    """bars: list of 16-step strings ('k.h.s.h.' etc)."""
    spb = 60.0 / bpm
    step = spb / 4
    t = t0
    for bar in bars:
        for i, c in enumerate(bar):
            if c == ".":
                continue
            key = c
            if key not in _dcache:
                _dcache[key] = drum(c)
            y = _dcache[key] * vol
            i0 = int((t + i * step) * SR)
            if i0 < len(buf):
                k = min(len(y), len(buf) - i0)
                buf[i0:i0 + k] += y[:k]
        t += 16 * step


def stereo_delay(mono, bpm, beats=0.75, fb=0.3, wet=0.28):
    d = int(60.0 / bpm * beats * SR)
    out = mono.copy()
    tap = np.zeros_like(mono)
    tap[d:] = mono[:-d]
    tap2 = np.zeros_like(mono)
    tap2[2 * d:] = mono[:-2 * d] if 2 * d < len(mono) else 0
    L = mono + tap2 * wet * fb
    R = mono + tap * wet
    return L, R


# ------------------------------------------------------------ chords helper
CH = {
    "C": ["C4", "E4", "G4"], "G": ["G3", "B3", "D4"], "Am": ["A3", "C4", "E4"], "F": ["F3", "A3", "C4"],
    "Em": ["E3", "G3", "B3"], "Dm": ["D4", "F4", "A4"], "Bb": ["Bb3", "D4", "F4"], "A": ["A3", "C#4", "E4"],
    "Fmaj7": ["F3", "A3", "C4", "E4"], "Em7": ["E3", "G3", "B3", "D4"], "Dm7": ["D3", "F3", "A3", "C4"],
    "Cmaj7": ["C4", "E4", "G4", "B4"], "G7": ["G3", "B3", "D4", "F4"], "D": ["D4", "F#4", "A4"],
    "Gm": ["G3", "Bb3", "D4"], "E": ["E3", "G#3", "B3"], "Edim": ["E4", "G4", "Bb4"],
}
ROOT = {"C": "C", "G": "G", "Am": "A", "F": "F", "Em": "E", "Dm": "D", "Bb": "Bb", "A": "A", "Fmaj7": "F",
        "Em7": "E", "Dm7": "D", "Cmaj7": "C", "G7": "G", "D": "D", "Gm": "G", "E": "E", "Edim": "E"}


def bass_octaves(prog, lo=2):
    """eighth-note root/octave bounce. prog: [(chord, beats)]"""
    s = []
    for c, b in prog:
        r = ROOT[c]
        for i in range(int(b * 2)):
            s.append((midi(r + str(lo + (i % 2))), 0.5))
    return s


def bass_long(prog, lo=2):
    return [(midi(ROOT[c] + str(lo)), b) for c, b in prog]


def arp_chords(prog, up=1):
    out = []
    for c, b in prog:
        notes = CH[c]
        out.append(([n[:-1] + str(int(n[-1]) + up) for n in notes], b))
    return out


# ------------------------------------------------------------ tracks
def track_main(bpm=150, sections="AB", drums=True, lead_vol=0.19):
    progA = [("C", 4), ("G", 4), ("Am", 4), ("F", 4), ("C", 4), ("G", 4), ("F", 2), ("G", 2), ("C", 4)]
    progB = [("Am", 4), ("Em", 4), ("F", 4), ("G", 4), ("Am", 4), ("Em", 4), ("F", 4), ("G", 4)]
    melA = ("C5:1 E5:.5 G5:.5 C6:1 B5:.5 A5:.5 "
            "G5:1.5 D5:.5 G5:1 F5:.5 E5:.5 "
            "E5:1 A5:1 C6:.5 B5:.5 A5:1 "
            "F5:1 A5:.5 G5:.5 F5:1 E5:.5 D5:.5 "
            "C5:1 E5:.5 G5:.5 C6:1 D6:.5 E6:.5 "
            "D6:1.5 B5:.5 G5:1 A5:.5 B5:.5 "
            "C6:1 A5:1 B5:1 G5:.5 B5:.5 "
            "C6:2 G5:.5 E5:.5 C5:1")
    melB = ("A5:.5 A5:.5 C6:.5 A5:.5 E6:1 D6:1 "
            "B5:.5 B5:.5 G5:.5 B5:.5 E6:1 D6:.5 B5:.5 "
            "C6:.5 C6:.5 A5:.5 C6:.5 F6:1 E6:.5 C6:.5 "
            "D6:1.5 B5:.5 G5:2 "
            "A5:.5 C6:.5 E6:.5 A6:.5 G6:1 E6:1 "
            "G6:.5 E6:.5 B5:.5 E6:.5 D6:1 B5:1 "
            "C6:1 A5:.5 C6:.5 F6:1 E6:.5 F6:.5 "
            "G6:2 D6:1 B5:1")
    beats = 32 * len(sections)
    spb = 60.0 / bpm
    n = int((beats * spb + 2) * SR)
    lead = np.zeros(n, np.float32)
    other = np.zeros(n, np.float32)
    t = 0.0
    for sec in sections:
        prog = progA if sec == "A" else progB
        mel = melA if sec == "A" else melB
        render_lead(lead, parse(mel), bpm, t, vol=lead_vol, duty=0.25 if sec == "A" else 0.5)
        render_arp(other, arp_chords(prog, 1), bpm, t, vol=0.055)
        render_bass(other, bass_octaves(prog, 2), bpm, t, vol=0.30)
        if drums:
            bars = ["k.h.s.h.k.k.s.h."] * 7 + ["k.h.s.h.k.s.sss."]
            if sec == "B":
                bars = ["k.hhs.hhk.hks.hh"] * 7 + ["k.k.s.k.s.s.ssss"]
            render_drums(other, bars, bpm, t, vol=0.42)
        t += 32 * spb
    L, R = stereo_delay(lead, bpm, 0.75)
    return np.stack([L + other, R + other], 1), beats * spb


def track_night(bpm=76, bars=8):
    prog = [("Fmaj7", 4), ("Em7", 4), ("Dm7", 4), ("Cmaj7", 4), ("Fmaj7", 4), ("Em7", 4), ("Dm7", 2), ("G7", 2),
            ("Cmaj7", 4)]
    mel = ("A5:1.5 G5:.5 F5:1 E5:1 G5:2 E5:1 D5:1 F5:1.5 E5:.5 D5:1 C5:1 E5:3 r:1 "
           "A5:1.5 G5:.5 F5:1 C6:1 B5:2 G5:1 E5:1 F5:1 E5:1 D5:1 B4:1 C5:4")
    spb = 60.0 / bpm
    beats = 32
    n = int((beats * spb + 3) * SR)
    lead = np.zeros(n, np.float32)
    other = np.zeros(n, np.float32)
    render_lead(lead, parse(mel), bpm, 0, vol=0.12, duty=0.5, vib=0.3, a=0.03, d=0.3, s=0.6, rel=0.2)
    bc = [([c[:-1] + str(int(c[-1]) + 1) for c in CH[ch]], b) for ch, b in prog]
    render_broken(other, bc, bpm, 0, vol=0.06, duty=0.25, step=0.5, decay=0.35)
    render_bass(other, bass_long(prog, 2), bpm, 0, vol=0.22, gate=0.95)
    L, R = stereo_delay(lead, bpm, 0.5, wet=0.35)
    return np.stack([L + other, R + other], 1), beats * spb


def track_scheme(bpm=132, drums=True):
    prog = [("Dm", 4), ("Dm", 4), ("Bb", 4), ("C", 4), ("Dm", 4), ("Dm", 4), ("Bb", 4), ("A", 4)]
    mel = ("D5:.25 r:.25 F5:.25 r:.25 A5:.5 G5:.5 F5:.5 E5:.5 D5:1 "
           "r:.5 A4:.5 D5:.5 E5:.5 F5:1 E5:.5 D5:.5 "
           "D5:.25 r:.25 F5:.25 r:.25 Bb5:.5 A5:.5 G5:.5 F5:.5 G5:1 "
           "E5:.5 F5:.5 G5:.5 E5:.5 C5:1 r:1 "
           "D5:.25 r:.25 F5:.25 r:.25 A5:.5 G5:.5 F5:.5 E5:.5 D5:1 "
           "r:.5 A4:.5 D5:.5 F5:.5 A5:1 C6:.5 A5:.5 "
           "Bb5:1 A5:.5 G5:.5 F5:.5 G5:.5 F5:.5 D5:.5 "
           "E5:1 C#5:1 A4:1 r:1")
    bassl = []
    pat = {"Dm": ("D2", "D3", "F2", "A2"), "Bb": ("Bb1", "Bb2", "D2", "F2"), "C": ("C2", "C3", "E2", "G2"),
           "A": ("A1", "A2", "C#2", "E2")}
    for c, b in prog:
        r, o, x, y = pat[c]
        bassl += [(midi(r), .5), (None, .5), (midi(o), .5), (midi(r), .5), (None, .5), (midi(r), .5),
                  (midi(x), .5), (midi(y), .5)]
    spb = 60.0 / bpm
    beats = 32
    n = int((beats * spb + 2) * SR)
    lead = np.zeros(n, np.float32)
    other = np.zeros(n, np.float32)
    render_lead(lead, parse(mel), bpm, 0, vol=0.17, duty=0.125, gate=0.7, vib=0.15)
    render_bass(other, bassl, bpm, 0, vol=0.32, gate=0.7)
    # off-beat chord stabs
    t = 0
    for c, b in prog:
        for k in range(int(b)):
            stab = [([x[:-1] + str(int(x[-1]) + 1) for x in CH[c]], 0.15)]
            render_arp(other, stab, bpm, t + (k + 0.5) * spb, vol=0.06, duty=0.25, rate=40)
        t += b * spb
    if drums:
        render_drums(other, ["k.hhs.hkh.khs.hh"] * 7 + ["k.hhs.hks.s.ssss"], bpm, 0, vol=0.4)
    L, R = stereo_delay(lead, bpm, 0.5, wet=0.22)
    return np.stack([L + other, R + other], 1), beats * spb


def track_tempt(bpm=124):
    prog = [("G", 4), ("Em", 4), ("C", 4), ("D", 4)] * 2
    G3 = {"G": "G", "Em": "E", "C": "C", "D": "D"}
    mel = ("D5:.5 G5:.5 B5:.5 D6:.5 G6:1 D6:1 "
           "E6:.5 D6:.5 B5:.5 G5:.5 B5:1 E5:1 "
           "C6:.5 E6:.5 G6:.5 E6:.5 C6:1 E6:1 "
           "F#6:1 E6:.5 D6:.5 A5:1 F#5:1 "
           "D5:.5 G5:.5 B5:.5 D6:.5 G6:1 B6:1 "
           "A6:.5 G6:.5 E6:.5 B5:.5 G6:1 E6:1 "
           "E6:.5 G6:.5 C7:.5 G6:.5 E6:1 C6:1 "
           "D6:1 F#6:1 G6:2")
    spb = 60.0 / bpm
    beats = 32
    n = int((beats * spb + 2) * SR)
    lead = np.zeros(n, np.float32)
    other = np.zeros(n, np.float32)
    render_lead(lead, parse(mel), bpm, 0, vol=0.16, duty=0.25, gate=0.8)
    chords = [(CH[c] if c != "D" else ["D4", "F#4", "A4"], b) for c, b in prog]
    render_arp(other, arp_chords([(c if c != "D" else "D", b) for c, b in prog], 1), bpm, 0, vol=0.06, rate=30)
    render_bass(other, bass_octaves([(c if c != "D" else "D", b) for c, b in prog], 2), bpm, 0, vol=0.3)
    render_drums(other, ["k.h.s.hkk.h.s.ho"] * 7 + ["k.k.s.s.ssssc..."], bpm, 0, vol=0.42)
    L, R = stereo_delay(lead, bpm, 0.75)
    return np.stack([L + other, R + other], 1), beats * spb


def track_dawn(bpm=92, drums_from=4):
    prog = [("F", 4), ("G", 4), ("Em", 4), ("Am", 4), ("Dm", 4), ("G", 4), ("C", 4), ("C", 4)]
    mel = ("C5:.5 F5:.5 A5:1 G5:.5 F5:.5 G5:1 "
           "B4:.5 D5:.5 G5:1 A5:.5 G5:.5 F5:1 "
           "E5:.5 G5:.5 B5:1.5 A5:.5 G5:1 "
           "A5:3 r:1 "
           "F5:.5 A5:.5 D6:1 C6:.5 A5:.5 F5:1 "
           "G5:.5 B5:.5 D6:1 C6:1 B5:1 "
           "C6:2 G5:1 E5:1 "
           "C6:4")
    spb = 60.0 / bpm
    beats = 32
    n = int((beats * spb + 3) * SR)
    lead = np.zeros(n, np.float32)
    other = np.zeros(n, np.float32)
    render_lead(lead, parse(mel), bpm, 0, vol=0.15, duty=0.5, vib=0.25, a=0.01, d=0.2, s=0.7, rel=0.12)
    bc = [([c[:-1] + str(int(c[-1]) + 1) for c in CH[ch]], b) for ch, b in prog]
    render_broken(other, bc, bpm, 0, vol=0.05, duty=0.125, step=0.5, decay=0.3, pat=(0, 1, 2, 1))
    render_bass(other, bass_long([(c, 2) for c, b in prog for _ in range(2)], 2), bpm, 0, vol=0.25)
    render_drums(other, ["................"] * drums_from + ["k.......s.......", "k.....k.s.......",
                                                          "k.......s.......", "k.....k.s...s.s."][:8 - drums_from],
                 bpm, 0, vol=0.3)
    L, R = stereo_delay(lead, bpm, 0.75, wet=0.32)
    return np.stack([L + other, R + other], 1), beats * spb


def track_panic(bpm=176):
    spb = 60.0 / bpm
    beats = 8
    n = int((beats * spb + 1) * SR)
    lead = np.zeros(n, np.float32)
    other = np.zeros(n, np.float32)
    mel = "E5:.25 G5:.25 Bb5:.25 E6:.25 " * 4 + "F5:.25 Ab5:.25 B5:.25 F6:.25 " * 4
    render_lead(lead, parse(mel), bpm, 0, vol=0.12, duty=0.125, gate=0.8, vib=0)
    bassl = [(midi("E2"), .5), (midi("E3"), .5)] * 4 + [(midi("F2"), .5), (midi("F3"), .5)] * 4
    render_bass(other, bassl, bpm, 0, vol=0.32)
    render_drums(other, ["k.k.s.k.k.k.s.kk"] * 2, bpm, 0, vol=0.42)
    return np.stack([lead + other, lead + other], 1), beats * spb


def track_tension(bpm=60):
    spb = 60.0 / bpm
    beats = 8
    n = int((beats * spb + 1) * SR)
    other = np.zeros(n, np.float32)
    render_bass(other, [(midi("E2"), 4), (midi("F2"), 4)], bpm, 0, vol=0.22, gate=1.0)
    render_drums(other, ["k...k...........", "k...k..........."], bpm, 0, vol=0.35)
    # clock tick
    for i in range(8):
        n2 = int(0.03 * SR)
        y = noise(n2, 30000, i) * expdecay(n2, 0.004) * 0.12
        i0 = int(i * spb * SR)
        other[i0:i0 + n2] += y
    return np.stack([other, other], 1), beats * spb


def track_sad():
    bpm = 92
    n = int(5.0 * SR)
    lead = np.zeros(n, np.float32)
    other = np.zeros(n, np.float32)
    notes = parse("G4:1 F#4:1 F4:1 E4:3.5")
    render_lead(lead, notes, bpm, 0, vol=0.2, duty=0.5, gate=0.85, vib=0.9, a=0.01, d=0.1, s=0.8, rel=0.2)
    render_bass(other, parse("G3:1 F#3:1 F3:1 E3:3.5"), bpm, 0, vol=0.25)
    y = lead + other
    return np.stack([y, y], 1), 4.6


def track_sting():
    bpm = 140
    n = int(2.2 * SR)
    lead = np.zeros(n, np.float32)
    render_lead(lead, parse("C6:.25 G5:.25 E5:.25 C5:.75"), bpm, 0, vol=0.2, duty=0.25, vib=0)
    other = np.zeros(n, np.float32)
    render_drums(other, ["....s.s.c......."], bpm, 0, vol=0.4)
    y = lead + other
    return np.stack([y, y], 1), 2.0


def track_fanfare():
    bpm = 160
    n = int(3.0 * SR)
    lead = np.zeros(n, np.float32)
    other = np.zeros(n, np.float32)
    render_lead(lead, parse("C5:.33 E5:.33 G5:.34 C6:1 G5:.5 C6:1.5"), bpm, 0, vol=0.2, duty=0.25)
    render_lead(other, parse("E4:.33 G4:.33 C5:.34 E5:1 D5:.5 E5:1.5"), bpm, 0, vol=0.1, duty=0.5)
    render_bass(other, parse("C3:1 G2:1 C3:2"), bpm, 0, vol=0.3)
    render_drums(other, ["k.s.k.s.c......."], bpm, 0, vol=0.4)
    y = lead + other
    return np.stack([y, y], 1), 2.6


TRACKS = {
    "main": lambda: track_main(150, "AB"),
    "mainA": lambda: track_main(150, "A"),
    "hustle": lambda: track_main(172, "B"),
    "night": lambda: track_night(),
    "scheme": lambda: track_scheme(),
    "tempt": lambda: track_tempt(),
    "dawn": lambda: track_dawn(),
    "panic": lambda: track_panic(),
    "tension": lambda: track_tension(),
    "sad": lambda: track_sad(),
    "sting": lambda: track_sting(),
    "fanfare": lambda: track_fanfare(),
}
ONESHOT = {"sad", "sting", "fanfare"}
_tc = {}


def get_track(name):
    if name not in _tc:
        _tc[name] = TRACKS[name]()
    return _tc[name]


# ------------------------------------------------------------ SFX
def sfx(name, **kw):
    r = np.random.RandomState(abs(hash(name)) % 1000 + kw.get("seed", 0))
    if name.startswith("blip_"):
        who = name[5:]
        n = int(0.035 * SR)
        e = expdecay(n, 0.012)
        p = kw.get("pitch", 0)
        if who == "clawd":
            f = [523, 587, 659, 587][p % 4]
            y = pulse(f, n, 0.5) * e * 0.07
        elif who == "codex":
            f = [880, 988, 1047, 932][p % 4]
            y = pulse(f, n, 0.125) * e * 0.06
        elif who == "me":
            f = [330, 370, 392][p % 3]
            y = tri(f, n) * e * 0.14
        elif who == "buyer":
            f = [740, 784, 698][p % 3]
            y = pulse(f, n, 0.25) * e * 0.06
        else:
            y = pulse(220, n, 0.5) * e * 0.06
        return y
    if name == "coin":
        n1, n2 = int(0.07 * SR), int(0.35 * SR)
        y = np.concatenate([pulse(988, n1, 0.25) * 0.8, pulse(1319, n2, 0.25) * expdecay(n2, 0.12)])
        return y * 0.16
    if name == "error":
        n1, g, n2 = int(0.11 * SR), int(0.04 * SR), int(0.2 * SR)
        y = np.concatenate([pulse(196, n1, 0.5), np.zeros(g), pulse(147, n2, 0.5) * env(n2, 0.001, 0.1, 0.8, 0.05)])
        return y.astype(np.float32) * 0.16
    if name == "ding":
        n = int(0.6 * SR)
        y = (pulse(1047, n, 0.25) * 0.6 + tri(2093, n) * 0.4) * expdecay(n, 0.15)
        return y * 0.14
    if name == "msg":
        n1, n2 = int(0.05 * SR), int(0.12 * SR)
        y = np.concatenate([pulse(784, n1, 0.25), pulse(1047, n2, 0.25) * expdecay(n2, 0.05)])
        return y * 0.11
    if name == "msg2":
        n1, n2 = int(0.05 * SR), int(0.12 * SR)
        y = np.concatenate([pulse(1047, n1, 0.5), pulse(784, n2, 0.5) * expdecay(n2, 0.05)])
        return y * 0.09
    if name == "stamp":
        n = int(0.35 * SR)
        tt = np.arange(n) / SR
        y = tri(60 + 80 * np.exp(-tt * 30), n) * expdecay(n, 0.09) * 0.9
        y += noise(n, 6000, 2) * expdecay(n, 0.03) * 0.6
        return y * 0.3
    if name == "whoosh":
        n = int(0.35 * SR)
        rate = np.linspace(3000, 16000, n)
        ph = np.cumsum(rate / SR).astype(np.int64)
        y = NOISE[ph % len(NOISE)] * np.sin(np.linspace(0, math.pi, n)) ** 2
        return y.astype(np.float32) * 0.12
    if name == "jump":
        n = int(0.16 * SR)
        y = pulse(np.linspace(300, 900, n), n, 0.25) * env(n, 0.002, 0.05, 0.7, 0.02, n - 800)
        return y * 0.1
    if name == "pop":
        n = int(0.09 * SR)
        y = pulse(np.geomspace(400, 1400, n), n, 0.5) * expdecay(n, 0.04)
        return y * 0.1
    if name == "land":
        n = int(0.08 * SR)
        return noise(n, 4000, 4) * expdecay(n, 0.02) * 0.2
    if name == "chime":
        out = []
        for i, f in enumerate([523, 659, 784, 1047, 1319]):
            n = int(0.07 * SR)
            out.append(pulse(f, n, 0.25) * 0.8)
        n = int(0.5 * SR)
        out.append(pulse(1568, n, 0.25) * expdecay(n, 0.15))
        return np.concatenate(out).astype(np.float32) * 0.12
    if name == "select":
        n = int(0.04 * SR)
        return pulse(1200, n, 0.5) * expdecay(n, 0.015) * 0.1
    if name == "click":
        n = int(0.02 * SR)
        return noise(n, 30000, 9) * expdecay(n, 0.004) * 0.25
    if name == "typing":
        dur = kw.get("dur", 1.0)
        n = int(dur * SR)
        y = np.zeros(n, np.float32)
        t = 0.0
        while t < dur - 0.03:
            k = int(0.015 * SR)
            i0 = int(t * SR)
            y[i0:i0 + k] += noise(k, r.uniform(18000, 40000), r.randint(0, 99)) * expdecay(k, 0.003) * r.uniform(0.12, 0.25)
            t += r.uniform(0.04, 0.11) / kw.get("speed", 1.0)
        return y
    if name == "glitch":
        dur = kw.get("dur", 0.5)
        n = int(dur * SR)
        y = np.zeros(n, np.float32)
        t = 0
        while t < n:
            k = r.randint(int(0.01 * SR), int(0.06 * SR))
            if r.rand() < 0.5:
                y[t:t + k] = noise(min(k, n - t), r.uniform(2000, 30000), r.randint(0, 99)) * 0.3
            else:
                y[t:t + k] = pulse(r.uniform(80, 2000), min(k, n - t), 0.5) * 0.15
            t += k
        return y
    if name == "disconnect":
        n = int(0.8 * SR)
        y = pulse(np.geomspace(900, 60, n), n, 0.5) * np.linspace(1, 0, n) * 0.14
        return y
    if name == "scratch":
        n = int(0.45 * SR)
        tt = np.arange(n) / SR
        rate = 6000 + 5000 * np.sin(tt * 2 * math.pi * 7)
        ph = np.cumsum(rate / SR).astype(np.int64)
        y = NOISE[ph % len(NOISE)] * np.linspace(1, 0, n) * 0.3
        y += pulse(np.linspace(600, 120, n), n, 0.5) * np.linspace(1, 0, n) * 0.12
        return y.astype(np.float32)
    if name == "snore":
        n = int(2.4 * SR)
        tt = np.arange(n) / SR
        amp = np.clip(np.sin(tt / 2.4 * 2 * math.pi - math.pi / 2) * 0.5 + 0.5, 0, 1) ** 2
        lo = noise(n, 900, 6)
        y = (lo * 0.5 + tri(70 + 10 * np.sin(tt * 30), n) * 0.3) * amp
        return y.astype(np.float32) * 0.18
    if name == "alarm":
        dur = kw.get("dur", 1.6)
        n = int(dur * SR)
        y = np.zeros(n, np.float32)
        for k in range(int(dur / 0.25)):
            if k % 4 == 3:
                continue
            m = int(0.1 * SR)
            i0 = int(k * 0.25 * SR)
            y[i0:i0 + m] += pulse(2093, min(m, n - i0), 0.5)[:min(m, n - i0)] * 0.09
        return y
    if name == "tick":
        n = int(0.03 * SR)
        return noise(n, 30000, 3) * expdecay(n, 0.004) * 0.15
    if name == "powerup":
        out = []
        for f in [262, 330, 392, 523, 659, 784, 1047]:
            m = int(0.045 * SR)
            out.append(pulse(f, m, 0.25))
        return np.concatenate(out).astype(np.float32) * 0.1
    if name == "cash":
        n = int(0.5 * SR)
        y = noise(n, 26000, 12) * expdecay(n, 0.05) * 0.3
        m = int(0.4 * SR)
        y[int(0.05 * SR):int(0.05 * SR) + m] += (pulse(1568, m, 0.25) + pulse(2093, m, 0.25)) * expdecay(m, 0.1) * 0.25
        return y * 0.5
    if name == "fail":
        n = int(0.4 * SR)
        y = pulse(np.geomspace(500, 150, n), n, 0.5) * env(n, 0.002, 0.1, 0.7, 0.05, n - 2000)
        return y * 0.12
    if name == "shutter":
        n = int(0.12 * SR)
        y = noise(n, 20000, 13) * (expdecay(n, 0.01) + 0.5 * np.roll(expdecay(n, 0.01), int(0.06 * SR)))
        return y * 0.25
    if name == "birds":
        dur = kw.get("dur", 3.0)
        n = int(dur * SR)
        y = np.zeros(n, np.float32)
        t = 0.2
        while t < dur - 0.3:
            for j in range(r.randint(2, 4)):
                m = int(0.06 * SR)
                f0 = r.uniform(2500, 3800)
                f = np.linspace(f0, f0 * r.uniform(1.2, 1.5), m)
                ph = np.cumsum(f / SR)
                i0 = int((t + j * 0.08) * SR)
                if i0 + m < n:
                    y[i0:i0 + m] += (np.sin(2 * math.pi * ph) * np.sin(np.linspace(0, math.pi, m))).astype(np.float32) * 0.06
            t += r.uniform(0.5, 1.2)
        return y
    if name == "heart":
        n = int(0.5 * SR)
        y = np.zeros(n, np.float32)
        for d in (0, 0.18):
            m = int(0.12 * SR)
            i0 = int(d * SR)
            y[i0:i0 + m] += tri(np.linspace(80, 50, m), m) * expdecay(m, 0.04) * 0.5
        return y * 0.5
    if name == "slide":
        n = int(0.3 * SR)
        y = pulse(np.linspace(300, 700, n), n, 0.125) * 0.05 + noise(n, 8000, 5) * 0.03
        return y.astype(np.float32)
    if name == "notif":
        n1, n2 = int(0.08 * SR), int(0.25 * SR)
        y = np.concatenate([tri(1319, n1) * 0.8, tri(1760, n2) * expdecay(n2, 0.1)])
        return y.astype(np.float32) * 0.2
    if name == "count":
        n = int(0.03 * SR)
        return pulse(1600, n, 0.5) * expdecay(n, 0.01) * 0.05
    if name == "boom":
        n = int(0.9 * SR)
        tt = np.arange(n) / SR
        y = noise(n, 3000, 14) * expdecay(n, 0.25) * 0.5 + tri(50 + 60 * np.exp(-tt * 10), n) * expdecay(n, 0.3) * 0.6
        return y * 0.35
    if name == "zip":
        n = int(0.12 * SR)
        y = pulse(np.geomspace(1500, 300, n), n, 0.25) * expdecay(n, 0.05)
        return y * 0.09
    raise KeyError(name)


# ------------------------------------------------------------ mixdown
def mixdown(total, music_cues, sfx_events):
    """music_cues: sorted [(t, name, opts)], each plays until next cue. sfx: [(t,name,opts)]"""
    n = int((total + 1.0) * SR)
    mus = np.zeros((n, 2), np.float32)
    fx = np.zeros((n, 2), np.float32)
    cues = sorted(music_cues, key=lambda c: c[0])
    for i, (t, name, opts) in enumerate(cues):
        if name == "stop":
            continue
        t_end = cues[i + 1][0] if i + 1 < len(cues) else total
        if opts.get("until") is not None:
            t_end = min(t_end, opts["until"])
        y, loop_len = get_track(name)
        seglen = t_end - t
        off = opts.get("offset", 0.0)
        if name in ONESHOT:
            seg = y[int(off * SR):]
            seglen = min(seglen, len(seg) / SR)
        else:
            L = int(loop_len * SR)
            need = int((seglen + off + 1) * SR)
            reps = need // L + 2
            body = np.zeros((reps * L + len(y), 2), np.float32)
            for k in range(reps):
                body[k * L:k * L + len(y)] += y
            seg = body[int(off * SR):]
        m = int(seglen * SR)
        seg = seg[:m].copy()
        nxt = cues[i + 1][2] if i + 1 < len(cues) else {}
        fo = int(nxt.get("xfade", opts.get("fade_out", 0.25)) * SR)
        if fo and len(seg) > fo:
            seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
        fi = int(opts.get("fade_in", 0.0) * SR)
        if fi:
            seg[:fi] *= np.linspace(0, 1, fi)[:, None]
        i0 = int(t * SR)
        k = min(len(seg), n - i0)
        mus[i0:i0 + k] += seg[:k] * opts.get("vol", 1.0)
    cache = {}
    for (t, name, opts) in sfx_events:
        key = (name, tuple(sorted((k, v) for k, v in opts.items() if k != "vol")))
        if key not in cache:
            cache[key] = sfx(name, **{k: v for k, v in opts.items() if k != "vol"})
        y = cache[key]
        if y.ndim == 1:
            y = np.stack([y, y], 1)
        y = y * opts.get("vol", 1.0)
        i0 = int(t * SR)
        if i0 >= n:
            continue
        k = min(len(y), n - i0)
        fx[i0:i0 + k] += y[:k]
    # light ducking of music under dialogue blips is not needed; mild master
    out = mus * 0.62 + fx
    peak = np.max(np.abs(out)) + 1e-9
    out = np.tanh(out / peak * 1.1) / np.tanh(1.1) * 0.79
    return out[: int(total * SR)]


def write_wav(path, data):
    import wave
    d = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(d.tobytes())
