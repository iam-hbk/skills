#!/usr/bin/env python3
"""Objective checks for a film's audio: you can't listen, so measure.

    python3 audio_check.py FILE [FILE…] [--sections 0,14,50] [--json]

For each file (wav/flac/mp3 via soundfile; anything else, e.g. an .mp4, is
decoded with ffmpeg; set FFMPEG="npx remotion ffmpeg" if only Remotion's
copy is installed) it reports:

  loudness   integrated LUFS (ITU-R BS.1770 K-weighting, gated) and true peak
             (4x oversampled dBTP). Delivery target: about -16 LUFS, < -1 dBTP.
  tempo      BPM in 6 s windows every 3 s, with the median and the spread.
             A steady score reads the same BPM in every window (e.g. 120.0);
             a drifting one, or one whose strength collapses, sounds "off beat".
  key        best and runner-up major/minor key from a chroma profile, plus
             the strongest pitch classes. Pitched effects should use notes
             from the score's key. Short clips (< 1 s) are reported by
             pitch classes only.

--sections splits the key estimate at the given times in seconds, useful
when a score modulates. --json prints machine-readable results.

Requires Python 3 with numpy, scipy and soundfile.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48_000
EPS = 1e-12
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# Krumhansl-Kessler key profiles.
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
# BS.1770 K-weighting at 48 kHz: high shelf, then high pass.
K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def load(path):
    """Audio as float (n, channels) at 48 kHz."""
    try:
        x, sr = sf.read(path, always_2d=True)
    except Exception:
        ffmpeg = shlex.split(os.environ.get("FFMPEG", "ffmpeg"))
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "a.wav")
            subprocess.run([*ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", os.path.abspath(path),
                            "-vn", "-ar", str(SR), "-c:a", "pcm_s24le", wav],
                           check=True, stdout=subprocess.DEVNULL)
            x, sr = sf.read(wav, always_2d=True)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = signal.resample_poly(x, SR // g, sr // g, axis=0)
    return x


def block_power(x, window=0.4, hop=0.1):
    y = signal.lfilter(*K1, x, axis=0)
    y = signal.lfilter(*K2, y, axis=0)
    p = (y ** 2).sum(axis=1)  # L/R weights are 1; surround channels are not handled
    n, h = int(window * SR), int(hop * SR)
    if len(p) < n:
        return np.array([p.mean()]) if len(p) else np.array([0.0])
    c = np.concatenate([[0.0], np.cumsum(p)])
    starts = np.arange(0, len(p) - n + 1, h)
    return (c[starts + n] - c[starts]) / n


def lufs(x):
    z = block_power(x)
    z = z[-0.691 + 10 * np.log10(z + EPS) > -70.0]
    if not len(z):
        return float("-inf")
    rel = -0.691 + 10 * np.log10(z.mean()) - 10.0
    z = z[-0.691 + 10 * np.log10(z + EPS) > rel]
    return float(-0.691 + 10 * np.log10(z.mean()))


def true_peak_db(x):
    peak = max(np.abs(signal.resample_poly(x[:, c], 4, 1)).max() for c in range(x.shape[1]))
    return float(20 * np.log10(peak + EPS))


def tempo(x, hop=512, window=6.0, step=3.0, lo=80, hi=180):
    m = x.mean(axis=1)
    _, _, Z = signal.stft(m, SR, nperseg=2048, noverlap=2048 - hop)
    mag = np.log1p(np.abs(Z) * 100)
    flux = np.maximum(0, np.diff(mag, axis=1)).sum(axis=0)
    env = flux - signal.medfilt(flux, 31)
    fps = SR / hop
    win = int(window * fps)
    out = []
    for s in range(0, max(len(env) - win, 0), int(step * fps)):
        e = env[s:s + win] - env[s:s + win].mean()
        ac = np.correlate(e, e, "full")[win - 1:]
        lags = np.arange(len(ac)) / fps
        sel = (lags > 60 / hi) & (lags < 60 / lo)
        i = np.flatnonzero(sel)[np.argmax(ac[sel])]
        # Parabolic interpolation: the lag grid is ~10 ms, which alone would read 120 as 119.7.
        a, b, c = ac[i - 1], ac[i], ac[i + 1]
        lag = (i + 0.5 * (a - c) / (a - 2 * b + c + EPS)) / fps
        out.append({"at": round(s / fps, 1), "bpm": round(60 / lag, 1),
                    "strength": round(float(ac[sel].max() / (ac[0] + EPS)), 2)})
    return out


def chroma(x):
    m = x.mean(axis=1)
    n = 8192 if len(m) >= 8192 else max(256, 2 ** int(np.log2(max(len(m), 256))))
    f, _, Z = signal.stft(m, SR, nperseg=n, noverlap=n * 3 // 4)
    P = np.abs(Z) ** 2
    sel = (f > 60) & (f < 2000)
    pc = np.round(12 * np.log2(f[sel] / 261.63)) % 12
    c = np.array([P[sel][pc == k].sum() for k in range(12)])
    return c / (c.sum() + EPS)


def key_of(c):
    scores = []
    for tonic in range(12):
        for prof, mode in ((MAJ, "major"), (MIN, "minor")):
            scores.append((float(np.corrcoef(np.roll(prof, tonic), c)[0, 1]), f"{NAMES[tonic]} {mode}"))
    scores.sort(reverse=True)
    return scores[:2]


def check(path, cuts):
    x = load(path)
    dur = len(x) / SR
    res = {"file": path, "seconds": round(dur, 2), "lufs": round(lufs(x), 1), "true_peak_dbtp": round(true_peak_db(x), 1)}
    if dur >= 8:
        windows = tempo(x)
        bpms = np.array([w["bpm"] for w in windows])
        res["tempo"] = {"median": float(np.median(bpms)), "min": float(bpms.min()), "max": float(bpms.max()),
                        "windows": windows}
    bounds = [0.0] + [t for t in cuts if 0 < t < dur] + [dur]
    res["key"] = []
    for a, b in zip(bounds, bounds[1:]):
        c = chroma(x[int(a * SR):int(b * SR)])
        top = [f"{NAMES[i]} {c[i]:.2f}" for i in np.argsort(c)[::-1][:4]]
        entry = {"from": round(a, 1), "to": round(b, 1), "top_pitch_classes": top}
        if b - a >= 1.0:
            (s1, k1), (s2, k2) = key_of(c)
            entry.update(best=k1, score=round(s1, 2), runner_up=k2)
        res["key"].append(entry)
    return res


def report(r):
    print(f"{r['file']}  ({r['seconds']:.2f} s)")
    print(f"  loudness  {r['lufs']:.1f} LUFS integrated, true peak {r['true_peak_dbtp']:.1f} dBTP")
    if "tempo" in r:
        t = r["tempo"]
        weak = sum(w["strength"] < 0.2 for w in t["windows"])
        print(f"  tempo     median {t['median']:.1f} BPM, range {t['min']:.1f}-{t['max']:.1f}"
              f" over {len(t['windows'])} windows" + (f", {weak} weak (strength < 0.2)" if weak else ""))
        print("            " + " | ".join(f"{w['at']:.0f}s {w['bpm']:.1f}" for w in t["windows"]))
    for k in r["key"]:
        span = f"{k['from']:.0f}-{k['to']:.0f}s"
        if "best" in k:
            print(f"  key {span:9s} {k['best']} ({k['score']:.2f}), else {k['runner_up']};  "
                  f"top {', '.join(k['top_pitch_classes'])}")
        else:
            print(f"  pitch {span:7s} top {', '.join(k['top_pitch_classes'])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--sections", default="", help="comma-separated split times (s) for the key estimate")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    cuts = [float(t) for t in a.sections.split(",") if t.strip()]
    results = [check(f, cuts) for f in a.files]
    if a.json:
        json.dump(results, sys.stdout, indent=2)
        print()
    else:
        for r in results:
            report(r)


if __name__ == "__main__":
    main()
