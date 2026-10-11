# Music and sound

## Brief and samples

- Write the brief as global styles + sections mapped to groups of scenes
  (cold open, reveal hit, product groove, breakdown, peak, finale), with
  section lengths taken from the cut. A steady tempo (120 BPM = 2 s bars,
  0.5 s beats) lets you cut scenes on beats.
- Send two or three 30-second directions first and let the client pick by
  ear. In one project an Afro-house take was "a bit too afrobeat"; nu-disco /
  French touch (funky bass, filtered piano, disco strings, four-on-the-floor)
  won over indie-pop and electro-pop.
- Ask the generator for no vocals, and say it must sit under a voice-over.

## One master take for every cut

Each generation is a different piece, and quality varies: one French take
had a loose, drifting opening the client heard as "off beat" next to the
approved English take. So:

1. Generate one master for one cut; record its section lengths next to it.
2. Make every other cut's music sections equal to the master's plus whole
   bars (pad scenes with a per-language minimum length if needed).
3. Run `scripts/conform_bars.py`, which repeats a chosen bar inside each longer
   section. Choose a bar with no hit, fill or riser (not the section's first
   bar when it starts with an impact, not the last when it ends on a riser).

Verify with `scripts/audio_check.py`: the tempo must stay steady (e.g. 120.0
BPM across windows) and the beat grid should sit on the cut's grid. Judge
tempo on the score file itself: in the finished mix, sparse sections under
narration read as weak or wandering windows even when the score is steady.

## Sound effects in the score's key

Pitched effects (chimes, success arpeggios, blips, shimmers, NFC beeps,
scrambles, swells) must use notes from the score's key, or they clash ("a
sound off key"). Estimate the score's key with `audio_check.py`, then
transpose the effects (one semitone moved an A-major set into A-flat for a
C-minor / A-flat-major score) and re-check their pitch classes.

## Loudness

- Generated music arrives mastered loud (around −11 LUFS); bring it to about
  −16 LUFS before mixing so voice ducking keeps the narrator on top.
- Duck the score under narration (around −8 dB), then master the final mix to
  −16 LUFS integrated with true peaks under −1 dBTP
  (`scripts/master_loudness.sh`). Re-measure after encoding (AAC can add
  a little peak).
- Report the numbers when you send a film; you can't listen, so measurements
  are your evidence.
