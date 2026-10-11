# Delivery

Every review round should reach the client in a form they can open on a
phone, away from their desk.

## Files in the chat

- Send web copies, not masters. Chat file transfers have size limits (about
  30 MiB worked); a 1080p, 80-second film fits at H.264 CRF 20 with
  `-maxrate 2600k -bufsize 5200k`, AAC 192k, `-movflags +faststart`. If it
  doesn't fit, lower `maxrate` rather than the resolution.
- Re-measure loudness and true peak on the encode you actually send.
- Caption each file with what changed in this round and the numbers you
  checked (length, LUFS, true peak, which lines were re-voiced).
- Samples for a decision (voices, music directions, stills) go as separate,
  clearly named files: `voice-2-ava.mp3`, `music-b-nudisco.mp3`.

## A watch page

A small, private web page with every language version side by side (a 720p
copy of each, poster frames, the date and what changed) is easier on a phone
than files. Update the same page each round so its link stays stable; keep
the files it references small enough to stream on mobile data.

## Where the masters live

- Large files don't go through chat or document connectors well (a Drive
  connector that creates files from text can't take a 200 MB video).
- If the project has object storage (R2, S3, GCS), a small staff-only media
  page works well: the backend hands out a presigned PUT URL for a key it
  chooses, the upload script streams the file straight to storage, then calls
  a token-protected "register" endpoint that checks the object exists and
  records title, group, size and type. The page lists files by group with
  play (short-lived signed URL) and download (signed URL with
  `Content-Disposition: attachment`).
- The upload token lives in the environment of both sides; compare it in
  constant time; never print it or ask for it in chat.
- Give the client the page's URL and say which files are there (e.g. "EN and
  FR 1080p masters, EN and FR web").

## Keep it rebuildable

Commit the sources: the script, copy, the voice clips and manifests (they
cost credits and the client approved specific takes), the score master and
its section lengths, effect generators, and the scripts. Don't commit the
renders or caches (`out/`, `__pycache__/`). Note in the film's README how to
rebuild: install, voice, music, render, master, web, publish.

## Hand-off notes

At the end of a round, write down what's approved, what's pending, which
takes are locked, and anything a future session must not change (a kept
take, a key, a tagline). Put lasting taste rules in the direction doc.
