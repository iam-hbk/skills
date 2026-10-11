---
name: product-film
description: Make a product launch film, explainer, promo or app demo video in code (Remotion/React), with AI voice-over, music, sound design and several language versions, reviewed with the client until it lands. Use this whenever someone wants a video for their product, app, startup or brand ("make a launch video", "explainer for our app", "promo with voice-over", "animate our UI", "a French version of the film", "add music to the video", "the voice sounds robotic", "the music is off-beat"), even if they don't say Remotion, and also when revising an existing code-made video's script, voice, music, pacing or delivery.
---

# Product film

A process and a set of hard-won defaults for making product films in code:
the product's real UI on screen, a narrated script that drives the cut, a
licensed or generated score, and versions per language, iterated with the
client by ear and by eye. It comes from a launch film made over many review
rounds; the defaults below are what the client kept, and each says why.

Read the reference that matches the step you're on:

- `references/craft.md`: story, claims, picture, pacing, transitions (read before writing a script or a scene)
- `references/voice.md`: narration, auditions, pronunciation, language versions
- `references/music-and-sound.md`: score briefs, one master for every cut, effects in key, loudness
- `references/remotion-architecture.md`: the code patterns (timeline from the read, real app UI, measuring the DOM, morphs, 3D)
- `references/delivery.md`: renders, encodes, review pages, storage, what doesn't work

Bundled scripts (Python 3 + numpy/scipy/soundfile; ffmpeg; Node 18+). They
find ffmpeg through `$FFMPEG` (e.g. `FFMPEG="npx remotion ffmpeg"` when only
Remotion's copy is installed):

- `scripts/audio_check.py FILE…`: loudness (LUFS), true peak, tempo per window, musical key. Use on every score, effect set and finished film; it's how you "listen".
- `scripts/conform_bars.py PLAN.json OUT`: fit one approved music take to a cut with longer sections by repeating whole bars (plan format in its header).
- `scripts/master_loudness.sh IN OUT [LUFS] [TP]`: two-pass loudness normalisation (−16 LUFS, −1.5 dBTP by default), video stream copied.
- `scripts/stt_check.mjs [--lang eng] [--expect word] FILE…`: speech-to-text on voice clips (ElevenLabs Scribe) to verify how names were actually said.

## The workflow

Each phase ends with something the client can see or hear. Taste decides
voices, music and taglines, so those go to the client as samples; everything
else, decide, do, and say what you decided.

1. **Brief and ground truth.** Find what the product really does (code,
   product docs, a capability contract) and what's only planned. Find the
   brand: name, how it's said, tagline, colours, type, logo files, any design
   system. Find the owner's existing direction doc if there is one (a
   `video-direction.md` or similar) and follow it.
2. **Script.** One line of narration per scene; every claim maps to a shipped
   capability and to what the scene shows. Keep it plain and specific: no
   superlatives, no swipes at alternatives.
3. **Voice audition.** Several candidate voices reading the same real passage,
   including the brand name, sent as files. Wait for the pick. Fix
   pronunciation by spelling, then verify with `stt_check.mjs`.
4. **Picture, stills first.** Build scenes on the timeline driven by the read.
   Render stills of the moments that matter and look at them before any full
   render. Iterate on stills; they cost seconds, renders cost minutes.
5. **Music.** Two or three 30-second directions as samples; wait for the pick.
   Generate one master take, then conform it to every cut by whole bars.
   Check tempo and key with `audio_check.py`; tune pitched effects to the key.
6. **Render, master, check.** Full renders, loudness mastering (−16 LUFS, true
   peak under −1 dBTP), frames pulled from the finished file, speech-to-text
   on new narration. Then send.
7. **Deliver and keep it watchable.** Web-size files in the chat, a
   phone-friendly page with every language version, full-quality masters where
   the client can download them. Commit the sources (script, voice clips,
   manifests, score master) so the film can be rebuilt.
8. **Write down the taste.** When the client approves or rejects something,
   record the rule and the reason in the project's direction doc (see the
   template at the end of `references/craft.md`). The next film starts there.

## Defaults that came from client feedback

These are starting points, not laws: a brief or a direction doc overrides
them. Each one exists because the opposite was tried and rejected.

- **Show the real product.** Render the app's actual components in the film
  (`references/remotion-architecture.md`) instead of redrawn mockups. Clients
  spot fake UI immediately, and the real thing stays true when the app changes.
- **One thing at a time; the device is the star.** A tap lands and is seen
  before its result appears, and the result grows out of what was tapped.
  Nothing beside the phone moves while the phone is doing something important.
  Key product moments (a language switch, a state change) must be large and
  slow enough that a first-time viewer can't miss them.
- **Honest claims, said plainly.** "Many of your best clients start with an
  introduction", not "the best clients don't come from ads". Show the range of
  what the product supports, not the one channel that's easiest to animate.
- **Universal over specific.** Named places and single personas narrow a
  product that works anywhere; prefer the idea ("wherever your name travels")
  to geography.
- **Natural narration.** Warm, expressive, a little playful; never robotic,
  never theatrical. Pick by ear; keep the take the client loved instead of
  hoping a regeneration reproduces it.
- **Brand names are said the owner's way in every language**, enforced by
  spelling in the text sent to the voice engine and verified by STT.
- **Adapt taglines, don't translate them**: catchy and idiomatic for the
  audience, with the original kept on screen if it's part of the brand.
- **Puns are intended, not explained.** Show the wordplay once (a morph, a
  beat) and trust the audience.
- **Scenes flow into each other.** One scene's last frame becomes the next
  scene's first; words morph into words; a network collapses into the logo.
- **References give the effect, not the scene.** Rebuild a borrowed effect
  from your own story and cast; copied counters, layouts and push-ins read
  as copies.
- **Upbeat but specific music, one take for all cuts, effects in key.**
  Separate generations per language differ (one drifted off-beat). Pitched
  effects in another key read as "a sound off key".
- **Every review round is something the client can open on a phone.**

## Working with the client

- Send samples (voices, music) and stills before committing to full renders;
  wait for a pick where it's a matter of taste.
- Report what you checked and what you couldn't (you can't hear: say so, and
  say which objective checks you ran instead: STT, tempo, key, loudness).
- When feedback arrives, fix the cause and write the rule down, so the next
  scene or film doesn't repeat the mistake.
