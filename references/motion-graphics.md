# Motion graphics — not slides

The client test: *"What you are creating is not motion graphics, it's a bunch of frames with text on it."* A scene that
fades text in and then holds still is a **slide**, however pretty. Real motion graphics (the TikTok launch videos
clients send as references) obey five laws. Every act must pass all five before it renders.

## The five laws

1. **Something is always moving.** No element is static for more than ~1 s: blobs drift, cards float (sine), the
   camera breathes (slow push 1.00→1.05), dust rises, a gear turns, a mascot blinks. Holds are *slow motion*, never
   freezes.
2. **One continuous world per act, a camera that travels.** Group the script into 3–5 **acts** (`merge_acts.py`), not
   one frame per sentence. Inside an act the camera pans / dives / whips between *stations* placed on one big world
   (whip pans get a blur pulse). No crossfades inside an act.
3. **Things transform instead of being replaced.** A bar shoots up and becomes the motif line; a paper ledger turns
   into a live dashboard as a wipe line passes over it; a chat box cracks and a character bursts out; the character
   lands in the bullseye and *becomes* the logo. Ask for every new element: what was here before, and what does it
   turn into?
4. **A hero carries the story.** A character (an orb with eyes, a mascot built from the brand mark) or a hero object
   (a line, a dot, a card) that the eye follows through every act. It *acts out* the voiceover: replies to the
   customer, sends the follow-ups, rides the chart, works at night, levels up. Squash & stretch, hops, blinks, looks.
5. **Every visible event has a sound.** Pops on appear, whooshes on camera moves, boing + landing thump on hops,
   ticks for typing, crack, riser before a climax, chimes for success. Built with `scripts/sfx.py` (no downloads).

## Recipes (all GSAP, one paused timeline, seek-safe)

### Camera — one state, one writer
```js
const world = $("#w"), cam = { x: 0, y: 0, s: 1, blur: 0 };
const CX = W / 2, CY = H / 2;                       // 960/540 landscape, 540/960 portrait
const at = (wx, wy, s) => ({ x: CX - s * wx, y: CY - s * wy, s });  // world point → centre of screen
const apply = () => { world.style.transform = `translate(${cam.x}px,${cam.y}px) scale(${cam.s})`;
                      world.style.filter = cam.blur > .05 ? `blur(${cam.blur}px)` : "none"; };
const camTo = (wx, wy, s, d, ease, t) => { const p = at(wx, wy, s); tl.to(cam, { ...p, duration: d, ease, onUpdate: apply }, t); };
const blurPulse = (peak, t, d) => { tl.to(cam,{blur:peak,duration:d/2,ease:"power2.in",onUpdate:apply},t); tl.to(cam,{blur:0,duration:d/2,ease:"power2.out",onUpdate:apply},t+d/2); };
```
`.world{transform-origin:0 0}` and `data-layout-allow-overflow data-layout-allow-occlusion` on it. Legs: drift
(`sine.inOut`, 2–8 s), reposition (`power3.inOut`, 0.7 s), whip (`expo.inOut` 0.5–0.6 s + blurPulse 16–18), dive
into the next act (`power3.in`/`power4.in` to scale 2–70 + blur ramp — the next act starts decelerating out of blur).
Punches (`kick`) on key words: a separate multiplier `punch.v` 1→1.03→1 composed in `apply()`.
**Portrait check:** content placed at world y must land on screen at `CY + s·(y − camY)` — put the camera centre
where the station's content centre is, or everything slides into the caption band (it happened).

### Ambient writer — one tween drives all idle motion
```js
const amb = { t: 0 };
tl.to(amb, { t: DUR, duration: DUR, ease: "none", onUpdate: () => {
  blobs.forEach((b,i)=> b.style.transform = `translate(${Math.sin(amb.t*.35+i)*140}px,${Math.cos(amb.t*.28+i)*120}px)`);
  floaters.forEach((f,i)=> f.style.translate = `0px ${Math.sin(amb.t*1.4+i*2)*10}px`);   // use `translate`, not transform, if GSAP also animates it
}}, 0);
```
Deterministic dust/particles: positions from a `hash(i, k)` function (never `Math.random`).

### Hero character (orb mascot) — see `assets/act-template.html`
Body = radial-gradient sphere + inset shadow; two white oval eyes with dark pupils + highlight; small smile; antenna
in the brand's second colour; soft ellipse shadow under it. Nest: `.orb` (x/y moves) › `.obody` (squash, rotation,
`transform-origin:50% 100%`) so movement and squash never fight.
```js
const hop = (t, x, y, h=170, d=.55) => {      // arc + stretch on take-off + squash on landing
  const top = Math.min(P.y, y) - h;
  tl.to(orb,{x,duration:d,ease:"power1.inOut"},t);
  tl.to(orb,{y:top,duration:d/2,ease:"power2.out"},t); tl.to(orb,{y,duration:d/2,ease:"power2.in"},t+d/2);
  tl.to(body,{scaleX:.86,scaleY:1.16,duration:.1},t); tl.to(body,{scaleX:1,scaleY:1,duration:.2},t+.12);
  tl.to(body,{scaleX:1.28,scaleY:.74,duration:.07},t+d); tl.to(body,{scaleX:1,scaleY:1,duration:.45,ease:"elastic.out(1,.4)"},t+d+.07);
  P.x=x; P.y=y; };
const blink = t => { tl.to(".eye",{scaleY:.1,duration:.06},t); tl.to(".eye",{scaleY:1,duration:.1},t+.08); };
const look  = (t,dx,dy) => tl.to(".eye i",{x:dx,y:dy,duration:.18},t);
```
Give it a job per sentence, a reaction per beat (look at the new card, blink after landing), and an entrance and
exit that hand off to the next act (bursts out of a crack; launches upward; falls into the logo).

