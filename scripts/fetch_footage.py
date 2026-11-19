#!/usr/bin/env python
"""Bring client footage into the project: URLs (Facebook, YouTube, Instagram, TikTok, Vimeo, Google Drive
shared links…) via yt-dlp, or local files (copied). Prints title / duration / resolution / uploader so you can
confirm the footage belongs to the client before using it.

  python fetch_footage.py --out <project>/source-videos  URL_or_path [URL_or_path ...] [--names a,b]
  python fetch_footage.py --info-only URL               # metadata only, no download

Needs: pip install yt-dlp (small). Downloads go to --out (keep it on the drive with the most free space).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg, duration  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("sources", nargs="+")
ap.add_argument("--out", default="source-videos")
ap.add_argument("--names", default="", help="comma-separated output base names (default: source-01, …)")
ap.add_argument("--info-only", action="store_true")
a = ap.parse_args()

out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
names = [n.strip() for n in a.names.split(",") if n.strip()]


def ytdlp(*args):
    return subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", *args], capture_output=True, text=True)


if subprocess.run([sys.executable, "-m", "yt_dlp", "--version"], capture_output=True).returncode != 0:
    if any(s.startswith("http") for s in a.sources):
        sys.exit("✗ yt-dlp missing: python -m pip install --no-cache-dir yt-dlp")

report = []
for i, src in enumerate(a.sources):
    name = names[i] if i < len(names) else f"source-{i + 1:02d}"
    if src.startswith("http"):
        info = ytdlp("--skip-download", "--print",
                     "%(title).90s\t%(duration)s\t%(width)sx%(height)s\t%(uploader)s", src)
        meta = (info.stdout.strip().splitlines() or ["?\t?\t?\t?"])[-1].split("\t")
        print(f"• {src}\n  title: {meta[0]} | {meta[1]} s | {meta[2]} | uploader: {meta[3] if len(meta) > 3 else '?'}")
        if info.returncode != 0:
            print("  ✗ metadata failed (private video? login needed?):", info.stderr.strip()[-300:])
            continue
        if a.info_only:
            continue
        r = ytdlp("--no-part", "-f", "bv*+ba/b", "--merge-output-format", "mp4",
                  "--ffmpeg-location", str(Path(ffmpeg()).parent), "-o", str(out / f"{name}.%(ext)s"), src)
        dst = out / f"{name}.mp4"
        if r.returncode != 0 or not dst.exists():
            print("  ✗ download failed:", r.stderr.strip()[-400:])
            continue
    else:
        p = Path(src)
        if not p.exists():
            print(f"✗ not found: {src}")
            continue
        dst = out / f"{name}{p.suffix.lower()}"
        if a.info_only:
            print(f"• {p}  ({duration(p):.1f} s, {p.stat().st_size / 1024**2:.1f} MB)")
            continue
        shutil.copy2(p, dst)
    if not a.info_only:
        d = duration(dst)
        mb = dst.stat().st_size / 1024**2
        print(f"  ✓ {dst}  ({d:.1f} s, {mb:.1f} MB)")
        report.append({"name": name, "source": src, "file": str(dst), "duration_s": round(d, 2)})

if report:
    (out / "footage.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"→ {out / 'footage.json'}")
