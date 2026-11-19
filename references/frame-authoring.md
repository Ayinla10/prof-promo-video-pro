# Frame authoring — the rules that make frames pass lint and render correctly

Start every frame from `assets/frame-template.html` (copy, rename ids/classes, fill in). The structural law comes from
`hyperframes/references/frame-worker-core.md`; this file is the practical checklist.

## Skeleton

- The file is ONE bare `<template>…</template>`. Inside it: the GSAP `<script src>`, the `<style>` (with its own
  `@font-face` for every weight used, `src:url("assets/fonts/…woff2")` project-root relative), the root
  `<div id="root" data-composition-id="NN-name" data-width data-height>`, and the timeline `<script>`.
- Style the root via `#root` only (a class on the root is dropped at render → unstyled scene).
- Full-bleed grounds are their own `class="clip"` element (`data-start="0" data-duration="<frame dur>"
  data-track-index="0"`), never a background on `#root`. Give every clip an `id` (Studio + lint warn otherwise).
- Prefix every class/id with the frame (`f05-…`) — all frames share one document at render time.
- Wrap the timeline script in an IIFE. Top-level `const tl` in ten frames = "already declared" crash.
- One paused timeline: `const tl = gsap.timeline({ paused: true }); … window.__timelines["NN-name"] = tl;`

## Timing — the CUE table

Put the frame's spoken cue times at the top of the script and drive every reveal from it:

```js
const CUE = { parler: 1.24, anglais: 1.54, ouvrir: 2.32 };   // from align_words.py (frame-relative seconds)
tl.fromTo(".f01-w1", { opacity: 0, yPercent: 50 }, { opacity: 1, yPercent: 0, duration: 0.5, ease: "power3.out" }, CUE.parler - 0.12);
```

Re-timing later = edit one line. Reveal each element ~0.1 s before its word; never dump everything at t=0, and fill
the opening second with something (a kicker label, a drawing line) so a frame never starts empty.

## Motion rules that bite

- Entrances use `fromTo` (seek-safe). For "hidden until later" with several tweens on one element, use `tl.set(...)`
  at 0 plus `immediateRender:false` on later fromTos, or lint warns about repeated fromTo baselines.
- Smooth `power3.out` / `expo.out` for type and camera; `back.out` / `elastic.out` only for playful pops and the
  hero character's squash & stretch (never on the camera). Finite `repeat`/`yoyo` is fine; no `repeat:-1`, no
  `Math.random` (use a `hash(i,k)` function), no CSS animations.
- **Never tween `letterSpacing`/width/height/top/left** (lint error: snaps to pixels). Animate x/y/scale/opacity/
  clipPath/filter instead.
- A child with `z-index:-1` (highlight bands) needs `isolation:isolate` on its parent.
- Don't put a CSS `transform` on something GSAP also transforms.
- Count-ups: initial text must be the start value (`0`), not the final number.
- Text-swap via `tl.set(el, {textContent})` is fine (typewriter, slot cycles).
- Exit motion only in the final frame (a 0.6 s fade to the brand's dark colour at the end).

## Real footage in a frame

Declare it frame-locally; the assembler hoists it to the root:

```html
<video data-frame-video="approved" src="assets/clip.mp4" muted playsinline
  data-start="5.15" data-duration="0.85" data-track-index="4"
  data-frame-video-x="1110" data-frame-video-y="150" data-frame-video-width="690" data-frame-video-height="560"
  data-frame-video-fit="cover"></video>
```

- Geometry is in canvas pixels; the hoisted video renders **on top of** the frame, so nothing (ribbons, labels) may
  overlap its rectangle — put labels outside it.
- It pops in on its `data-start`: draw a panel (colour block + accent bar) that wipes open on the cue first, and start
  the video ~0.2 s after the wipe completes, inside the same rectangle → reads as "footage appears in the window".
- Two clips in one window = consecutive `data-start`s (hard cut on a spoken word).
- `cover` crops from the centre (no object-position) — vertical source clips with burned subtitles in the lower half
  will show them; prefer horizontal clips or plan a cover.
- Clip length ≥ its `data-duration`.
- The assembler removes these tags from the frame file: `videos.py save` before the first assembly, `videos.py
  restore` before every re-assembly, `videos.py dedupe` after each assembly.

## Acts (multi-station frames)

One frame per **act** (see `motion-graphics.md`): a `.world` wrapper holds every station; the camera writer moves it;
idle motion comes from one ambient tween; build repeated elements (bubbles, tiles, wall of cards) in JS at setup from
fixed coordinates, never measured at tween time. Prefix every class per act (`b1-`, `b2-`…) and never let two
different groups share an animated class.

## Layout

- Landscape 1920×1080: all content above y ≈ 900 (captions own the bottom ~17%). Margins ~120 px.
- Portrait 1080×1920: all content above y ≈ 1600; margins ~80 px; anchor the hero high (0.15–0.35 H); stack
  vertically instead of side-by-side (split screens become top/bottom); type sizes stay big (display 110–200 px).
  Long words: estimate width ≈ font-size × 0.68 × letters and keep under ~920 px.
- Real photos: one slow push from entrance (scale 1.12 → 1.0) — never a late drift.
- Hard-edged colour regions + one ribbon-tag device + one signature motif give consistency across frames.

## Verify

`npx hyperframes lint` (0 errors), `inspect` (fix text_box_overflow on real copy), `snapshot --at …` and LOOK:
text cut off, a word reveal missing at its cue, wrong shot in a video window, empty frames.
