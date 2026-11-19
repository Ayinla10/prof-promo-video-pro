#!/usr/bin/env python
"""Merge per-sentence scenes into a few long ACTS, so each act can be ONE continuous camera move.

  python merge_acts.py --project . --groups "1-6,7-8,9-11,12-13"

Run AFTER split_voice.py + align_words.py (and fix_cut.py if a boundary was wrong). For every group it concatenates
the voice clips into assets/voice/actN.wav and rewrites voice_split.json, audio_meta.json and words-by-frame.json
so frame N = act N, with every word re-timed relative to the act start. It also merges the matching SCRIPT.md lines.
Backups of the per-sentence files go to _scenes/ first. Print the act word table and drive each act's CUE times from it.

Grouping rule of thumb: an act = one idea / one place in the story (hook, problem, solution, proof, CTA), 10–25 s.
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--project", default=".")
ap.add_argument("--groups", required=True, help='e.g. "1-6,7-8,9-11,12-13" (1-based scene numbers)')
a = ap.parse_args()
proj = Path(a.project)
groups = []
for part in a.groups.split(","):
    lo, _, hi = part.strip().partition("-")
    groups.append(list(range(int(lo), int(hi or lo) + 1)))

bk = proj / "_scenes"; bk.mkdir(exist_ok=True)
for f in ("voice_split.json", "audio_meta.json", "words-by-frame.json", "SCRIPT.md"):
    if (proj / f).exists():
        shutil.copy2(proj / f, bk / f)

vs = json.load(open(proj / "voice_split.json", encoding="utf-8"))
am = json.load(open(proj / "audio_meta.json", encoding="utf-8"))
wb = json.load(open(proj / "words-by-frame.json", encoding="utf-8"))
F, V, K = vs["frames"], am["voices"], list(wb)
if sum(len(g) for g in groups) != len(F):
    sys.exit(f"✗ groups cover {sum(len(g) for g in groups)} scenes but there are {len(F)}")
nF, nV, nW = [], [], {}
for gi, g in enumerate(groups):
    fs = [F[i - 1] for i in g]; vv = [V[i - 1] for i in g]; base = fs[0]["start"]
    path = f"assets/voice/act{gi + 1}.wav"
    lst = proj / "tools" / "concat.txt"; lst.parent.mkdir(exist_ok=True)
    lst.write_text("".join(f"file '../{x['voice']}'\n" for x in fs))
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(proj / path)], check=True)
    dur = round(sum(x["duration"] for x in fs), 3); words = []
    for x, vx in zip(fs, vv):
        off = round(x["start"] - base, 3)
        words += [{**w, "start": round(w["start"] + off, 3), "end": round(w["end"] + off, 3)} for w in vx["words"]]
    nF.append({"frame": gi + 1, "start": base, "duration": dur, "voice": path, "voice_duration": dur,
               "line": " ".join(x["line"] for x in fs)})
    nV.append({**vv[0], "frame": gi + 1, "path": path, "duration_s": dur, "words": words})
    nW[K[g[0] - 1]] = words
    print(f"ACT {gi + 1}  start {base:.3f}  dur {dur:.3f}\n  " + " ".join(f"{w['text']}@{w['start']}" for w in words))
vs["frames"] = nF; am["voices"] = nV
json.dump(vs, open(proj / "voice_split.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(am, open(proj / "audio_meta.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump(nW, open(proj / "words-by-frame.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
sp = proj / "SCRIPT.md"
if sp.exists():
    t = sp.read_text(encoding="utf-8").split("\n")
    idx = [i for i, l in enumerate(t) if l.startswith("    ") and l.strip()]
    if len(idx) == len(F):
        new = ["    " + " ".join(t[idx[i - 1]].strip() for i in g) for g in groups]
        keep = [l for i, l in enumerate(t) if i not in idx]
        sp.write_text("\n".join(keep[: idx[0]] + new + keep[idx[0]:]) + "\n", encoding="utf-8")
print(f"✓ {len(groups)} acts written (backups in _scenes/). Write one STORYBOARD frame per act with these durations.")
