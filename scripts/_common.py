"""Shared helpers for the prof-promo-video scripts (ffmpeg discovery, syllables, script parsing)."""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Windows consoles default to cp1252: make ✓ / → / accented text printable.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def find_tool(name):
    """Locate ffmpeg/ffprobe even when a fresh winget install has not reached this shell's PATH yet."""
    exe = shutil.which(name)
    if exe:
        return exe
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / f"{name}.exe",
        Path("C:/ffmpeg/bin") / f"{name}.exe",
        Path("/usr/bin") / name,
        Path("/opt/homebrew/bin") / name,
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    sys.exit(f"✗ {name} not found. Install it (Windows: `winget install Gyan.FFmpeg`, then restart the app).")


FFMPEG = None
FFPROBE = None


def ffmpeg():
    global FFMPEG
    FFMPEG = FFMPEG or find_tool("ffmpeg")
    return FFMPEG


def ffprobe():
    global FFPROBE
    FFPROBE = FFPROBE or find_tool("ffprobe")
    return FFPROBE


def duration(path):
    out = subprocess.run([ffprobe(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def syllables(word):
    """Rough syllable count (vowel groups — fine for Latin-script languages; for others the
    alignment still works, only the estimates for unrecognised words are rougher) — used to estimate speaking time per line."""
    return max(1, len(re.findall(r"[aeiouyàâäéèêëîïôöûùüœæ]+", word.lower())))


def norm(word):
    return re.sub(r"[^\w']", "", word.lower())


def script_lines(script_md):
    """The spoken lines of SCRIPT.md = every 4-space-indented line, in order (one line per frame)."""
    lines = []
    for raw in Path(script_md).read_text(encoding="utf-8").splitlines():
        if raw.startswith("    ") and raw.strip():
            lines.append(raw.strip())
    if not lines:
        sys.exit(f"✗ no indented spoken lines found in {script_md}")
    return lines


def decode_mono(path, rate=16000):
    """Decode any audio with ffmpeg to float32 mono (avoids PyAV version bugs inside faster-whisper)."""
    import numpy as np
    raw = subprocess.run([ffmpeg(), "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(rate), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)
