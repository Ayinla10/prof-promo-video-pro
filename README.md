# prof-promo-video-pro — a Claude Code skill

The **Pro** edition of [prof-promo-video](https://github.com/Ayinla10/prof-promo-video): real motion graphics (continuous
camera acts, a hero character, transformations, ambient motion, 300+ synced sound effects), reference-video analysis,
light or dark mode, 9:16-first delivery.

Turns any business's **website URL**, its **own recorded voiceover**, its **photos and footage** and a **music track**
into an exceptionally polished ~60-second motion-designed ad — delivered as a **16:9** MP4 (YouTube, Facebook feed,
website) and a re-designed **9:16** MP4 (TikTok, Reels, Shorts, WhatsApp Status), with burned-in captions and
social-ready loudness. Works for any sector and any language.

Built on [HyperFrames](https://hyperframes.heygen.com) (HTML → video) and refined on real client deliveries.

## Use

In Claude Code:

```
/prof-promo-video-pro make a promo video for <client>, their website is https://…
```

(or just describe the job — the skill also triggers on requests for client video ads / promos.)

## How it works

1. **Discovery interview** — a few rounds of quick multiple-choice questions (goal, audience, language, formats,
   length, prices, call to action, voice, footage, music, style), each option with a suggestion.
2. **Capture** the website (text, contacts, photos, logo, colours, fonts), footage and music.
3. **2–3 creative concepts** with a signature visual motif, colour roles, type and motion personality — you choose.
4. Script → client voiceover → word-accurate timing → storyboard approval → motion design.
5. **Beauty pass** — every scene is scored against a quality bar and redesigned until it passes.
6. Render the 16:9 master, then **re-design** (not crop) the 9:16 version.

## What it automates

| Script | Does |
|---|---|
| `capture_site.py` | Crawls the client site (≤ 25 pages): text, contacts, socials, opening hours, logo, photos (de-duplicated), brand colours, font files, embedded videos; falls back to the installed Chrome when a bot check blocks plain requests |
| `fetch_footage.py` | Downloads footage from Facebook / YouTube / Instagram / TikTok / Drive links (yt-dlp) or copies local files |
| `scan_shots.py`, `cut_clips.py` | Find clean shots (contact sheets + hard-cut detection) and cut silent clips with a verification sheet |
| `split_voice.py` | Cuts the client's voiceover into one clip per scene at its natural pauses |
| `align_words.py` | Exact per-word timings aligned to the client's script (faster-whisper, offline, many languages) → captions + animation cues |
| `fix_cut.py` | Moves one scene boundary to the right pause (e.g. a brand name said on its own) and re-cuts both clips |
| `merge_acts.py` | Groups sentence scenes into 3–5 continuous **acts** (one camera world each) and re-times every word |
| `sfx.py` | Builds a 21-sound procedural library (pops, whooshes, boing, crack, riser, chimes…) and pre-mixes a cue sheet into one synced sound-effects track |
| `music.py` | Compares candidate tracks (loudness, tempo, build-up) and trims a bed to the exact length with fades |
| `videos.py` | Protects frame footage across HyperFrames re-assemblies; fixes duplicate ids |
| `finalize.py` | Renders with temp files on a roomy drive and normalises audio to -14 LUFS |
| `disk_guard.py` | Stops before heavy steps when a drive is nearly full |

Guides: `references/discovery.md` (interview), `art-direction.md` (what makes it beautiful), `quality-bar.md`
(the beauty pass), `script-and-voice.md`, `frame-authoring.md`, `lessons.md`.

## Install

1. [Claude Code](https://claude.com/claude-code).
2. This skill:
   ```bash
   git clone https://github.com/Ayinla10/prof-promo-video ~/.claude/skills/prof-promo-video
   ```
3. The HyperFrames skills it builds on (once per machine):
   ```bash
   npx skills add heygen-com/hyperframes --all
   ```
4. Tools: Node.js ≥ 20, FFmpeg (Windows: `winget install Gyan.FFmpeg`; macOS: `brew install ffmpeg`), Python 3 with
   Pillow and NumPy, Google Chrome. Installed on demand: `yt-dlp`, `faster-whisper`, `playwright`.

Restart Claude Code after installing so the skill appears.

## License

[MIT](LICENSE) — free to use, modify and share; keep the copyright notice.

## Motion graphics, not slides

Every film follows `references/motion-graphics.md`: acts with a travelling camera, a hero character or object that
carries the story, elements that transform into each other, constant ambient motion and 300+ synced sound effects.
Starter: `assets/act-template.html` (camera + ambient writers, fluted-glass light background, orb mascot with
hop/blink/look). Client reference videos are studied frame by frame (`references/reference-analysis.md`).
