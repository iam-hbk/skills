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

# One `skills add` per source with every skill from it, so each repo is cloned once
# instead of once per line; many lines share a repo.
grouped="$(awk '!/^#/ && NF >= 2 {
  if (!($1 in skills)) order[++n] = $1
  skills[$1] = skills[$1] " " $2
} END { for (i = 1; i <= n; i++) print order[i] skills[order[i]] }' "$manifest")"

while read -r source names; do
  [ -n "${source:-}" ] || continue
  args=()
  for name in $names; do args+=(--skill "$name"); done
  # </dev/null: otherwise npx reads the rest of the list from stdin and the loop stops early.
  npx -y skills add "$source" -g "${args[@]}" -y "$@" </dev/null
done <<< "$grouped"
