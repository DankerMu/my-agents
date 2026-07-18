# Repository Guidelines

## Instruction Source Of Truth

The root `AGENTS.md` and `CLAUDE.md` files are generated outputs. Edit `instructions/root/shared.md` plus the relevant platform fragment (`instructions/root/codex.md` or `instructions/root/claude.md`) instead of hand-editing the generated files. Run `npm run sync-instructions` after changing those source files. Agent behavior regions are likewise generated from `agents/*/AGENT.md`; run `npm run sync-agents` instead of hand-editing those regions. The repo's versioned `pre-commit` hook auto-syncs and stages both generated surfaces, and `npm test` plus CI fail if they drift.

## Reference

- `instructions/root/reference/structure.md` — project layout, package conventions, directory roles. Consult when creating or reorganizing packages.
- `instructions/root/reference/commands.md` — build, test, lint, install, and scaffolding commands. Consult when you need to run or document a command.

## Coding Style & Naming Conventions

Match the existing style in surrounding files. JavaScript in `scripts/` uses CommonJS, 2-space indentation, semicolons, and double quotes. Python helpers use 4-space indentation and should stay deterministic and CLI-friendly. Use kebab-case for package directories and keep `name` fields in `skill.json`, `agent.json`, `hook.json`, and `pack.json` aligned with the folder name. Prefer ASCII Markdown. Do not hand-edit generated catalogs, `dist/catalog.json`, or the generated root instruction files.

## Quality & Validation Rules

- Categories must come from `categories.json`; add a new category there before using it in package metadata.
- Skill docs, canonical agent contracts and operating guides, hook docs (`HOOK.md`), and pack READMEs must be substantive and not placeholders.
- When a version changes in `skill.json`, `agent.json`, `hook.json`, or `pack.json`, add a matching `## [x.y.z]` entry to the package `CHANGELOG.md`.
- Follow SemVer: MAJOR for breaking changes, MINOR for new capabilities, PATCH for fixes.
- Run `npm run sync-instructions`, `npm run build`, and `npm test` before opening a PR after changing canonical packages, metadata, generated outputs, or contributor instructions.
- The versioned `pre-commit` hook keeps local commits fast: it syncs root instructions, formats staged files, auto-fixes staged JavaScript where possible, and re-stages the results.
- Validation checks schema compliance, directory conventions, changelog/version alignment, category whitelists, pack and project-manifest reference integrity, canonical agent-contract budgets and projection freshness, generated catalog/instruction freshness, and packaged Python unit tests that participate in the shared validation path.
- User-invoked skills set `disable-model-invocation: true` in SKILL.md frontmatter: Claude Code drops them from standing context (only `/name` reaches them), Codex installs/projections land in `.agents/skills-manual/` instead of `.agents/skills/`, and omp honors the flag natively so its copies stay in `.omp/skills/`. The `ask-danker` router skill is their discovery surface — when you add, rename, remove, or re-flag any skill, or change a flow, update the router map in the same change; validation fails if a user-invoked skill is missing from it. Never flag a skill that other skills or pipelines invoke mid-run.

## GitHub & Contribution Workflow

Use Conventional Commits such as `feat(skills): add skill lifecycle manager workflow` or `chore(catalog): refresh generated metadata`. Keep PRs focused, explain whether the change affects canonical packages, generated outputs, install flows, or local-only behavior, and link any relevant issue or research note. GitHub Actions runs `npm test` on every push and PR via `.github/workflows/validate.yml`. Tagging `v*` triggers `.github/workflows/release.yml`, which assembles GitHub Release notes from skill, agent, hook, and pack changelogs.

## Common Gotchas

- `dist/catalog.json` contains a volatile `generatedAt` timestamp; freshness checks compare the durable catalog fields, not that timestamp.
- Schema `$id` values under `schemas/` point at GitHub raw URLs; update them if the repo is renamed or transferred.
- Keep root guidance concise and push package-specific operating details into the relevant `SKILL.md`, agent `AGENT.md` / `references/`, hook `HOOK.md`, pack `README.md`, or changelog.

## Observable Completion

After completing work, include an `Execution Summary` using this canonical format by default:

`Execution Summary: agents=<...>; skills=<...>; tools=<...>; verification=<...>; limits=<...>`

- Keep it lightweight and factual. Do not expose hidden reasoning or chain-of-thought.
- `agents`, `skills`, `tools`, and `verification` must always be present. Use `none` when not used.
- `limits` may be omitted if there are no meaningful limits or blockers.
- For trivial tasks, the default one-line format is enough.
- If the summary would be too long, use the same keys on separate lines in the same order.
