# Craft: story, claims, picture, pacing

## Contents
- Story and script
- Claims
- Picture
- Pacing and attention
- Transitions and morphs
- Using references
- Example content
- Direction doc template

## Story and script

- One narrated line per scene. The line names what the scene shows; the
  scene shows what the line names. If a line has no picture, cut it; if a
  scene has no line, it's probably a transition.
- A shape that worked for a ~80 s launch film (12 scenes): the everyday
  situation → the doubt → the reveal → the promise → proof (work,
  credentials, services) → the action (one tap, their way) → sharing →
  follow-up and measurement → languages → who it's for → the network idea →
  the logo and the tagline.
- Every idea pays off. A scene that introduces a concept the film never
  returns to feels unfinished to clients ("ideas that are not really
  complete"). Prefer scenes built from the film's own cast and objects: the
  network scene grew out of the six example profiles the previous scene had
  just shown, and collapsed into the logo that carries the tagline.
- End on the brand line, and give the logo a moment: let it land, fire, take
  its place; a static lockup undersells it.

## Claims

- Only shipped capabilities, at the plan level the product actually enforces.
  Read the product's capability docs or code before writing a line.
- No sweeping or comparative claims ("X doesn't work, we do"). Say what the
  scene shows: "Many of your best clients start with a simple introduction."
- Show breadth honestly. If the product supports email, website, socials,
  booking links, a link in bio, don't tell a WhatsApp-only story: many
  professionals don't want to lead with a personal number.
- Universal over local: named cities or one market shrink a product that
  works anywhere.
- Invented people and businesses are labelled as examples; contact details use
  reserved domains (`.example`, `example.com`) and fictional number ranges.
  Never invent testimonials, customer counts or metrics; label illustrative
  numbers as illustrative.

## Picture

- The product on screen is the real app (see `remotion-architecture.md`).
- Example content looks real: openly licensed photos (CC0) for covers and
  galleries, credited in a file next to them; friendly, varied illustrations
  where no photo fits; cards on a grid with equal heights. Smooth shapes; any
  stray corner or misalignment gets noticed.
- Device mockups: one phone, big enough to read; its text must be legible at
  1080p when it matters (zoom in rather than shrink).
- Depth with restraint: 3D rotation, perspective, near-bright/far-dim fog and
  slight blur on far objects make networks and carousels feel alive.

## Pacing and attention

- One thing moves at a time. The viewer's eye goes to the newest motion; if a
  card animates beside the phone while the phone is tapped, the tap is missed.
  Sequence: the finger lands and presses → a beat (6–10 frames) → the result
  grows out of the pressed element → only then does nearby text change.
- Dim the room around the device during taps (a radial vignette) to point the
  eye.
- Product moments that carry the message (a language switch, a status change)
  need a push-in so the changed text is readable, a hold before, a visible
  agent of change (a wipe running down the screen), the changed words
  outlined, and a hold after. Text that names the change waits until it has
  happened on screen.
- Lists of options ("WhatsApp, email, your website, your socials") work when
  each item gets its own tap as it's named and its own result card, settling
  into a grid that ends the scene as an overview.

## Transitions and morphs

- One scene's last frame is the next one's first: a carousel ring of phones
  tips back into a 3D network of their owners; the network collapses into a
  white-hot point that the logo flashes out of. Hand-offs need matching
  positions: share the coordinates in one layout module.
- Word morphs: letter slots that leave (float up, gap closes), arrive (gap
  opens, drop in) or flip (rotateX through 90°). "network → net worth" and
  "logo → your link" both used this. Measure glyph widths in the real font so
  gaps close exactly.
- Logo morphs: draw added letters in the logo's own geometry (x-height,
  stroke width, spacing), slide the logo's own letters apart, shrink the mark
  into the letter it stands for, and morph back before any transition that
  needs the logo (e.g. flying through its ring).

## Using references

When the client shares a reference video, extract frames around the moment
they point to and name what makes it work (depth, a morph into the next frame,
a camera move). Rebuild that effect from the film's own story and cast. Do
not copy its counters, labels, push-ins or layout: the client said "I like the
effect, not a copy pasta."

## Example content

Personas: each example profile offers the channels its owner realistically
would (a booking link and LinkedIn for an accountant, Instagram and TikTok for
a bridal artist, WhatsApp for a builder), and some have no phone. The variety
on screen tells the story without narration.

## Direction doc template

Keep one per brand (e.g. `docs/ux/video-direction.md`) and update it whenever
the client approves or rejects something:

```markdown
# <Brand> Video Direction
## The brand, spoken and shown   (name pronunciation, tagline, adaptations, logo moment)
## Story and claims              (what may be said, what was rejected)
## Narration                     (voices per language, why, kept takes)
## Picture                       (real UI, example content, pacing rules)
## Music and sound               (brief, master take, key, loudness)
## Working together              (what to send for picks, how to deliver)
## Decisions log                 | Asked for | Rejected | Chosen |
```

Add a project skill that points to it so future sessions load it
automatically.
