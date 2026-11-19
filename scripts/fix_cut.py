#!/usr/bin/env python
"""Move one scene boundary of a split voiceover to a better pause, and re-cut both clips.

  python fix_cut.py --project . --voice source/voiceover.mp3 --scene 12 --at 65.06
  then re-run align_words.py (same args as before)

Why: split_voice.py picks the pause nearest each line's expected end; when a short word sits alone between two
pauses (a brand name like "TEDMARK." said on its own), the cut can land on the wrong side of it — the word ends up
in the previous scene and align_words reports e.g. "matched 5/6" or a word at 0.00. Find the real pauses with
  ffmpeg -ss <start> -t 8 -i voice.mp3 -af silencedetect=n=-40dB:d=0.12 -f null -
and pass the MIDDLE of the pause BEFORE the word as --at. --scene N moves the boundary between scene N and N+1.
"""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--project", default=".")
ap.add_argument("--voice", required=True)
ap.add_argument("--scene", type=int, required=True, help="boundary between this scene and the next")
ap.add_argument("--at", type=float, required=True, help="new cut time, absolute seconds")
a = ap.parse_args()
proj = Path(a.project); p = proj / "voice_split.json"
d = json.load(open(p, encoding="utf-8")); F = d["frames"]
x, y = F[a.scene - 1], F[a.scene]
end = y["start"] + y["duration"]
if not (x["start"] < a.at < end):
    sys.exit(f"✗ --at {a.at} is outside scenes {a.scene}–{a.scene + 1} ({x['start']:.2f}–{end:.2f})")
x["duration"] = x["voice_duration"] = round(a.at - x["start"], 3)
y["start"] = round(a.at, 3); y["duration"] = y["voice_duration"] = round(end - a.at, 3)
json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for f in (x, y):
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(f["start"]), "-t", str(f["duration"]), "-i", a.voice,
                    "-ar", "48000", "-ac", "1", str(proj / f["voice"])], check=True)
    print(f"  scene {f['frame']}: start {f['start']:.3f}  dur {f['duration']:.3f}")
print("✓ boundary moved — now re-run align_words.py")
