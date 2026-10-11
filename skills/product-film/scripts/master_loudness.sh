#!/usr/bin/env bash
# Delivery loudness for a finished film (or any audio file), two-pass:
#
#   master_loudness.sh IN OUT [TARGET_LUFS=-16] [TRUE_PEAK=-1.5]
#
# Pass 1 measures the file with ffmpeg's loudnorm; pass 2 applies one linear
# gain to hit the target (no compression, so the mix you approved keeps its
# dynamics). The video stream is copied untouched; audio is re-encoded as AAC
# 320k for .mp4/.mov/.m4a, otherwise by OUT's extension.
#
# If reaching the target would push true peaks over the ceiling, loudnorm
# switches to dynamic mode (a gentle compressor/limiter); the script says so.
# That's usually fine for a narrated film. If you want the approved mix's
# dynamics untouched, limit the peaks first (a look-ahead limiter in Python,
# ~1-2 dB of gain reduction) or accept a slightly lower target, then rerun.
#
# Uses $FFMPEG if set (e.g. FFMPEG="npx remotion ffmpeg"), else ffmpeg.
# Re-measure the result with audio_check.py; AAC can add a few tenths of peak.
set -euo pipefail
IN=${1:?usage: master_loudness.sh IN OUT [TARGET_LUFS] [TRUE_PEAK]}
OUT=${2:?usage: master_loudness.sh IN OUT [TARGET_LUFS] [TRUE_PEAK]}
I=${3:--16}
TP=${4:--1.5}
LRA=20
read -r -a FF <<< "${FFMPEG:-ffmpeg}"

measure=$("${FF[@]}" -hide_banner -nostats -i "$IN" -vn \
  -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
field() { printf '%s' "$measure" | sed -n "s/.*\"$1\" *: *\"\([^\"]*\)\".*/\1/p"; }
in_i=$(field input_i); in_tp=$(field input_tp); in_lra=$(field input_lra)
in_th=$(field input_thresh); offset=$(field target_offset)
[ -n "$in_i" ] || { echo "Couldn't measure $IN" >&2; exit 1; }

case "${OUT##*.}" in
  mp4|mov|m4v) codec=(-map 0:v? -map 0:a -c:v copy -c:a aac -b:a 320k -movflags +faststart) ;;
  m4a) codec=(-vn -c:a aac -b:a 320k -f mp4) ;;  # minimal ffmpeg builds lack the ipod muxer
  wav) codec=(-vn -c:a pcm_s24le) ;;
  *) codec=(-vn) ;;
esac

log=$("${FF[@]}" -hide_banner -nostats -y -i "$IN" \
  -af "loudnorm=I=$I:TP=$TP:LRA=$LRA:measured_I=$in_i:measured_TP=$in_tp:measured_LRA=$in_lra:measured_thresh=$in_th:offset=$offset:linear=true:print_format=json" \
  -ar 48000 "${codec[@]}" "$OUT" 2>&1) || { printf '%s\n' "$log" | tail -5 >&2; exit 1; }
measure=$(printf '%s' "$log" | sed -n '/^{/,/^}/p')
echo "$IN: $in_i LUFS, $in_tp dBTP → $(field output_i) LUFS, $(field output_tp) dBTP ($(field normalization_type))"
if [ "$(field normalization_type)" != "linear" ]; then
  echo "note: dynamic mode was needed to keep true peaks under $TP dBTP (see this script's header)" >&2
fi