### Transformations
- **Wipe-line transform:** two layers in the same place (old grey version / new brand version); a glowing line moves
  and the new layer is clipped to the line (`clipPath: inset(0 W-x 0 0)` or `inset(0 0 H-y 0)` in portrait) — each
  object changes as the line passes it, cued to its word.
- **Grow-into-motif:** an element `scaleY`s far past its box while changing colour, and the camera follows it.
- **Crack-open:** scratch strokes (SVG path draw) → crack lines → glow fills → camera dives in → next act bursts out.
- **Logo assembly:** rings `scale 0→1` staggered `from:"end"`, arrow flies in on `power4.in`, a tiny shake, wordmark
  wiped by `clipPath`. Rebuild brand marks as vector shapes (measure the logo PNG) so they can animate.

### Kinetic type
Per-word rise in masks (`yPercent:115→0`, stagger to the word cues), per-letter pops (`scale 0, rotation −14 →
back.out(2.2)`) for the hero word, accent words in a **gradient pill** (brand colour A→B) or Bricolage-style italic.
"Lagging" letters (one word arrives late) for humour. Word **wheel/selector**: a vertical list in a masked window,
active item ink + dot, others pale, the list `y` steps to each cue. Typewriter text with `tl.call` per character.

### Backgrounds that feel premium (light mode)
Warm white `#FAFAF7` + 2–3 big radial blobs in the brand colours (opacity ~.4–.55) drifting slowly + **fluted
glass**: 12 vertical strips, each `backdrop-filter: blur(26px)` with a soft white highlight gradient. Night/mood shifts
= a gradient overlay fading in (dusk lavender→peach) — still light. Dark mode: near-black + one glow + fine grain.

### Sound design
`python scripts/sfx.py build` once, then a `tools/cues.py` per project:
```python
A = {1: 0.0, 2: 19.946, 3: 36.719, 4: 59.928}   # act start times from voice_split.json
C = []
def c(act, t, s, g=.5): C.append({"t": round(A[act]+t, 3), "s": s, "g": g})
def hop(act, t, d):    c(act, t, "boing", .32); c(act, t+d, "pop_lo", .38)
```
Copy the times straight from the act's GSAP calls (each pop-in, hop, camera move, typed character, crack). Then
`python scripts/sfx.py mix --cues tools/cues.json --length <total> --attach` and re-assemble. Gains: pops .3–.5,
whooshes .4–.6, impacts .3–.7, chimes .3–.6; sfx track volume ~.55, music bed ~.12 under the voice. A 70 s film
had ~340 cues — that density is what makes it feel produced.

## Pitfalls already paid for

- **Initial state peeks in.** `fromTo` renders its *from* state at t=0: a card "off-screen" at `y:1300` is still
  visible at the bottom of a 1920-high frame; a calendar at `y:-400` shows its bottom edge. Push starts fully out
  (`y:±1700`) or start at `opacity:0`.
- **Masks leak.** Text masks with bottom padding show the top edge of a **pill** or the blurred glyphs of a word
  that is "hidden" at `yPercent:115` — use `yPercent:160` + `opacity:0` for pills, and add opacity to blur-ins.
- **Shared class names collide.** A new heading that reuses another heading's class gets that heading's tweens (it
  scattered on screen). Give every animated group its own class.
- **`clip-path` clips `box-shadow`.** A glow/frame on a clipped panel must be a separate sibling element.
- **Overlapping tweens on one property** (a punch inside a long camera push) jump — compose through one writer.
- **No `left/top/width/height` tweens** (lint) — move with transforms; conveyor belts via `translateX` in the writer.
- **Text width:** Geist 800 ≈ 0.55 × font-size × characters; italic display faces need +5 %. Keep portrait lines
  ≤ 920 px and leave the right ~120 px free (platform buttons); 300 px italic hero words overflow 1080 wide.
- **Fonts:** a family with no italic on Google Fonts (Bricolage Grotesque) is synthesised by the browser — declare the
  upright file and set `font-style: italic`; it matches the client's website exactly.
- **Long frames render slower** (backdrop-filter + blur): a 74 s portrait film ≈ 8–10 min. Run renders in the
  background; deliver a compressed preview (`-crf 23`) when the master is over 30 MB for phone viewing.
