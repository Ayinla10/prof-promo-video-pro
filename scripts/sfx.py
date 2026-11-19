#!/usr/bin/env python
"""Procedural sound-effect library + cue mixer — sound design with no downloads and no licences to check.

  python sfx.py build  --project .                       # writes assets/sfx/lib/*.wav (21 sounds, deterministic)
  python sfx.py mix    --project . --cues tools/cues.json --length 73.64 [--attach --volume 0.55]

cues.json = [{"t": 1.23, "s": "pop", "g": 0.5}, ...]  — t is ABSOLUTE seconds in the film, s a library name, g gain.
`mix` pre-mixes every cue into ONE track (assets/sfx/sfx-mix.wav) — the assembler gives each sfx cue its own lane, so
300 separate cues would mean 300 lanes; one pre-mixed track is exact and cheap. `--attach` writes it into
audio_meta.json as a single sfx entry on frame 1 (re-run assemble-index.mjs afterwards).

Library: pop pop_hi pop_lo (appear) · click tick0-3 (UI, typing) · swish (text reveal) · whoosh whoosh_long whoosh_dn
(moves, camera) · riser (build-up into a climax) · impact (land/slam) · splat · boing (character hop) · crack (break) ·
ding notif success (chimes) · sparkle (magic/level-up).

Write the cue sheet as a small Python file next to the frames (see references/motion-graphics.md → Sound design):
one helper per act offset, a `hop()` helper that adds boing + landing pop, and cue times copied from the GSAP
timelines so every visible move has a sound.
"""
import argparse, json, sys, wave
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import _common  # noqa: E402,F401  (UTF-8 console on Windows)

SR = 48000
rng = np.random.default_rng(7)


def env(n, a=0.002, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / max(d, 1e-4))


def sweep(f0, f1, dur, curve=1.0):
    n = int(SR * dur); x = np.linspace(0, 1, n) ** curve
    return np.sin(2 * np.pi * np.cumsum(f0 + (f1 - f0) * x) / SR)


def noise(dur):
    return rng.standard_normal(int(SR * dur))


def lp(x, cut):
    a = np.exp(-2 * np.pi * cut / SR); y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y


def bp_sweep(x, f0, f1):
    n = len(x); y = np.zeros(n); s1 = s2 = 0.0
    for i, v in enumerate(x):
        f = f0 + (f1 - f0) * i / n
        a1 = np.exp(-2 * np.pi * f * 1.6 / SR); a2 = np.exp(-2 * np.pi * f * 0.6 / SR)
        s1 = (1 - a1) * v + a1 * s1; s2 = (1 - a2) * v + a2 * s2; y[i] = s1 - s2
    return y


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


def tone(fr, d, dec, harm=(1, .35, .15)):
    n = int(SR * d); t = np.arange(n) / SR
    return sum(h * np.sin(2 * np.pi * fr * (k + 1) * t) for k, h in enumerate(harm)) * env(n, .002, dec)


def write(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    d = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())


