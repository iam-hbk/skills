#!/usr/bin/env node
// Hear what the narrator actually said: transcribe voice clips with
// ElevenLabs Scribe and flag brand names that came back wrong.
//
//   node stt_check.mjs [--lang eng] [--expect yourlink] FILE…
//
// --lang     ISO 639-3 code to transcribe as (default eng). Transcribing a
//            French clip as English is deliberate when checking an English
//            brand name inside it: the brand should come back spelled the
//            way it's meant to sound ("yourlink", not "hurlinc").
// --expect   a word that must appear (letters/digits only, case-insensitive;
//            repeatable). Clips missing it are marked ✗ and the exit code is 1.
//
// Needs Node 18+ and ELEVENLABS_API_KEY in the environment. The key is read,
// never printed; set it in the environment's settings, not in the chat.
import { readFileSync } from "node:fs";
import { basename } from "node:path";

const args = process.argv.slice(2);
let lang = "eng";
const expect = [];
const files = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--lang") lang = args[++i];
  else if (args[i] === "--expect") expect.push(args[++i]);
  else files.push(args[i]);
}
if (!files.length) {
  console.error("usage: node stt_check.mjs [--lang eng] [--expect word] FILE…");
  process.exit(2);
}
const key = process.env.ELEVENLABS_API_KEY?.trim();
if (!key) {
  console.error("ELEVENLABS_API_KEY is not set. Add it to the environment's settings (never paste it in chat).");
  process.exit(2);
}

const bare = (s) => s.toLowerCase().replace(/[^\p{L}\p{N}]/gu, "");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function transcribe(file) {
  for (let attempt = 0; ; attempt++) {
    const form = new FormData();
    form.set("model_id", "scribe_v1");
    form.set("language_code", lang);
    form.set("tag_audio_events", "false");
    form.set("file", new Blob([readFileSync(file)]), basename(file));
    const res = await fetch("https://api.elevenlabs.io/v1/speech-to-text", {
      method: "POST",
      headers: { "xi-api-key": key },
      body: form,
    }).catch((err) => ({ ok: false, status: 0, text: async () => String(err) }));
    if (res.ok) return (await res.json()).text?.trim() ?? "";
    if (attempt < 4 && (res.status === 0 || res.status === 429 || res.status >= 500)) {
      await sleep(2000 * 2 ** attempt);
      continue;
    }
    throw new Error(`speech-to-text ${res.status} for ${file}: ${(await res.text()).slice(0, 300)}`);
  }
}

let failed = false;
for (const file of files) {
  const text = await transcribe(file);
  const words = new Set(text.split(/\s+/).map(bare));
  const joined = bare(text);
  const missing = expect.filter((w) => !words.has(bare(w)) && !joined.includes(bare(w)));
  if (missing.length) failed = true;
  const mark = expect.length ? (missing.length ? `✗ missing ${missing.join(", ")}` : "✓") : "";
  console.log(`${file}  ${mark}\n  ${text}`);
}
process.exit(failed ? 1 : 0);
