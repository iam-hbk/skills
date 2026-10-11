#!/usr/bin/env node
// Checks every skills/<name>/SKILL.md against the cross-agent Agent Skills format
// that `npx skills` installs. Errors break installs for every agent; warnings mark
// content only some agents understand. Usage: node scripts/validate.mjs [skills-dir]
import { readdirSync, readFileSync, statSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(process.argv[2] ?? "skills");
const NAME = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const SHARED_KEYS = new Set(["name", "description", "license", "compatibility", "metadata", "allowed-tools"]);
const AGENT_SPECIFIC = [
  [/\b(TaskCreate|TaskUpdate|TodoWrite|AskUserQuestion|ToolSearch|SendMessage)\b/, "Claude Code tool name"],
  [/subagent_type|\bthe Agent tool\b/, "Claude Code subagent call"],
  [/\$\{CLAUDE_PLUGIN_ROOT\}|\$\{CLAUDE_PLUGIN_DATA\}/, "Claude Code plugin variable"],
  [/~\/\.claude\//, "hard-coded ~/.claude path"],
];
const SECRET = [
  [/\b(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,})/, "looks like an API token"],
  [/-----BEGIN [A-Z ]*PRIVATE KEY-----/, "private key"],
];

function frontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return null;
  const fields = {};
  const lines = m[1].split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const kv = lines[i].match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!kv) continue;
    let [, key, value] = kv;
    if (/^[|>][+-]?$/.test(value) || value === "") {
      const block = [];
      while (i + 1 < lines.length && /^\s+\S|^\s*$/.test(lines[i + 1])) block.push(lines[++i].trim());
      value = block.join(" ").trim();
    }
    fields[key] = value.replace(/^(["'])([\s\S]*)\1$/, "$2");
  }
  return { fields, body: text.slice(m[0].length) };
}

function* files(dir) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) yield* files(p);
    else yield p;
  }
}

const errors = [];
const warnings = [];
const dirs = existsSync(root) ? readdirSync(root).filter((d) => statSync(join(root, d)).isDirectory()) : [];

for (const dir of dirs) {
  const skillFile = join(root, dir, "SKILL.md");
  if (!existsSync(skillFile)) { errors.push(`${dir}: no SKILL.md`); continue; }
  const parsed = frontmatter(readFileSync(skillFile, "utf8"));
  if (!parsed) { errors.push(`${dir}: SKILL.md has no --- frontmatter block`); continue; }
  const { name, description } = parsed.fields;

  if (!name) errors.push(`${dir}: missing name`);
  else if (name !== dir) errors.push(`${dir}: name "${name}" must match its folder name`);
  else if (!NAME.test(name) || name.length > 64) errors.push(`${dir}: name must be lowercase letters, digits and single hyphens, max 64`);
  if (!description) errors.push(`${dir}: missing description`);
  else if (description.length > 1024) errors.push(`${dir}: description is ${description.length} chars, max 1024`);

  const extra = Object.keys(parsed.fields).filter((k) => !SHARED_KEYS.has(k));
  if (extra.length) warnings.push(`${dir}: frontmatter ${extra.join(", ")} only works in some agents (others ignore it)`);

  for (const file of files(join(root, dir))) {
    const text = readFileSync(file, "utf8");
    const rel = file.slice(root.length + 1);
    for (const [re, what] of SECRET) if (re.test(text)) errors.push(`${rel}: ${what}, remove it before committing`);
    if (!file.endsWith(".md")) continue;
    for (const [re, what] of AGENT_SPECIFIC) if (re.test(text)) warnings.push(`${rel}: ${what} (${text.match(re)[0]})`);
  }
}

for (const w of warnings) console.log(`warn   ${w}`);
for (const e of errors) console.log(`ERROR  ${e}`);
console.log(`${dirs.length} skills, ${errors.length} errors, ${warnings.length} warnings`);
process.exit(errors.length ? 1 : 0);
