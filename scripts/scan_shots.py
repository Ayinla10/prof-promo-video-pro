#!/usr/bin/env python
"""Find usable shots in a source video. Two outputs, both meant to be LOOKED AT (Read the jpg):

1. Hard cuts (scene detection) — printed timestamps.
2. A timestamped contact sheet sampled every --step seconds (default 3 s; use 0.5 s over a narrow --range to
   pin exact in/out points). Soft crossfades and title cards are NOT caught by scene detection, so always
   confirm the clean range on a 0.5 s sheet before cutting — source timestamps eyeballed from a 3 s sheet were
   off by 1–2 s on a real project.

  python scan_shots.py VIDEO --out sheet.jpg [--step 3] [--range 48-58,64-74] [--width 220]
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg, duration  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--out", required=True)
ap.add_argument("--step", type=float, default=3.0)
ap.add_argument("--range", default="", help="comma list of a-b second ranges; one sheet row per range")
ap.add_argument("--width", type=int, default=220)
ap.add_argument("--threshold", type=float, default=0.18, help="scene-change threshold for hard cuts")
a = ap.parse_args()

from PIL import Image, ImageDraw  # noqa: E402

total = duration(a.video)
cuts = subprocess.run([ffmpeg(), "-hide_banner", "-i", a.video, "-vf", f"select='gt(scene,{a.threshold})',showinfo",
                       "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
import re  # noqa: E402
times = [float(t) for t in re.findall(r"pts_time:([0-9.]+)", cuts)]
print(f"duration {total:.2f} s | hard cuts: " + (" ".join(f"{t:.2f}" for t in times) or "none"))

rows = []
if a.range:
    for r in a.range.split(","):
        s, e = (float(x) for x in r.split("-"))
        n = int((e - s) / a.step) + 1
        rows.append([s + i * a.step for i in range(n)])
else:
    ts = [i * a.step for i in range(int(total / a.step) + 1)]
    per = 10
    rows = [ts[i:i + per] for i in range(0, len(ts), per)]

probe = subprocess.run([ffmpeg(), "-v", "error", "-ss", "0", "-i", a.video, "-frames:v", "1", "-vf", f"scale={a.width}:-2",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
import io  # noqa: E402
W, H = Image.open(io.BytesIO(probe)).size
cols = max(len(r) for r in rows)
sheet = Image.new("RGB", (cols * W, len(rows) * (H + 16)), "white")
d = ImageDraw.Draw(sheet)
with tempfile.TemporaryDirectory() as tmp:
    f = Path(tmp) / "f.png"
    for ri, row in enumerate(rows):
        for ci, t in enumerate(row):
            subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1",
                            "-vf", f"scale={W}:{H}", str(f)])
            if f.exists():
                sheet.paste(Image.open(f), (ci * W, ri * (H + 16)))
            d.text((ci * W + 3, ri * (H + 16) + H + 2), f"{t:g}s", fill="black")
sheet.save(a.out, quality=82)
print(f"→ {a.out}  ({sheet.size[0]}x{sheet.size[1]}) — open it and note clean in/out points")
