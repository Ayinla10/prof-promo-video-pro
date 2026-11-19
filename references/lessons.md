# Lessons already paid for (pitfalls and their fixes)

Collected on a real 60 s client ad delivered in 16:9 and 9:16. Each is handled by a script or a rule in this skill.

1. **Free local TTS voice rejected by the client** → default to a client-recorded (or client-approved AI) voice; the
   skill writes the script and recording tips. The recording's wording becomes the final script.
2. **Model download stalled for hours** (Hugging Face's default downloader on a slow connection) → `align_words.py`
   downloads the four faster-whisper files over plain HTTP.
3. **Whole-file transcription skipped 19 s and looped a phrase** → transcribe each per-scene clip separately and align
   to the script text.
4. **Recogniser missed some words** → gaps are filled by syllables over speech time only, and a new sentence's first
   word snaps to the end of the pause before it.
5. **Clips cut from 3-second contact-sheet guesses opened on crossfades or the wrong person** → 0.5 s scans over the
   candidate range + a first/middle/last-frame verification sheet.
6. **Re-assembly silently lost all footage and duplicated ids** → `videos.py save / restore / dedupe`.
7. **Lint error on a letter-spacing tween; a z-index:-1 highlight vanished** → rules in `frame-authoring.md`.
8. **A word overflowed its slot; a decorative wallpaper word read as nonsense** → `inspect` + the beauty pass.
9. **Render audio at -21 LUFS sounded weak on social** → `finalize.py` normalises to -14 LUFS.
10. **System drive nearly full; package/model caches ate gigabytes** → `disk_guard.py`, heavy files on the roomiest
    drive, render temp redirected there.
11. **The vertical version needed a real redesign** (stacked panels, portrait photo crops, safe zones), not a crop.
12. **Website capture done by hand** → `capture_site.py`. Pitfalls it handles: WordPress's default palette outranking
    the brand colours, icon fonts mistaken for brand fonts, `?query` page duplicates, accented URLs, the same photo
    saved as .jpg + .webp + resized copies, course timetables mistaken for opening hours, bot-check pages.
13. **The client asked for no prices and no dates** → ask in the interview; timeless "enrolment/booking open" keeps an
    ad usable for months.
14. **"This is not motion graphics, it's frames with text on it."** One frame per sentence with fade-in text and
    holds was rejected → acts with a travelling camera, a hero character, transformations, constant ambient motion
    and dense sound design (`motion-graphics.md`, `merge_acts.py`, `sfx.py`, `act-template.html`). The rebuilt film:
    *"this is what a motion graphic should look like"*.
15. **Show a motion test before building everything:** render the first act only (`render --end`) and get a yes.
16. **Client reference videos are the brief:** sample them frame by frame (`reference-analysis.md`) and say what you
    learned before proposing concepts.
17. **A cut landed after a brand name said on its own** ("…ordinary. | TEDMARK."): the word went to the wrong scene
    → `fix_cut.py`, then re-align.
18. **The client's domain had expired mid-project** (the site showed a registrar parking page): capture found it.
    Tell the client at once — DNS/hosting fixes are theirs to make; check again before the CTA goes out.
19. **Things peeked in before their entrance** (off-screen starts too close, masked pills, blurred words) and **a
    reused class name animated the wrong heading** — see Pitfalls in `motion-graphics.md`.
20. **Light-mode captions:** a white pill with ink text and the accent on the active word; portrait band raised to
    y 1330 so TikTok/Reels text never covers it (both skins in `assets/`).
21. **Renders over 30 MB can't be sent to phone viewers** → send a `-crf 23` preview, give the master's path.
