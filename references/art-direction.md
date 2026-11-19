# Art direction — what makes a promo look exceptional

Generic motion graphics look generated: centred text on a flat colour, everything fading up at once, five fonts,
random gradients. Studio work looks *designed*: one idea, strict colour roles, confident type, real images treated
with care, motion with a personality, and rhythm. These rules get you there. Apply them when writing concepts
(Phase 0), the `## Video direction` (Phase 3) and every frame (Phase 4).

The motion laws (camera acts, hero, transformations, ambient motion, sound) live in `motion-graphics.md` — beauty
without motion is still a slide.

## 1. One concept, one signature motif

Every ad needs a single visual idea that carries meaning and returns at the end. Derive it from the client's promise:

| Promise / sector | Motif ideas |
|---|---|
| opportunity, education, careers | doors / windows opening onto the world; a staircase or progress bar climbing levels; a pathway line drawn across scenes |
| travel, relocation, hospitality | passport stamps; a boarding-pass ticket; a map pin travelling between scenes |
| food, restaurants | a plate/frame that every dish enters; steam/brush strokes revealing photos; menu-card typography |
| health, beauty, wellness | soft circular masks that breathe open once; before→after split wipes; a calm horizon line |
| construction, real estate, industry | blueprint grid that draws itself, then fills with photos; measuring-tape counters; stacked blocks |
| finance, legal, B2B | a ledger/grid system; numbers counting into place; a single accent line that connects facts |
| retail, fashion | price-tag / label cards; fast editorial cuts with a fixed logo corner; colour-blocked lookbook panels |
| events, churches, NGOs | a light / spotlight sweeping; a ribbon or banner that unfurls; a countdown |
| tech, AI, digital agencies | a character built from the brand mark (an orb with eyes) that does the work; a wipe line that turns old into new; a cracked chat box the hero bursts out of; a word wheel of jobs |
| any brand with a round mark | the mark as a character: it falls into place, the rings pop around it, it becomes the logo |

Rules: the motif appears in frame 1, at least once mid-film, and closes the film around the logo. It is built from
the brand's shapes and colours, not clip-art.

## 2. Colour discipline

- Extract roles from the brand: **ground** (light paper or deep night), **ink** (text), **primary accent** (the one
  loud colour — use it on < 25 % of any frame), **secondary** (supporting surfaces), plus one **neutral sand/grey**.
- Alternate grounds across scenes (light → deep → photo → light…) for rhythm; never three identical grounds in a row.
- Accent = what the eye must hit first (the key word, the CTA, the stat). If everything is accent, nothing is.
- Light mode that looks premium: warm white `#FAFAF7`, 2–3 large brand-colour glow blobs drifting behind fluted
  glass (vertical strips with `backdrop-filter: blur`), ink text, accent words in a brand-gradient pill.
- Texture over gradients: subtle diagonal hatch, grain, or a faint grid on solid regions. No rainbow or "AI purple"
  gradients; a single dark scrim over photos for legibility is fine.
- Check contrast: white on the accent colour and accent on the ground must both be readable at phone size.

## 3. Typography

- One family (the brand's) in 2–3 weights, or brand + one complementary display face if the brand font is weak.
- **Scale contrast is the drama:** hero words 140–260 px (landscape) / 150–230 px (portrait) vs labels 20–30 px in
  tracked uppercase. Avoid the middle sizes that make everything look equal.
- Tight tracking on big display type (-2 to -6 px), generous tracking on small labels (+3 to +8 px).
- Max ~6 words of display text on screen at once; captions carry the rest.
- Line breaks by meaning, never by accident; no orphan words; no text over busy parts of a photo.

## 4. Layout archetypes (vary them)

Rotate between: **full-bleed photo + scrim + bottom-left title** · **hard 40/60 colour split with a photo window** ·
**centred kinetic type on a deep ground** · **card grid / staircase that assembles** · **video window with a label
ribbon** · **stat counters** · **testimonial with name lower-third** · **logo lockup + CTA card**. Never use the same
archetype twice in a row. Keep generous margins (≥ 6 % of width), align to a clear grid, one focal point per frame.

## 5. Images and footage treatment

- Choose photos with real people, faces, emotion and light; rate them in `asset-descriptions.md` and use the best.
- One slow push (scale 1.12 → 1.0) from the entrance per photo; never drift in the back half.
- Footage lives in **windows** with a coloured bar or ribbon — it feels designed, not pasted.
- Crop for the frame: faces in the upper third, nothing important under captions or platform UI.
- Never use a shot with someone else's logo/watermark, a title card, or burned subtitles visible.

## 6. Motion personality

- Pick one personality for the whole film and say it in `## Video direction`: **playful physics** (character
  squash & stretch, back/elastic pops, hops, splats — the TikTok launch-video feel) · **confident** (power3/expo, crisp
  slams, hard cuts) · **warm** (softer power2, longer settles, crossfades) · **premium** (slow, few moves, lots of
  stillness) · **energetic** (fast reveals, more cuts, beat-synced).
- Every element enters on its spoken word (CUE table); stagger, never everything at once.
- Masks and wipes (clip-path) feel more designed than fades; scale-from-blur for the one hero word per scene.
- Hold the final state of each scene still for at least ~0.6 s so it can be read.
- Transitions: a small set, repeated — e.g. push-slide inside a section, zoom-through between sections.

## 7. Rhythm of the film

Plan intensity like music: **hook (bold, fast) → promise (clear) → proof/features (building) → breather (one still,
emotional image) → climax (outcome words / numbers) → calm signature + CTA held ~2 s**. The breather is what makes
the climax land.

## 8. Captions

Brand-coloured caption pill in the bottom band, 2–4 words per group, highlighted current word. They must never
cover faces or key text — plan every frame with the band empty.

## 9. Vertical (9:16) is a redesign

- The first frame must hook alone (big words or a striking image) — people decide in a second.
- Platform UI safe zone: keep key content out of the top ~200 px, the bottom ~380 px (captions sit just above the
  platform's own text) and the right ~120 px (like/share buttons).
- Stack instead of splitting side by side; use portrait crops for full-bleed photos; type stays huge.

## 10. Presets (HyperFrames frame presets) by concept

Bold, energetic, youth, education, retail → `coral` or `bold-poster` (recoloured to brand) · corporate, finance,
B2B → `blue-professional` or `cobalt-grid` · premium, culture, architecture → `cartesian`, `biennale-yellow` or
`editorial-forest` · playful, kids, food → `capsule` or `daisy-days` · tech → `code-editorial`. Always recolour
to the brand and fix display weights; the preset gives structure, the brand gives identity.
