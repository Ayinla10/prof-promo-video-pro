#!/usr/bin/env python
"""Disk-space guard. Run before any heavy step (installs, model downloads, renders).

  python disk_guard.py --drive C: --min-gb 3 [--drive D: --min-gb 5]      (Windows)
  python disk_guard.py --drive / --min-gb 3                                (macOS / Linux)

Exit 0 = enough space; exit 2 = below a threshold → STOP and tell the user (offer cleanup advice,
never delete anything on your own). Prints free space for every drive checked.
"""
import argparse
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ap = argparse.ArgumentParser()
ap.add_argument("--drive", action="append", required=True, help="drive or path, e.g. C: or D:\\ or /")
ap.add_argument("--min-gb", action="append", type=float, required=True, help="minimum free GB, one per --drive")
a = ap.parse_args()
if len(a.min_gb) != len(a.drive):
    sys.exit("give one --min-gb per --drive")

low = False
for d, m in zip(a.drive, a.min_gb):
    path = d if d.endswith(("\\", "/")) else d + ("\\" if d.endswith(":") else "")
    free = shutil.disk_usage(path).free / 1024**3
    ok = free >= m
    low |= not ok
    print(f"{'✓' if ok else '✗'} {d} free {free:.2f} GB (minimum {m:g} GB)")
if low:
    print("STOP: not enough free space. Ask the user before continuing; suggest safe cleanups (caches, temp, moving the pagefile).")
    sys.exit(2)
