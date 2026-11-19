#!/usr/bin/env python
"""Pick and prepare the music bed.

  python music.py analyze track1.mp3 track2.mp3 …     # loudness, rough BPM, energy curve per 5 s
  python music.py bed --in track.mp3 --out assets/audio/bgm-bed.mp3 --length 59 [--offset 0] [--fade-out 3.2]

Choosing: prefer a track that starts soft and builds within ~25 s, stays full to the end of the ad, and is
not mastered louder than ~-12 LUFS (it sits under a voice). Energy digits 0–9 per 5 s make the build visible.
`bed` trims to the exact video length with a short fade-in and a long fade-out, so the music ends WITH the
video instead of being cut. Mount it in audio_meta.json at volume ~0.12–0.16 under narration.
Always tell the user the licence/credit line (e.g. freetouse.com tracks need "Music by … (freetouse.com)").
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg, duration  # noqa: E402

ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
an = sub.add_parser("analyze")
an.add_argument("tracks", nargs="+")
bd = sub.add_parser("bed")
bd.add_argument("--in", dest="inp", required=True)
bd.add_argument("--out", required=True)
bd.add_argument("--length", type=float, required=True)
bd.add_argument("--offset", type=float, default=0.0)
bd.add_argument("--fade-out", type=float, default=3.2)
a = ap.parse_args()

if a.cmd == "analyze":
    import numpy as np
    for f in a.tracks:
        lufs = re.findall(r"I:\s+(-?[0-9.]+) LUFS", subprocess.run([ffmpeg(), "-hide_banner", "-i", f, "-af",
                          "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)
        raw = subprocess.run([ffmpeg(), "-v", "error", "-i", f, "-ac", "1", "-ar", "11025", "-f", "s16le", "-"],
                             capture_output=True).stdout
        x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        hop = 256
        n = len(x) // hop
        rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
        env = np.maximum(0, np.diff(np.log(rms + 1e-4)))
        env -= env.mean()
        m = min(len(env), 20000)
        ac = np.correlate(env[:m], env[:m], "full")[m - 1:]
        fps = 11025 / hop
        lo, hi = int(fps * 60 / 180), int(fps * 60 / 70)
        bpm = 60 * fps / (lo + int(np.argmax(ac[lo:hi])))
        sec = np.array([rms[int(i * fps):int((i + 5) * fps)].mean() for i in range(0, int(len(x) / 11025) - 5, 5)])
        bar = " ".join(str(int(v / sec.max() * 9)) for v in sec)
        print(f"{Path(f).name[:48]:48s} {duration(f):6.1f}s  {lufs[-1] if lufs else '?':>6} LUFS  ~{bpm:5.1f} BPM  energy/5s: {bar}")
else:
    fo = max(0.0, a.length - a.fade_out)
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(a.offset), "-i", a.inp, "-t", str(a.length), "-af",
                    f"afade=t=in:st=0:d=0.6,afade=t=out:st={fo}:d={a.fade_out}", "-c:a", "libmp3lame", "-q:a", "2", a.out],
                   check=True)
    print(f"✓ {a.out} ({duration(a.out):.2f} s, fades in 0.6 s / out {a.fade_out} s)")