def build(lib):
    S = {}
    for nm, f0, f1, d in [("pop", 700, 280, .09), ("pop_hi", 1100, 520, .07), ("pop_lo", 420, 160, .12)]:
        S[nm] = norm(sweep(f0, f1, d, .5) * env(int(SR * d), .001, d / 3), .8)
    for i in range(4):
        d = .03; n = int(SR * d)
        S[f"tick{i}"] = norm((noise(d) * .5 + np.sin(2 * np.pi * (2400 + 300 * i) * np.arange(n) / SR)) * env(n, .0005, .006), .5)
    d = .05; n = int(SR * d)
    S["click"] = norm((noise(d) * .4 + np.sin(2 * np.pi * 1800 * np.arange(n) / SR)) * env(n, .0005, .012), .7)
    for nm, d, f0, f1 in [("whoosh", .38, 400, 2600), ("whoosh_long", .7, 300, 3200), ("whoosh_dn", .45, 2800, 300)]:
        t = np.linspace(0, 1, int(SR * d)); S[nm] = norm(bp_sweep(noise(d), f0, f1) * np.sin(np.pi * t) ** 1.6, .75)
    d = 1.3; t = np.linspace(0, 1, int(SR * d))
    S["riser"] = norm(bp_sweep(noise(d), 300, 5000) * t ** 2 * .7 + sweep(200, 900, d, 2) * t ** 2 * .3, .7)
    d = .55; n = int(SR * d)
    S["impact"] = norm(sweep(120, 40, d, .4) * env(n, .001, .16) + lp(noise(d), 900) * env(n, .001, .05) * 3, .9)
    d = .32; n = int(SR * d)
    S["splat"] = norm(lp(noise(d), 1400) * env(n, .002, .07) + sweep(260, 90, d, .6) * env(n, .001, .09) * .6, .8)
    d = .35; n = int(SR * d); t = np.arange(n) / SR
    f = 260 + 320 * (1 - np.exp(-t * 18)) + 25 * np.sin(2 * np.pi * 18 * t)
    S["boing"] = norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .003, .12), .7)
    S["ding"] = norm(tone(1320, 1.0, .3), .6)
    a = tone(988, .5, .14); b = tone(1480, .7, .22); x = np.zeros(int(SR * .85)); x[:len(a)] += a; x[int(SR * .11):int(SR * .11) + len(b)] += b
    S["notif"] = norm(x, .6)
    x = np.zeros(int(SR * 1.1))
    for i, fr in enumerate([523, 659, 784, 1047]):
        s = tone(fr, .6, .18); o = int(SR * .08 * i); x[o:o + len(s)] += s
    S["success"] = norm(x, .6)
    x = np.zeros(int(SR * .7))
    for i in range(9):
        s = tone(2000 + rng.random() * 3000, .18, .05, (1,)); o = int(rng.random() * SR * .5); x[o:o + len(s)] += s
    S["sparkle"] = norm(x, .45)
    d = .4; n = int(SR * d); x = np.zeros(n)
    for i in range(14):
        o = int(rng.random() * n * .7); L = int(SR * .012); x[o:o + L] += noise(.012) * env(L, .0003, .003) * (1 - o / n)
    S["crack"] = norm(x + sweep(180, 60, d, .5) * env(n, .001, .08) * .5, .85)
    d = .22; t = np.linspace(0, 1, int(SR * d))
    S["swish"] = norm(bp_sweep(noise(d), 1800, 5200) * np.sin(np.pi * t) ** 2, .45)
    for k, v in S.items():
        write(lib / f"{k}.wav", v)
    print("✓ library:", " ".join(sorted(S)))


def load(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767


def mix(proj, cues_path, length, attach, volume):
    lib = proj / "assets/sfx/lib"
    if not lib.exists():
        build(lib)
    cues = json.load(open(proj / cues_path, encoding="utf-8"))
    buf = np.zeros(int(SR * length) + SR); cache = {}
    for c in cues:
        f = lib / f"{c['s']}.wav"
        if not f.exists():
            sys.exit(f"✗ unknown sound '{c['s']}'")
        x = cache.setdefault(c["s"], load(f)); o = int(SR * c["t"])
        if o >= len(buf):
            continue
        seg = x[: len(buf) - o] * c.get("g", .5); buf[o:o + len(seg)] += seg
    buf = buf[: int(SR * length)]
    peak = np.max(np.abs(buf)) or 1
    if peak > .95:
        buf = buf / peak * .95
    out = proj / "assets/sfx/sfx-mix.wav"; write(out, buf)
    print(f"✓ mixed {len(cues)} cues → {out.relative_to(proj)} ({length:.2f} s)")
    if attach:
        p = proj / "audio_meta.json"; d = json.load(open(p, encoding="utf-8"))
        d["sfx"] = [{"frame": 1, "file": "assets/sfx/sfx-mix.wav", "offset_s": 0, "duration_s": length, "volume": volume}]
        json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"✓ attached to audio_meta.json (volume {volume}) — now re-run assemble-index.mjs")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "mix"])
    ap.add_argument("--project", default=".")
    ap.add_argument("--cues", default="tools/cues.json")
    ap.add_argument("--length", type=float)
    ap.add_argument("--attach", action="store_true")
    ap.add_argument("--volume", type=float, default=0.55)
    a = ap.parse_args(); proj = Path(a.project)
    if a.cmd == "build":
        build(proj / "assets/sfx/lib")
    else:
        if not a.length:
            sys.exit("✗ --length (total film seconds) is required for mix")
        mix(proj, a.cues, a.length, a.attach, a.volume)
