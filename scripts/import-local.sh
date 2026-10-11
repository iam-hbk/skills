#!/usr/bin/env bash
# Imports skills from a local agent folder into this repo.
# Usage, from the repo root:  scripts/import-local.sh [source-dir] [--force]
# source-dir defaults to ~/.claude/skills. Existing skills are skipped unless --force.
#
# Skills the `skills` CLI installed from someone else's repo (recorded in
# ~/.agents/.skill-lock.json) are not copied. They are listed in third-party.txt
# so scripts/install.sh installs them from upstream and they keep getting updates.
# Nothing is committed; review `git status` and commit yourself.
set -euo pipefail

src="${HOME}/.claude/skills"
force=0
for arg in "$@"; do
  case "$arg" in
    --force) force=1 ;;
    *) src="$arg" ;;
  esac
done

repo="$(cd "$(dirname "$0")/.." && pwd)"
dest="$repo/skills"
manifest="$repo/third-party.txt"
lock="${SKILLS_LOCK:-$HOME/.agents/.skill-lock.json}"
[ -d "$src" ] || { echo "no skills folder at $src" >&2; exit 1; }
mkdir -p "$dest"
touch "$manifest"

# "<name> <source>" for every lock entry installed from a remote repo other than this one.
third_party="$(node -e '
  const fs = require("fs");
  const [lock, self] = process.argv.slice(1);
  if (!fs.existsSync(lock)) process.exit(0);
  const { skills = {} } = JSON.parse(fs.readFileSync(lock, "utf8"));
  for (const [name, s] of Object.entries(skills)) {
    if (s.sourceType === "local" || !s.source || s.source === self) continue;
    // A pinned install keeps its pin: <sourceUrl>#<ref>, the form `npx skills add` accepts.
    console.log(name + " " + (s.ref && s.sourceUrl ? s.sourceUrl + "#" + s.ref : s.source));
  }' "$lock" "iam-hbk/skills")"

copied=0 skipped=0 linked=0
for dir in "$src"/*/; do
  name="$(basename "$dir")"
  # Only real skills: a folder with SKILL.md at its top level (skips synced/ and plugin caches).
  [ -f "$dir/SKILL.md" ] || { echo "skip   $name (no SKILL.md)"; continue; }

  source="$(printf '%s\n' "$third_party" | awk -v n="$name" '$1 == n { print $2 }')"
  if [ -n "$source" ]; then
    grep -qxF "$source $name" "$manifest" || echo "$source $name" >> "$manifest"
    echo "3rd    $name (from $source, listed in third-party.txt)"
    linked=$((linked + 1)); continue
  fi

  if [ -e "$dest/$name" ] && [ "$force" -eq 0 ]; then
    echo "skip   $name (already in repo, use --force to overwrite)"; skipped=$((skipped + 1)); continue
  fi
  rm -rf "${dest:?}/$name"
  # -L follows symlinks so the repo holds real files, not links into your home folder.
  cp -RL "${dir%/}" "$dest/$name"
  find "$dest/$name" \( -name '.DS_Store' -o -name 'node_modules' -o -name '__pycache__' -o -name '.env*' \) \
    -prune -exec rm -rf {} +
  echo "copy   $name"
  copied=$((copied + 1))
done

sort -u -o "$manifest" "$manifest"
echo "copied $copied, skipped $skipped, third-party $linked"
[ -f "$lock" ] || echo "note   no $lock found, so every skill was treated as yours; check skills/ for ones you didn't write"
node "$repo/scripts/validate.mjs" "$dest"
