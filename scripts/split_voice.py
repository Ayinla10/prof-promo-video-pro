#!/usr/bin/env python
"""Cut a client-recorded voiceover into one clip per frame, at the natural pauses that match the script.

  python split_voice.py --voice capture/assets/audio/voiceover.mp3 --script SCRIPT.md --project . \
                        [--tail-hold 1.6] [--noise -38] [--min-pause 0.28]

How boundaries are chosen: the recording's pauses are detected (ffmpeg silencedetect); each line of SCRIPT.md
gets an expected end time from its share of syllables; for every boundary the closest detected pause is used
(each pause at most once, kept in order). Cuts land in the MIDDLE of a pause, so no word is clipped.

Writes assets/voice/NN.wav (one per script line = per frame) and voice_split.json with each frame's start /
duration (the last frame gets --tail-hold extra seconds for the end card). Paste those durations into
STORYBOARD.md — they ARE the frame durations (frame starts must equal cumulative durations for captions/voice
to stay in sync). Always print and eyeball the table: a line whose boundary jumped to the wrong pause shows up
as an implausible duration (compare words-per-second across lines).
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg, duration, syllables, script_lines  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--voice", required=True)
ap.add_argument("--script", default="SCRIPT.md")
ap.add_argument("--project", default=".")
ap.add_argument("--tail-hold", type=float, default=1.6)
ap.add_argument("--noise", default="-38")
ap.add_argument("--min-pause", type=float, default=0.28)
a = ap.parse_args()

proj = Path(a.project)
lines = script_lines(proj / a.script if not Path(a.script).is_absolute() else a.script)
total = duration(a.voice)
log = subprocess.run([ffmpeg(), "-hide_banner", "-i", a.voice, "-af", f"silencedetect=noise={a.noise}dB:d={a.min_pause}",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
pauses = [(s, e) for s, e in zip(starts, ends) if s > 0.15 and e < total - 0.05]
speech_start = ends[0] if starts and starts[0] <= 0.05 and ends else 0.0
trail = [s for s in starts if s > total - 1.5]
speech_end = trail[0] if trail else total

n = len(lines)
if len(pauses) < n - 1:
    sys.exit(f"✗ only {len(pauses)} pauses for {n} lines — lower --min-pause (e.g. 0.2) or raise --noise (e.g. -35)")

syl = [sum(syllables(w) for w in l.split()) for l in lines]
cum, acc = [], 0
for s in syl[:-1]:
    acc += s
    cum.append(speech_start + (speech_end - speech_start) * acc / sum(syl))

# Dynamic programming: pick n-1 ordered pauses minimising distance to the expected boundaries.
P = len(pauses)
mid = [(s + e) / 2 for s, e in pauses]
INF = float("inf")
cost = [[INF] * P for _ in range(n - 1)]
back = [[-1] * P for _ in range(n - 1)]
for j in range(P):
    cost[0][j] = abs(mid[j] - cum[0])
for i in range(1, n - 1):
    best, bj = INF, -1
    for j in range(P):
        if j - 1 >= 0 and cost[i - 1][j - 1] < best:
            best, bj = cost[i - 1][j - 1], j - 1
        if best < INF:
            cost[i][j] = best + abs(mid[j] - cum[i])
            back[i][j] = bj
j = min(range(P), key=lambda k: cost[n - 2][k])
chosen = []
for i in range(n - 2, -1, -1):
    chosen.append(j)
    j = back[i][j]
chosen.reverse()
bounds = [0.0] + [round(mid[k], 3) for k in chosen] + [total]

vdir = proj / "assets/voice"
vdir.mkdir(parents=True, exist_ok=True)
frames, t = [], 0.0
print(f"{'fr':>2} {'start':>7} {'dur':>6} {'w/s':>5}  line")
for i in range(n):
    s, e = bounds[i], bounds[i + 1]
    out = vdir / f"{i + 1:02d}.wav"
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", a.voice,
                    "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(out)], check=True)
    dur = round(e - s, 3) + (a.tail_hold if i == n - 1 else 0)
    words = len(lines[i].split())
    frames.append({"frame": i + 1, "start": round(t, 3), "duration": round(dur, 3), "voice": f"assets/voice/{i + 1:02d}.wav",
                   "voice_duration": round(e - s, 3), "line": lines[i]})
    print(f"{i + 1:>2} {t:7.2f} {dur:6.2f} {words / (e - s):5.2f}  {lines[i][:70]}")
    t += dur
(proj / "voice_split.json").write_text(json.dumps({"total_s": round(t, 3), "frames": frames}, indent=1, ensure_ascii=False),
                                     encoding="utf-8")
print(f"total video length {t:.2f} s → voice_split.json  (unused pauses: {P - (n - 1)})")
