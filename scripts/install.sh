#!/usr/bin/env bash
# Installs this repo's skills plus every third-party skill in third-party.txt,
# for the current user. Extra arguments go to `npx skills add` (e.g. -a claude-code -a codex).
# Usage, from a checkout of this repo:  scripts/install.sh [-a <agent> ...]
set -euo pipefail

self="${SKILLS_REPO:-iam-hbk/skills}"
manifest="$(cd "$(dirname "$0")/.." && pwd)/third-party.txt"

# Skip the self-install while skills/ is empty: `skills add` exits non-zero on a repo with no skills.
if ls "$(dirname "$0")/../skills"/*/SKILL.md >/dev/null 2>&1; then
  npx -y skills add "$self" -g --skill '*' -y "$@"
fi

[ -f "$manifest" ] || exit 0
while read -r source name; do
  [ -z "${source:-}" ] || [ "${source:0:1}" = "#" ] && continue
  # </dev/null: otherwise npx reads the rest of the manifest from stdin and the loop stops after one line.
  npx -y skills add "$source" -g --skill "$name" -y "$@" </dev/null
done < "$manifest"
