#!/usr/bin/env python
"""Exact word timings for each frame's voice clip, aligned to the client's script, + audio_meta.json.

  python align_words.py --project . --lang <en|fr|es|pt|…> [--model-dir <roomy-drive>/models/fw-base]
                        [--bgm assets/audio/bgm-bed.mp3 --bgm-volume 0.14]

Transcribes every assets/voice/NN.wav separately with faster-whisper (short clips are far more reliable than
one long file — the long-file pass hallucinated and skipped 19 s on a real project), then aligns the recognised words to
the script's words with difflib, so caption text is always the client's exact wording. Words the recogniser
missed get syllable-proportional estimates between their neighbours (marked "est").

Writes words-by-frame.json, audio_meta.json (voices with frame-relative words + bgm) and prints a CUE helper
per frame: the start time of every word, to copy into each frame's CUE table.

Model: faster-whisper "base" (~140 MB, multilingual). If --model-dir is missing the script downloads the four
model files with plain HTTP (the Hugging Face xet downloader stalled for hours on a slow connection). Keep the
model on a drive with space. Needs: pip install --no-cache-dir faster-whisper
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ffmpeg, duration, syllables, norm, script_lines, decode_mono  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--project", default=".")
ap.add_argument("--script", default="SCRIPT.md")
ap.add_argument("--lang", default="fr")
ap.add_argument("--model", default="base")
ap.add_argument("--model-dir", default="")
ap.add_argument("--bgm", default="")
ap.add_argument("--bgm-volume", type=float, default=0.14)
a = ap.parse_args()

proj = Path(a.project)
lines = script_lines(proj / a.script)
split = json.loads((proj / "voice_split.json").read_text(encoding="utf-8")) if (proj / "voice_split.json").exists() else None

mdir = Path(a.model_dir) if a.model_dir else Path.home() / ".cache" / f"fw-{a.model}"
if not (mdir / "model.bin").exists():
    mdir.mkdir(parents=True, exist_ok=True)
    base = f"https://huggingface.co/Systran/faster-whisper-{a.model}/resolve/main/"
    for f in ["config.json", "tokenizer.json", "vocabulary.txt", "model.bin"]:
        print(f"↓ {f}")
        urllib.request.urlretrieve(base + f, mdir / f)

from faster_whisper import WhisperModel  # noqa: E402
model = WhisperModel(str(mdir), device="cpu", compute_type="int8")

result, voices = {}, []
for i, line in enumerate(lines, start=1):
    wav = proj / f"assets/voice/{i:02d}.wav"
    segs, _ = model.transcribe(decode_mono(wav), language=a.lang, word_timestamps=True,
                               condition_on_previous_text=False, beam_size=5, initial_prompt=line)
    heard = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    sw = [w for w in line.split() if norm(w)]
    sm = difflib.SequenceMatcher(a=[norm(x) for x in sw], b=[norm(x[0]) for x in heard], autojunk=False)
    times = [None] * len(sw)
    for ai, bi, k in sm.get_matching_blocks():
        for t in range(k):
            times[ai + t] = (round(heard[bi + t][1], 3), round(heard[bi + t][2], 3))
    dur = duration(wav)
    log = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(wav), "-af", "silencedetect=noise=-38dB:d=0.2", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    sil = list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)],
                   [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]))

    def speech_map(t0, t1):
        """Piecewise map from 'speech-only seconds' to clip time between t0 and t1 (skips detected pauses)."""
        segs, cur = [], t0
        for s0, s1 in sil:
            if s1 <= t0 or s0 >= t1:
                continue
            if s0 > cur:
                segs.append((cur, s0))
            cur = max(cur, s1)
        if cur < t1:
            segs.append((cur, t1))
        total = sum(b - a for a, b in segs) or (t1 - t0)

        def at(x):  # x in [0, total]
            for a, b in segs:
                if x <= b - a:
                    return a + x
                x -= b - a
            return t1
        return at, total

    # fill gaps by syllable share between known neighbours, over speech time only
    known = [-1] + [k for k, t in enumerate(times) if t] + [len(sw)]
    for x, y in zip(known, known[1:]):
        if y - x <= 1:
            continue
        t0 = times[x][1] if x >= 0 else 0.05
        t1 = times[y][0] if y < len(sw) else dur - 0.05
        # A narrator pauses after a sentence end: split the gap into sentence chunks and give each chunk the
        # speech between consecutive pauses, so a new sentence's first word starts AFTER the pause.
        idxs = list(range(x + 1, y))
        prev_end_sentence = x >= 0 and re.search(r"[.?!:;]$", sw[x])
        chunks, cur_chunk = [], []
        for k in idxs:
            cur_chunk.append(k)
            if re.search(r"[.?!:;]$", sw[k]) and k != idxs[-1]:
                chunks.append(cur_chunk)
                cur_chunk = []
        chunks.append(cur_chunk)
        inner = [(s0, s1) for s0, s1 in sil if t0 < s0 and s1 < t1]
        if prev_end_sentence and inner and len(inner) >= len(chunks):
            inner = inner[len(inner) - len(chunks):]
            spans = [(inner[0][1], (inner[1][0] if len(inner) > 1 else t1))] +                     [(inner[c][1], inner[c + 1][0] if c + 1 < len(inner) else t1) for c in range(1, len(chunks))]
        elif inner and len(inner) >= len(chunks) - 1 and len(chunks) > 1:
            bounds = [t0] + [v for s0, s1 in inner[:len(chunks) - 1] for v in (s0, s1)] + [t1]
            spans = [(bounds[2 * c], bounds[2 * c + 1]) for c in range(len(chunks))]
        else:
            spans = [(t0, t1)] if len(chunks) == 1 else None
            if spans is None:
                chunks, spans = [idxs], [(t0, t1)]
        for chunk, (c0, c1) in zip(chunks, spans):
            at, speech = speech_map(c0, c1)
            tot = sum(syllables(sw[k]) for k in chunk)
            acc = 0.0
            for k in chunk:
                d = speech * syllables(sw[k]) / tot
                times[k] = (round(at(acc), 3), round(at(acc + d), 3), "est")
                acc += d
    words = []
    for w, t in zip(sw, times):
        item = {"text": w, "start": max(0.0, t[0]), "end": t[1]}
        if len(t) == 3:
            item["est"] = True
        words.append(item)
    hit = sum(1 for w in words if not w.get("est"))
    result[str(i)] = words
    voices.append({"frame": i, "path": f"assets/voice/{i:02d}.wav", "duration_s": round(dur, 3),
                   "words": [{k: v for k, v in w.items() if k != "est"} for w in words]})
    print(f"F{i:02d} matched {hit}/{len(words)} | " + " ".join(f"{w['text']}@{w['start']:.2f}" for w in words))

(proj / "words-by-frame.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
total = split["total_s"] if split else sum(v["duration_s"] for v in voices)
meta = {"tts_provider": "client recording", "voice_id": None, "bgm_pending": False, "voices": voices, "sfx": [],
        "total_duration_s": total, "bgm": None}
if a.bgm:
    meta["bgm"] = {"path": a.bgm, "volume": a.bgm_volume, "query": "client-supplied", "duration_s": total}
(proj / "audio_meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
print("→ words-by-frame.json, audio_meta.json. Low match counts (< 70 %) = check that line was recorded as written.")
