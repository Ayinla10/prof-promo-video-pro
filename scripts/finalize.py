#!/usr/bin/env python
"""Render the assembled project and deliver a social-ready MP4.

  python finalize.py --project . --out renders/CLIENT-pub-16x9.mp4 [--temp <roomy-drive>/hf-temp] [--lufs -14] [--quality high]

1. Checks disk space (render temp + output need ~1.5 GB headroom; C: is never used for temp if --temp is set).
2. Runs `npx hyperframes render --skill=product-launch-video` with TEMP/TMP pointed at --temp.
3. Measures loudness and re-encodes ONLY the audio to --lufs (default -14 LUFS, true peak -1.5 dB — the level
   Facebook / TikTok / Instagram / YouTube normalise to; HyperFrames renders land around -21 LUFS, which sounds
   weak next to other posts). Video stream is copied untouched.
4. Prints resolution, duration, size and final loudness.

A 60 s 1080p render takes ~6–12 min on a laptop CPU — run it in the background and wait for the notification.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg, ffprobe, find_tool  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--project", default=".")
ap.add_argument("--out", required=True)
ap.add_argument("--temp", default="")
ap.add_argument("--lufs", type=float, default=-14)
ap.add_argument("--quality", default="high")
ap.add_argument("--skip-render", action="store_true", help="only normalise an existing raw render")
a = ap.parse_args()

proj = Path(a.project).resolve()
out = (proj / a.out) if not Path(a.out).is_absolute() else Path(a.out)
out.parent.mkdir(parents=True, exist_ok=True)
raw = out.with_name(out.stem + ".raw.mp4")

env = dict(os.environ)
if a.temp:
    Path(a.temp).mkdir(parents=True, exist_ok=True)
    env["TEMP"] = env["TMP"] = env["TMPDIR"] = a.temp
    free = shutil.disk_usage(a.temp).free / 1024**3
    if free < 2:
        sys.exit(f"✗ only {free:.1f} GB free on the temp drive — free space first")
env["PATH"] = str(Path(find_tool("ffmpeg")).parent) + os.pathsep + env.get("PATH", "")

if not a.skip_render:
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    cmd = [npx, "--yes", "hyperframes", "render", "--skill=product-launch-video", "--quality", a.quality, "--output", str(raw)]
    print("▶", " ".join(cmd))
    r = subprocess.run(cmd, cwd=proj, env=env)
    if r.returncode != 0 or not raw.exists():
        sys.exit("✗ render failed — read the output above; fix the frame named in the error, rerun lint, then retry")

subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af", f"loudnorm=I={a.lufs}:TP=-1.5:LRA=7",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)], check=True)
info = subprocess.run([ffprobe(), "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "csv=p=0",
                       str(out)], capture_output=True, text=True).stdout.split()
lufs = re.findall(r"I:\s+(-?[0-9.]+) LUFS", subprocess.run([ffmpeg(), "-hide_banner", "-i", str(out), "-af",
                  "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True).stderr)
print(f"✓ {out}\n  {' / '.join(info)} | {out.stat().st_size / 1024**2:.1f} MB | loudness {lufs[-1] if lufs else '?'} LUFS")
