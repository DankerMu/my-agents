# My Agents

Language: English | [Chinese](README.zh-CN.md)

[![Validate](https://github.com/DankerMu/my-agents/actions/workflows/validate.yml/badge.svg)](https://github.com/DankerMu/my-agents/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A monorepo for authoring, validating, and publishing reusable skills, agents, hooks, and installable packs for Claude Code, Codex, and similar AI coding agents.

This repository keeps the canonical source of truth under `skills/`, `agents/`, `hooks/`, and `packs/`, generates discovery catalogs from that source, and provides scaffold/install tooling so the same content can be projected into different runtime surfaces.

> [!NOTE]
> Edit packages in `skills/`, `agents/`, `hooks/`, and `packs/`. Treat generated catalogs and project-scope runtime copies as derived artifacts.
> Root `AGENTS.md` and `CLAUDE.md` are generated contributor instruction files. Edit `instructions/root/` and regenerate them instead of hand-editing the root files.

## Quick Start

Prerequisites:

- Node.js 18 or newer
- `uv` for Python-backed validation and test helpers used by `npm test`

```bash
npm install
npm run new -- my-skill
npm run new -- --agent my-agent
npm run new -- --hook my-hook
npm run new -- --pack my-pack
npm run lint
npm run build
npm test
```

## Browse the Catalog

- [docs/catalog/skills.md](docs/catalog/skills.md) is the generated human-readable index of tracked skills.
- [docs/catalog/agents.md](docs/catalog/agents.md) is the generated human-readable index of tracked agents.
- [docs/catalog/hooks.md](docs/catalog/hooks.md) is the generated human-readable index of tracked hooks.
- [docs/catalog/packs.md](docs/catalog/packs.md) is the generated human-readable index of tracked packs.
- `dist/catalog.json` is the generated machine-readable index consumed by tooling.

For package authoring workflows, start with `skill-lifecycle-manager`, `agent-lifecycle-manager`, `hook-development`, and the generated catalogs under `docs/catalog/`.

## Metadata Conventions

- [schemas/skill.schema.json](schemas/skill.schema.json), [schemas/agent.schema.json](schemas/agent.schema.json), [schemas/hook.schema.json](schemas/hook.schema.json), [schemas/pack.schema.json](schemas/pack.schema.json), [schemas/project-manifest.schema.json](schemas/project-manifest.schema.json), and [schemas/catalog.schema.json](schemas/catalog.schema.json) define the machine-readable metadata contracts.
- [docs/metadata/skill-metadata-policy.md](docs/metadata/skill-metadata-policy.md) explains how to use `requirements`, `capabilities`, and `maturity` consistently across skill packages.
- Installable skills and agents are expected to stay self-contained after install. Avoid private cross-package runtime script dependencies; if no shared runtime distribution exists yet, prefer package-local copies.
- In `agent.json`, `agents` is the canonical cross-surface dependency graph. When a runtime projection needs a flatter direct-child surface, use `platformDependencies["claude-code"].agents` instead of distorting the canonical graph.
- [docs/metadata/pack-metadata-policy.md](docs/metadata/pack-metadata-policy.md) explains how to model pack membership, `packType`, and `persona` consistently.
- [docs/metadata/project-manifest-policy.md](docs/metadata/project-manifest-policy.md) explains how to use `my-agents.project.json` for repository bootstrap.
- [docs/cli/README.md](docs/cli/README.md) is the operator-facing command reference index.
- [docs/architecture/tooling-layout.md](docs/architecture/tooling-layout.md) explains how the tooling and docs are organized as the command surface grows.
- [docs/architecture/official-agent-best-practices.md](docs/architecture/official-agent-best-practices.md) distills official OpenAI, Anthropic, MCP, and Agent Skills guidance into repository design defaults.
- [research/OpenAI_Anthropic_Codex_Claude_Code_Best_Practices_20260329.md](research/OpenAI_Anthropic_Codex_Claude_Code_Best_Practices_20260329.md) keeps the longer source-backed research basis for those defaults.
- [instructions/root/shared.md](instructions/root/shared.md) is the source of truth for rules shared by Codex and Claude Code.
- [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), and [CONTRIBUTING.md](CONTRIBUTING.md) cover contributor workflow, release hygiene, and local conventions.

## Repository Layout

| Path                       | Purpose                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `docs/architecture/`       | Maintainer-oriented notes about tooling boundaries, projection flow, and repository architecture                               |
| `docs/catalog/`            | Generated Markdown catalogs for tracked skills, agents, hooks, and packs                                                       |
| `docs/cli/`                | Operator-facing command reference for runtime, sync, and maintenance workflows                                                 |
| `docs/metadata/`           | Repository-level metadata policy and authoring conventions                                                                     |
| `eval/routing/`            | Cross-skill competition suites with unlabeled prompts, expected winners, negative routes, and depth controls                   |
| `skills/<name>/`           | Canonical source packages for reusable skills (`skill.json`, `SKILL.md`, `CHANGELOG.md`)                                       |
| `agents/<name>/`           | Agent packages with canonical `AGENT.md`, optional `references/`, platform metadata/projections, and changelog                 |
| `hooks/<name>/`            | Canonical hook packages (`hook.json`, `HOOK.md`, platform fragments, scripts, `CHANGELOG.md`)                                  |
| `packs/<name>/`            | Canonical source packages for installable compositions of skills, agents, and hooks (`pack.json`, `README.md`, `CHANGELOG.md`) |
| `my-agents.project.json`   | Optional project bootstrap manifest consumed by `npx my-agents project sync`                                                   |
| `instructions/root/`       | Canonical source fragments used to generate root `AGENTS.md` and `CLAUDE.md`                                                   |
| `scripts/`                 | Scaffolding, install, catalog build, and validation tooling                                                                    |
| `schemas/`                 | JSON Schemas for skill, agent, hook, pack, project manifest, and catalog metadata                                              |
| `research/`                | Research notes, source digests, and longer-form background documents                                                           |
| `workspaces/<skill-name>/` | Evaluation sandboxes and scratch space for skill development                                                                   |
| `.my-agents/`              | Ignored local state such as project sync state and the optional `reference-repos.json` manifest                                |
| `.claude/` and `.agents/`  | Project-scope runtime projections created during local installation flows                                                      |

## Common Workflows

### Create a skill

```bash
npm run new -- my-skill
npm run build
npm test
```

This scaffolds `skills/my-skill/` with `skill.json`, `SKILL.md`, and `CHANGELOG.md`.

### Create an agent

```bash
npm run new -- --agent my-agent
npm run build
npm test
```

This scaffolds `agents/my-agent/` with `agent.json`, canonical `AGENT.md`, generated behavior regions in `claude-code.md` / `codex.toml`, and `CHANGELOG.md`.

### Create a hook

```bash
npm run new -- --hook my-hook
npm run build
npm test
```

This scaffolds `hooks/my-hook/` with `hook.json`, `HOOK.md`, platform configuration fragments, shared scripts, and `CHANGELOG.md`.

### Create a pack

```bash
npm run new -- --pack product-manager
npm run build
npm test
```

This scaffolds `packs/product-manager/` with `pack.json`, `README.md`, and `CHANGELOG.md`.

### Runtime and sync commands

```bash
npx my-agents --help
npx my-agents add https://github.com/affaan-m/everything-claude-code/tree/main/skills/agentic-engineering
npx my-agents install skill clarify
npx my-agents install hook worktree-guard
npx my-agents project sync --prune
npm run sync-instructions
npx my-agents references sync
```

The root README keeps only the highest-frequency entrypoints. Treat `npx my-agents ...` as the canonical runtime CLI surface; the `npm run ...` commands remain available as repo-local compatibility aliases. Use `npx my-agents --help` when you need the full CLI surface, including `install`, `uninstall`, `project sync`, `references`, `--platform`, `--scope`, `--manifest`, `--all`, and `--prune`. For the full command reference, examples, and behavior notes, see [docs/cli/runtime-and-sync-commands.md](docs/cli/runtime-and-sync-commands.md).
Unless you pass `--scope user` or narrow `--platform`, install and uninstall flows default to project scope across all supported platforms.

If you are bootstrapping a project manifest from scratch, start from [docs/examples/my-agents.project.example.json](docs/examples/my-agents.project.example.json).

Project manifests can now mix local package names with external official GitHub-backed assets. The `add <url>` flow resolves the URL to a structured manifest entry with an immutable commit SHA so `project sync` stays reproducible.

### Lint and format the repo

```bash
npm run lint
npm run lint:fix
npm run format
npm run format:check
```

ESLint covers the repo's JavaScript tooling and Prettier covers supported repository source files such as Markdown, JSON, YAML, and TOML. The versioned `pre-commit` hook runs a fast staged-file pass: it syncs root instructions and agent behavior projections, formats staged files, auto-fixes staged JavaScript when possible, and re-stages the results.

## Installation Targets

| Package type | Claude Code target                                                                                                         | Codex target                                                                                                    |
| ------------ | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Skill        | `~/.claude/skills/<name>/` or `.claude/skills/<name>/`                                                                     | `~/.agents/skills/<name>/` or `.agents/skills/<name>/`                                                          |
| Agent        | Definition at `.claude/agents/<name>.md`; on-demand guides under `.claude/agents/<name>/references/` (or user equivalents) | Definition at `.codex/agents/<name>.toml`; on-demand guides under `.codex/agents/<name>/references/`            |
| Hook         | Copies scripts to `.claude/hooks/<name>/` and merges `claude-code.json` into `.claude/settings.json` (or user equivalents) | Copies scripts to `.codex/hooks/<name>/` and merges `codex.json` into `.codex/hooks.json` (or user equivalents) |
| Pack         | Installs its referenced skills, agents, and hooks into the targets above                                                   | Installs its referenced skills, agents, and hooks into the targets above                                        |

## Generated Files

- `npm run build` synchronizes generated agent contract regions and regenerates `dist/catalog.json`, `docs/catalog/skills.md`, `docs/catalog/agents.md`, `docs/catalog/hooks.md`, and `docs/catalog/packs.md`.
- `npm run sync-agents` regenerates the behavior body in every platform Agent definition from canonical `agents/*/AGENT.md`.
- `npm run sync-instructions` regenerates the root `AGENTS.md` and `CLAUDE.md` files from `instructions/root/`.
- Do not hand-edit generated indexes or platform Agent behavior regions; update the underlying package or `AGENT.md` instead.
- Policy docs under `docs/metadata/` and instruction fragments under `instructions/root/` are source documents and should be edited directly when repository conventions change.
- Tooling structure guidance lives in [docs/architecture/tooling-layout.md](docs/architecture/tooling-layout.md).

## Validation and Release

- `npm test` runs `npm run validate`.
- Validation checks ESLint, Prettier, all four package schemas and directory conventions, embedded/changelog version alignment, pack and project-manifest references (including hooks), generated agent contracts and catalogs, generated root instructions, documentation quality, and packaged Python unit tests executed through `uv`.
- When metadata semantics change, update the canonical package, any relevant policy docs, then rerun `npm run build`, `npm run sync-instructions`, and `npm test` before committing.
- GitHub Actions runs validation on every push and pull request via `.github/workflows/validate.yml`.
- Dependabot keeps npm and GitHub Actions dependencies fresh via `.github/dependabot.yml`.
- Tagging `v*` triggers `.github/workflows/release.yml`, which assembles GitHub Release notes from skill, agent, hook, and pack changelogs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for authoring rules and release hygiene.

If you need a new category, add it to [categories.json](categories.json) before using it in `skill.json`, `agent.json`, `hook.json`, or `pack.json`.

## License

[MIT](LICENSE) - Qiongyu Li
