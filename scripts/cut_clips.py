#!/usr/bin/env python
"""Cut silent, web-friendly clips from source footage and verify them visually.

  python cut_clips.py --spec clips.json --project <project-dir>

clips.json = [ {"src": "source-videos/fb-temoignage.mp4", "start": 51.6, "dur": 3.4, "name": "classe-attentive"}, … ]

Writes each clip to capture/assets/videos/<name>.mp4 AND assets/<name>.mp4 (h264, yuv420p, no audio,
faststart), then a verification sheet (first / middle / last frame of every clip) at
capture/extracted/clips-check.jpg — READ IT: every frame must be the intended clean shot (no crossfade,
no title card, no burned-in subtitles unless you plan to cover them).
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--spec", required=True)
ap.add_argument("--project", default=".")
ap.add_argument("--crf", type=int, default=20)
a = ap.parse_args()

proj = Path(a.project)
spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
(proj / "capture/assets/videos").mkdir(parents=True, exist_ok=True)
(proj / "assets").mkdir(parents=True, exist_ok=True)
(proj / "capture/extracted").mkdir(parents=True, exist_ok=True)

made = []
for c in spec:
    src = proj / c["src"] if not Path(c["src"]).is_absolute() else Path(c["src"])
    dst = proj / "capture/assets/videos" / f"{c['name']}.mp4"
    r = subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(c["start"]), "-t", str(c["dur"]), "-i", str(src), "-an",
                        "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(dst)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"✗ {c['name']}: {r.stderr.strip()[-300:]}")
        continue
    shutil.copy2(dst, proj / "assets" / dst.name)
    made.append((c, dst))
    print(f"✓ {dst.name}  {c['start']}s +{c['dur']}s")

from PIL import Image, ImageDraw  # noqa: E402
W, H = 256, 144
sheet = Image.new("RGB", (3 * W, len(made) * (H + 16)), "white")
d = ImageDraw.Draw(sheet)
with tempfile.TemporaryDirectory() as tmp:
    f = Path(tmp) / "f.png"
    for r, (c, dst) in enumerate(made):
        for k, t in enumerate([0.05, c["dur"] / 2, max(0.05, c["dur"] - 0.15)]):
            subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(dst), "-frames:v", "1",
                            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2", str(f)])
            if f.exists():
                sheet.paste(Image.open(f), (k * W, r * (H + 16)))
        d.text((4, r * (H + 16) + H + 2), c["name"], fill="black")
out = proj / "capture/extracted/clips-check.jpg"
sheet.save(out, quality=82)
print(f"→ verify: {out}")
