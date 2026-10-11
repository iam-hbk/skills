# Voice: narration, auditions, pronunciation, languages

## Engine and keys

ElevenLabs worked well (`eleven_v4` for English, `eleven_v3` for African
French). Keep the API key in the environment (`ELEVENLABS_API_KEY`); never
print, log or commit it, and never ask for it in chat. Check access first
(list models, plan, credits).

## Auditions

- Search the voice library for the brief's accent and language; rank by
  quality category, intended use (narration, conversational) and usage, but
  don't pretend to judge by ear: you can't hear the samples.
- Read the same real passage with every candidate: two or three actual lines
  including the brand name and the tagline. One line isn't enough to judge
  warmth or pacing.
- Send every sample as a file with name, accent and library description; wait
  for the pick. Offer an engine A/B on the chosen voice (a newer model often
  sounds more natural).
- Expect "compelling", "real", "not too serious, expressive but not
  exaggerated" as the target. Polished-but-flat voices get rejected.

## Pronunciation

- Fix it in the text sent to the engine, never on screen: keep a map of
  display text → spoken spelling per language (e.g. `urlinq` → `yourlink`,
  `urlinq.com` → `yourlink dot com` / `yourlink point com`). Apply it only
  when building the request.
- Verify with speech-to-text (`scripts/stt_check.mjs`, transcribed as
  English): the brand should come back spelled the way it's meant to sound.
  A French engine read "urlink" as "hurlinc"; "yourlink" fixed it everywhere.
  Check every line containing the name, not just the first.
- When a language's speakers use the brand's original pronunciation, say so in
  the brief and spell for it in that language too.

## Timing from the read

Generate one clip per scene with the neighbouring lines as context
(`previous_text` / `next_text`) so the delivery flows. Keep the character
alignment and turn it into word timings mapped back to the on-screen words;
scenes cut to the real read (see `remotion-architecture.md`). Store a
manifest per language: file, duration, words with start/end.

## Keep what works

- If the client loves a particular take (a chuckle on the punchline), splice
  that exact take into the film: find its span with forced alignment, cut it
  on silence (stream copy is fine), write its word timings into the manifest
  with a note of its source. Regeneration won't reproduce it.
- Re-voice only lines that changed (`--only scene,scene`), so approved takes
  survive.
- Let the timeline detect stale clips: if a clip's words no longer match the
  script line (letters and digits only), estimate the read until it's
  re-voiced.

## Language versions

- Localise the story, not just the words: a local hero, local names, local
  phone formats and currency.
- Taglines are adapted, not translated: catchy and familiar to that audience
  ("Your network is your net worth" → "Votre réseau vaut de l'or"). If the
  brand line is part of the identity, keep it on screen in the original with
  the local line under it, and narrate the local line.
- A pun that only works in one language can still be shown in that language
  (the logo spelling "your link") with a spoken bridge in the other
  ("Votre lien… your link").
