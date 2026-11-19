#!/usr/bin/env python
"""Keep frame <video> tags safe across re-assemblies, and fix the assembler's duplicate ids.

Background: product-launch-video's assemble-index.mjs HOISTS every approved frame video to index.html and
REWRITES the frame file, replacing each <video> with an "approved frame video hoisted" comment. A second
assembly then silently loses all footage. It also gives both videos of one frame the same id.

  python videos.py save    --project .   # before the FIRST assembly: snapshot every frame's <video> tags
  python videos.py restore --project .   # before EVERY re-assembly: put the tags back into the frame files
  python videos.py dedupe  --project .   # after every assembly: make <video id> unique in index.html
  python videos.py swap    --project . --frame 06-vos-formules --old a.mp4 --new b.mp4   # change a clip

The snapshot lives in frame-videos.json (frame file → list of tags); edit it there to retime or re-place a clip.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ap = argparse.ArgumentParser()
ap.add_argument("cmd", choices=["save", "restore", "dedupe", "swap"])
ap.add_argument("--project", default=".")
ap.add_argument("--frame", default="")
ap.add_argument("--old", default="")
ap.add_argument("--new", default="")
a = ap.parse_args()
proj = Path(a.project)
store = proj / "frame-videos.json"
frames = sorted((proj / "compositions/frames").glob("*.html"))
TAG = re.compile(r"[ \t]*<video\b[^>]*data-frame-video=\"approved\"[^>]*>\s*</video>\n?")
HOIST = re.compile(r"[ \t]*<!-- approved frame video hoisted by assemble-index -->\n?")

if a.cmd == "save":
    data = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {}
    for f in frames:
        tags = [t.strip() for t in TAG.findall(f.read_text(encoding="utf-8"))]
        if tags:
            data[f.name] = tags
    store.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"✓ saved {sum(len(v) for v in data.values())} video tag(s) from {len(data)} frame(s) → {store.name}")

elif a.cmd == "restore":
    if not store.exists():
        sys.exit("✗ no frame-videos.json — run `save` before the first assembly")
    data = json.loads(store.read_text(encoding="utf-8"))
    for name, tags in data.items():
        f = proj / "compositions/frames" / name
        s = f.read_text(encoding="utf-8")
        s = HOIST.sub("", TAG.sub("", s))
        # insert just before the root's closing </div> (the last </div> before the timeline <script>)
        idx = s.rfind("</div>", 0, s.find("<script>", s.find("data-composition-id")))
        if idx <= 0:
            print(f"✗ {name}: could not find the root closing tag — add the tags by hand")
            continue
        s = s[:idx] + "  " + "\n    ".join(tags) + "\n  " + s[idx:]
        f.write_text(s, encoding="utf-8")
        print(f"✓ {name}: {len(tags)} video tag(s) restored")

elif a.cmd == "dedupe":
    idx = proj / "index.html"
    s = idx.read_text(encoding="utf-8")
    seen = {}

    def ren(m):
        i = m.group(1)
        seen[i] = seen.get(i, 0) + 1
        return f'<video id="{i}{"" if seen[i] == 1 else "-" + chr(96 + seen[i])}"'

    s = re.sub(r'<video id="([^"]+)"', ren, s)
    idx.write_text(s, encoding="utf-8")
    print(f"✓ video ids unique ({sum(1 for v in seen.values() if v > 1)} duplicate group(s) fixed)")

elif a.cmd == "swap":
    data = json.loads(store.read_text(encoding="utf-8"))
    key = next(k for k in data if k.startswith(a.frame))
    data[key] = [t.replace(f'src="assets/{a.old}"', f'src="assets/{a.new}"') for t in data[key]]
    store.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"✓ {key}: {a.old} → {a.new} (run restore + re-assemble)")
