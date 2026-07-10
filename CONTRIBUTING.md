# Contributing Guide

This repository uses `uv` for Python-backed validation and test helpers. If a workflow or `npm test` exercises packaged Python checks, prefer the documented `uv run ...` commands instead of relying on a manually managed virtualenv.

## Adding a New Skill

```bash
npm run new -- my-skill
npm run build
npm test
```

Conventions:

- Directory name must match `skill.json` `name` field (kebab-case)
- Required files: `skill.json`, `SKILL.md`, `CHANGELOG.md`
- `SKILL.md` frontmatter must declare exactly one `version` or `metadata.version`
  matching `skill.json.version`
- Categories must be from the whitelist in `categories.json`
- `SKILL.md` must be substantive (>= 200 characters) and include:
  - **Trigger** — when the skill should activate
  - **Instructions** — core behavioral prompt
  - **Examples** — concrete input/output demonstrations
  - **Caveats** — limitations and edge cases

## Updating a Skill

1. Edit `skills/<name>/SKILL.md` with your changes
2. Bump `version` in `skills/<name>/skill.json` and the matching embedded
   `SKILL.md` frontmatter version (SemVer)
3. Add a matching `## [x.y.z] - YYYY-MM-DD` section to `skills/<name>/CHANGELOG.md`
4. Run:

```bash
npm run build
npm test
```

Version guidance:

- `MAJOR`: Breaking changes (incompatible input/output/behavior)
- `MINOR`: Backward-compatible new capabilities
- `PATCH`: Backward-compatible bug fixes or doc improvements

## Adding a New Agent

```bash
npm run new -- --agent my-agent
npm run build
npm test
```

Conventions:

- Directory name must match `agent.json` `name` field (kebab-case)
- Required files: `agent.json`, canonical `AGENT.md`, at least one generated platform file (`claude-code.md` / `codex.toml`), and `CHANGELOG.md`
- `agent.json` requires an `archetype` field: `explorer`, `reviewer`, `implementer`, `planner`, `debugger`, or `custom`
- `AGENT.md` must contain 5-8 substantive behavior bullets covering role, output, and safety boundaries
- Put detailed workflows and templates in `references/operating-guide.md`; reference it with `{{agent_references}}` so installation can resolve the platform-specific path
- Edit platform metadata in `claude-code.md` / `codex.toml`, but regenerate their behavior regions with `npm run sync-agents`
- The `skills` array in `agent.json` references skills by name; validation checks they exist

When behavior changes, edit `AGENT.md`, bump `agent.json.version`, add the matching changelog section, then run `npm run sync-agents`. Put detailed workflows and templates in `references/operating-guide.md` instead of expanding the always-loaded contract.

## Adding a New Hook

```bash
npm run new -- --hook my-hook
npm run build
npm test
```

Conventions:

- Required files: `hook.json`, `HOOK.md`, `CHANGELOG.md`, and at least one platform fragment (`claude-code.json` or `codex.json`)
- Shared executable logic belongs in `scripts/`; fragments must declare only events listed in `hook.json.events`
- Install and uninstall must preserve unrelated user configuration and remove only deep-equal managed entries
- Packs and project manifests reference hooks by the `hook.json.name` value

## Adding a New Pack

```bash
npm run new -- --pack my-pack
npm run build
npm test
```

Pack membership may include skills, agents, and hooks. Every referenced package must exist, duplicates are invalid, and agent dependencies must be listed explicitly so installation remains reproducible.

## Metadata

Field definitions are in `schemas/skill.schema.json`, `schemas/agent.schema.json`, `schemas/hook.schema.json`, and `schemas/pack.schema.json` (enforced by CI).

Skill minimum required fields: `name`, `displayName`, `description`, `version`, `maturity`, `categories`, `authors`

Agent minimum required fields: all of the above plus `archetype`

Hook and Pack minimum fields are defined by their schemas and include the same identity/version fields plus their event or membership contracts.

## Adding a New Category

If any Skill, Agent, Hook, or Pack needs a category not in `categories.json`, add it there first, then use it in the corresponding metadata file.
