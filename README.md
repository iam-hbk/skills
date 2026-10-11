# skills

My agent skills, kept in one place and installed into any agent that reads
`SKILL.md` (Claude Code, Codex, Cursor, Gemini CLI, OpenCode and others) with the
[`skills`](https://github.com/vercel-labs/skills) CLI.

## Layout

Each skill is a folder under `skills/`:

```
skills/<name>/
  SKILL.md        # required: frontmatter with name + description, then instructions
  scripts/ ...    # optional helper scripts, templates, references
```

`SKILL.md` frontmatter:

```yaml
---
name: my-skill            # lowercase, digits, single hyphens; must equal the folder name
description: What it does and when to use it.   # max 1024 characters
---
```

Keep skills agent-agnostic. Describe actions in plain words ("ask the user",
"run the tests") instead of one agent's tool names, and avoid hard-coded paths
such as `~/.claude/`. Agent-specific frontmatter (for example Claude Code's
`user-invocable`) is fine, other agents ignore it.

## Install

```bash
git clone git@github.com:iam-hbk/skills.git && cd skills
scripts/install.sh                         # my skills + third-party ones, prompts for agents
scripts/install.sh -a claude-code -a codex # specific agents, no agent prompt
npx skills update -g                       # update everything later
```

`install.sh` runs `npx skills add iam-hbk/skills -g --skill '*'`, then installs
each skill in `third-party.txt` from its own upstream repo. Skills land once in
`~/.agents/skills/` and are linked into each agent's folder (for example
`~/.claude/skills/`). To install only my skills: `npx skills add iam-hbk/skills -g`.

## Third-party skills

Skills written by other people are not copied into `skills/`. They are listed in
`third-party.txt` as `<source> <skill>` (for example `vercel-labs/skills find-skills`),
so they install from upstream, keep getting updates, and stay under their
authors' licenses. Add a line by hand, or let `scripts/import-local.sh` add it.

## Updating

```bash
npx skills update -g          # every installed skill, mine and third-party
npx skills update -g <skill>  # just one
```

The CLI records each skill's source in `~/.agents/.skill-lock.json` and pulls the
newest version from it. Nothing updates on its own; run the command when you
want changes. My own skills update the same way after I push to this repo.

Third-party skills follow their repo's default branch (`main`, then `master`), so
whatever the author pushes arrives on the next update. Skills run with the
agent's full permissions, so pin authors you don't fully trust to a tag:

```
https://github.com/<owner>/<repo>.git#v1.2.0 <skill>
```

A pinned skill stays on that tag through `npx skills update`. To move it, edit
the tag here and run `scripts/install.sh` again. `scripts/import-local.sh` keeps
any pin a skill already has on this machine.

### Claude Code cloud sessions

Cloud sessions don't see your local `~/.claude/skills`. Add this to the cloud
environment's setup script:

```bash
git clone -q https://github.com/iam-hbk/skills.git /opt/skills
/opt/skills/scripts/install.sh -a claude-code
```

This repo is private, so the session needs GitHub access to it (the Claude GitHub
App installed on this repo).

## Add or update skills

```bash
scripts/import-local.sh                            # import from ~/.claude/skills
scripts/import-local.sh ~/.agents/skills --force   # another source, overwrite existing
node scripts/validate.mjs                          # check every skill
```

The import never commits. It reads `~/.agents/.skill-lock.json` (written by the
`skills` CLI) to tell my skills from installed third-party ones. It copies mine
into `skills/`, following symlinks and dropping `.env*`, `node_modules` and OS
junk, and adds third-party ones to `third-party.txt`. Skills copied in by hand
have no lock entry, so they count as mine; remove any I didn't write before
committing. The validator fails on a missing or mismatched `name`, a missing or
over-long `description`, or anything that looks like a secret, and warns about
content only some agents understand.
