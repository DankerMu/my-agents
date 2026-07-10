# Project Structure & Module Organization

This repository is a monorepo for reusable skills, agents, hooks, and installable packs. Edit canonical sources in `skills/<name>/`, `agents/<name>/`, `hooks/<name>/`, and `packs/<name>/`, not projected runtime copies in `.agents/`, `.claude/`, or `.codex/`.

- Skill packages should contain `skill.json`, `SKILL.md`, and `CHANGELOG.md`; `eval/`, `references/`, `scripts/`, `projection.json`, and `tests/` are optional.
- Agent packages should contain `agent.json`, one concise canonical `AGENT.md`, at least one generated platform definition (`claude-code.md` or `codex.toml`), optional installable `references/`, and `CHANGELOG.md`. Edit `AGENT.md`, then run `npm run sync-agents`; do not hand-edit generated behavior regions in platform files.
- Hook packages should contain `hook.json`, `HOOK.md`, at least one platform fragment (`claude-code.json` for `.claude/settings.json`, `codex.json` for `.codex/hooks.json`), and `CHANGELOG.md`; shared shell scripts live in `scripts/`. Install copies `scripts/` into the target project's `.claude/hooks/<name>/` (or `.codex/hooks/<name>/`) and idempotently merges the fragment's `hooks` object into the platform config; uninstall removes only deep-equal managed entries.
- Pack packages should contain `pack.json`, `README.md`, and `CHANGELOG.md`; packs may bundle skills, agents, and hooks.
- Shared schemas live in `schemas/`; authoring tools live in `scripts/`; generated catalogs live in `docs/catalog/` and `dist/catalog.json`; longer research notes live in `research/`.
- Cross-package competition evals live under `eval/routing/`; unlike package-local evals, they use unlabeled prompts and declare expected winners, forbidden routes, allowed followups, and justified workflow depth.
- Treat installable skills and agents as self-contained packages. A skill or agent may reference another package conceptually, but it must not depend on another skill or agent package's private script paths. If no formal shared-runtime distribution mechanism exists, prefer local duplication over cross-package runtime dependencies.
- Local-only external reference repositories should live under `workspaces/references/`. If `.my-agents/reference-repos.json` exists, treat it as the discovery index for those references, but do not commit the manifest or the cloned repositories.
