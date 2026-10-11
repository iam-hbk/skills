# Remotion architecture

Patterns that made a code-built film easy to re-cut, re-voice and keep true
to the product. Adapt names to the project; the ideas carry over to any
React-based video tool.

## Contents
- Project layout
- The script is the source of truth
- Timeline from the read
- Cuts on the beat
- The real app on screen
- Taps and measured boxes
- Motion helpers: morphs, logo morphs, 3D networks
- Audio in the composition
- Stills, renders and the pipeline

## Project layout

Keep the film in its own folder (e.g. `video/`) with its own `package.json`,
pinned Remotion version and lockfile, beside the app it advertises:

```
video/
  src/script.ts       scenes: id, narration per language, minimum length, voice delay
  src/copy.ts         on-screen text per language (not narrated)
  src/timeline.ts     script + voice manifest → frames (pure, no React)
  src/scenes/*.tsx    one component per scene; src/scenes/layout.ts shared coordinates
  src/components/     brand mark, phone, morphs, cards
  src/app-ui/         renders the real app inside the film (shadow root + shims)
  src/film/           composition, transitions, sound-effect cues
  public/vo/<lang>/   narration clips + manifest.json
  public/audio/       score master, per-cut conforms, effects
  scripts/            voice, music, audio, stills, timeline export, publishing
```

## The script is the source of truth

`script.ts` holds each scene's narration for every language, its minimum
length (`minSeconds`), an optional per-language minimum (`hold`) to make room
for slower reads or longer animations, and the delay before the line starts.
Everything else (the voice generator, the timeline, the music conformer)
reads from it, so a line change propagates everywhere.

Keep a separate pronunciation map (display text → spoken spelling) used only
when calling the voice engine.

## Timeline from the read

`buildTimeline(lang, manifest)` is a pure function used by the composition,
the voice script and the music exporter, so they all agree on the cut:

- With a voice manifest, each scene lasts `voDelay + read + tail` (about
  0.55 s of air), at least `max(minSeconds, hold[lang])`.
- Without one, word timings are estimated (per-word + per-letter time, pauses
  after punctuation), so picture work starts before the narrator exists.
- **Stale-clip detection:** a clip counts only if its words, reduced to
  lowercase letters and digits, equal the script line's. Edit a line and the
  scene falls back to the estimate until it is re-voiced, instead of playing
  the old read.
- Expose word timings in scene frames and a helper like
  `wordFrame(scene, "tap", nth)` so animations land on the word that names
  them ("one tap" → the finger lands on "tap").

Export the timeline to JSON (`scripts/export-timeline.mjs`) for the Python
audio tools.

## Cuts on the beat

Pick a tempo with a whole number of frames per beat (120 BPM at 30 fps = 15
frames) and round every scene up to whole beats. The score is generated or
conformed to the same section lengths, so cuts, hits and taps fall on the
beat. Group scenes into music sections (`sections.json`: name, scene ids,
and the bar that can be repeated when a cut is longer).

## The real app on screen

Render the product's actual React components rather than redrawing them:

- **Webpack aliases.** Resolve the app's import alias (`@/…`) to the repo
  root, and swap the framework modules those components touch (router,
  `next/image`, data hooks, toasts, i18n providers, dialog portals) for small
  film shims that return fixed example data.
- **The app's stylesheet in a shadow root.** Compile the app's Tailwind CSS
  into a string at bundle time (a PostCSS loader rule for one CSS file) and
  attach it to a shadow root with `adoptedStyleSheets`, so its reset never
  touches the film's layout. Rewrite `:root` to `:host`. Chrome ignores
  `@property` inside shadow roots, so adopt those rules on the document once.
- **Force the mobile layout.** Override the breakpoints (`--breakpoint-*:
  999rem`) so responsive classes stay in their phone variant at any canvas
  size.
- **Deterministic CSS animations.** After each render, `pause()` every
  `root.getAnimations()` and set `currentTime` from the scene's frame;
  otherwise renders differ from frame to frame and between workers.
- **Fonts.** Load the app's font families in the film and hold the frame with
  `delayRender` until `document.fonts` is ready; set the CSS variables the
  app's font loader would have set.
- **Dialogs and sheets** render into a portal container inside the phone
  screen, not over the whole film.
- **Example data** lives in one module (profiles, channels, photos as data
  URLs if the image component only accepts https or data sources).

## Taps and measured boxes

Don't guess where a button is. After the app screen renders, measure the
target element (`getBoundingClientRect()` relative to the screen host, scaled
by the phone's transform) and store the box in state; the finger, the press
ripple and the "result grows out of the tapped element" animation all use it.
Find targets by visible text or a data attribute so layout changes in the app
don't break the film.

## Motion helpers

- **Spring and ease helpers** in one `lib/anim.ts`: `rise`, `fade`, `pop`,
  `growFrom(box → box)`, with consistent defaults so the film feels like one
  piece.
- **Word morphs (`MorphSlots`).** Model a phrase change as letter slots that
  stay, leave (float up, width shrinks to 0), arrive (width grows, drop in) or
  flip (rotateX through 90° at the midpoint). Measure each glyph's width in
  the real font (`@remotion/layout-utils` `measureText`) so gaps close exactly.
  Used for "network → net worth" and "logo → your link".
- **Logo morphs.** Draw added letters in the logo's own geometry (stroke
  width, x-height, spacing), animate the logo's own glyphs apart, scale the
  mark into the letter it replaces. Always morph back before a transition that
  needs the original mark.
- **3D networks without WebGL.** Place nodes on rings/spheres in 3D, rotate
  with yaw and pitch over time, project with a simple perspective divide, sort
  by depth, and use depth for fog (opacity, slight blur, smaller scale far
  away). Draw edges as SVG lines between projected points, with light pulses
  travelling along them. A collapse is all nodes easing to one projected
  point, which then becomes the logo.
- **Hand-offs between scenes** use coordinates from one shared layout module
  so the last frame of one scene equals the first of the next.

## Audio in the composition

- Narration: one `<Audio>` per scene at `scene.from + voFrom`.
- Score: one `<Audio>` for the conformed file of that language, with volume
  ducked under narration (e.g. −8 dB, ramped over ~0.25 s around each read).
- Effects: a cue list (frame, sound, gain) generated from the same timings as
  the picture (taps, pops, whooshes), so re-timing a scene moves its sounds.

## Stills, renders and the pipeline

- `scripts/stills.mjs <lang> <outDir> <frame…>` bundles once and renders PNG
  stills. Check the moments that matter (each tap, each morph's midpoint, every
  text-heavy frame) before rendering the whole film. Combine them into one
  contact sheet to review many at a glance.
- Render each language at 1080p (h264, CRF 18, yuv420p, AAC 320k), then master
  the loudness (`master_loudness.sh`), then make web copies (see
  `delivery.md`). Wire it as `render → master → web` scripts.
- Pull frames from the finished file (`ffmpeg -ss T -i film.mp4 -frames:v 1`)
  to confirm the encode matches the stills.
- Run the typecheck before every render; a broken import costs a whole render.
- Don't kill a render with `pkill -f "remotion render"` from a shell whose own
  command line contains that text; it kills the shell. Find the PIDs with
  `ps aux | grep "[r]emotion"`.
- Remotion's bundled ffmpeg is minimal (no `afade`, `alimiter`, `fps` filter).
  Do audio processing in Python (numpy/scipy/soundfile) or a system ffmpeg.
