#!/usr/bin/env python3
"""Fit one approved music take to a cut whose sections run longer, by
repeating whole bars, so every language version shares the same performance.

    python3 conform_bars.py PLAN.json OUT.wav

PLAN.json:

    {
      "source": "music-master.mp3",      // relative to the plan file
      "bpm": 120, "beatsPerBar": 4,       // bar = 2.0 s here
      "total": 87.0,                      // optional: trim the result to the cut's length
      "sections": [                       // in order, covering the master from 0 s
        {"name": "Cold open", "source": 14.0, "target": 16.0, "repeatBar": 2},
        {"name": "Reveal",    "source": 5.5,  "target": 5.5}
      ]
    }

- `source` is the section's length in the master; `target` its length in this
  cut. target - source must be zero or a whole number of bars: make the cut
  fit (round scenes to beats, add per-language minimum lengths) rather than
  stretching audio.
- `repeatBar` is the 0-based bar, counted from the section's start, that is
  repeated (back to back) as many times as needed. Pick a bar with no hit,
  fill or riser: usually not bar 0 when the section opens on an impact, and
  not the last bar when it ends on a riser. Listen-free check: it should be a
  bar where the section's phrase simply continues.
- Splices crossfade for 12 ms (equal power), centred on the bar line.

The master must be steady (check with audio_check.py) and start on a
downbeat at 0 s, so bar lines fall at multiples of the bar length.

Output: .wav/.flac written directly (24-bit); any other extension is encoded
with ffmpeg (FFMPEG env var, default "ffmpeg").
Requires Python 3 with numpy, scipy and soundfile.
"""

import json
import os
import shlex
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

FADE = 0.012  # seconds


def ffmpeg(*args):
    cmd = shlex.split(os.environ.get("FFMPEG", "ffmpeg"))
    subprocess.run([*cmd, "-hide_banner", "-loglevel", "error", "-y", *args], check=True, stdout=subprocess.DEVNULL)


def load(path):
    try:
        return sf.read(path, always_2d=True)
    except Exception:
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "src.wav")
            ffmpeg("-i", os.path.abspath(path), "-vn", "-ar", "48000", "-c:a", "pcm_s24le", wav)
            return sf.read(wav, always_2d=True)


def stitch(x, ranges, h):
    """Concatenate sample ranges of x with a 2h-sample equal-power crossfade
    centred on every join."""
    t = np.linspace(0, np.pi / 2, 2 * h)[:, None]
    pad = np.zeros((h, x.shape[1]))
    xp = np.concatenate([pad, x, pad])  # so ranges at the very start/end can borrow h samples
    s0, e0 = ranges[0]
    out = xp[s0 + h:e0 + 2 * h].copy()
    for s, e in ranges[1:]:
        head = xp[s:e + 2 * h]  # = x[s-h : e+h]
        out[-2 * h:] = out[-2 * h:] * np.cos(t) + head[:2 * h] * np.sin(t)
        out = np.concatenate([out, head[2 * h:]])
    return out[:-h]


def plan_ranges(plan, sr):
    bar_s = 60.0 / plan["bpm"] * plan.get("beatsPerBar", 4)
    bar = int(round(bar_s * sr))
    ranges, start, problems, notes = [], 0.0, [], []
    for sec in plan["sections"]:
        a, b = float(sec["source"]), float(sec["target"])
        extra = (b - a) / bar_s
        if b < a - 1e-6 or abs(extra - round(extra)) > 1e-6:
            problems.append(f"{sec['name']}: master {a:.3f}s, target {b:.3f}s "
                            f"(target must be the master's length plus whole bars of {bar_s:g}s)")
            start += a
            continue
        extra = int(round(extra))
        s0, s1 = int(round(start * sr)), int(round((start + a) * sr))
        if extra:
            rb = sec.get("repeatBar")
            if rb is None:
                problems.append(f"{sec['name']}: needs {extra} extra bar(s) but has no repeatBar")
            else:
                at = s0 + bar * (rb + 1)
                if at > s1:
                    problems.append(f"{sec['name']}: repeatBar {rb} is past the section's end")
                else:
                    ranges += [(s0, at)] + [(at - bar, at)] * extra + [(at, s1)]
                    notes.append(f"{sec['name']}: +{extra} bar(s), repeating {at / sr - bar_s:.2f}-{at / sr:.2f}s of the master")
        else:
            ranges.append((s0, s1))
        start += a
    merged = [ranges[0]] if ranges else []
    for s, e in ranges[1:]:
        if s == merged[-1][1]:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return merged, problems, notes, start


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    plan_path, out_path = sys.argv[1:]
    with open(plan_path) as f:
        plan = json.load(f)
    src = os.path.join(os.path.dirname(os.path.abspath(plan_path)), plan["source"])
    x, sr = load(src)
    ranges, problems, notes, used = plan_ranges(plan, sr)
    if used > len(x) / sr + 0.05:  # decoders can trim a few ms
        problems.append(f"sections add up to {used:.2f}s but the master is {len(x) / sr:.2f}s")
    if problems:
        sys.exit("Can't conform:\n  " + "\n  ".join(problems))
    y = stitch(x, ranges, int(round(FADE * sr / 2)))
    if "total" in plan:
        y = y[:int(round(plan["total"] * sr))]
    for n in notes:
        print("  " + n)
    ext = os.path.splitext(out_path)[1].lower()
    if ext in (".wav", ".flac"):
        sf.write(out_path, y, sr, subtype="PCM_24")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "out.wav")
            sf.write(wav, y, sr, subtype="PCM_24")
            ffmpeg("-i", wav, os.path.abspath(out_path))
    print(f"→ {out_path} ({len(y) / sr:.2f}s)")


if __name__ == "__main__":
    main()
