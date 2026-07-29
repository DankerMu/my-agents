---
name: readme-craftsman
description: "Create, update, or review a repository README when the user explicitly asks for README work. Use it to draft a new README, refresh an existing README after project changes, or audit a README against the current repository. Do not use it for general documentation, API docs, architecture docs, or documentation tasks that do not specifically target a README file. Not for trivial single-line README edits such as fixing a typo — just make the edit directly."
version: 1.2.0
---

# README Craftsman

Create, update, or review README files by analyzing the actual repository and tailoring output to the project type and audience. Works for any GitHub repository — software, documentation sites, datasets, research repos, tutorials, community collections. The goal is READMEs that are accurate, scannable, and genuinely useful — not generic filler.

```
Detect Mode → Analyze Project → Classify Type → [Interview if Creating] → Generate/Update/Review → Quality Check → Deliver
```

## When Not To Use

- General documentation work not targeting a `README.md` — `docs/` governance belongs to `project-documentation`
- API references, architecture docs, runbooks, docs-site pages, standalone user guides
- Generic writing requests ("write docs", "document the API") with no explicit README ask

## Step 1: Detect Task Mode

| Mode | When | Approach |
|------|------|----------|
| **Create** | No README exists, or user asks to "create / write / generate a README" | Full generation from codebase analysis |
| **Update** | README exists and code has changed, or "update / refresh / sync the README" | Targeted section updates, preserving existing voice |
| **Review** | "review / check / audit the README" | Compare README against actual project state, report findings |

**Edge case — placeholder README**: a README with only a title, one-line description, or auto-generated stub content is Create mode, not Update — the existing content is not worth preserving. If the mode is still ambiguous, ask.

## Step 2: Deep Project Analysis

Before writing a single line, understand the project — this separates a useful README from a template dump. Read the project's metadata files, map the directory tree (2-3 levels), identify code vs content/data/community, and review existing docs and git activity. The full discovery checklist (per-ecosystem metadata files, universal checks, structure and doc scans) is in [references/project-analysis.md](references/project-analysis.md).

## Step 3: Classify Project Type

Classification drives section selection, tone, and which template file to read. Four families, each with detailed signal/audience/tone tables in [references/project-analysis.md](references/project-analysis.md):

| Family | Sub-types | Template file |
|---|---|---|
| **Software** | OSS library, web service/API, CLI tool, personal, internal/team, monorepo, config/dotfiles | `references/templates.md` |
| **Content & education** | Documentation/KB, tutorial/course, blog/content | `references/templates-content.md` |
| **Data & research** | Dataset, academic research | `references/templates-research.md` |
| **Community** | Awesome list, org profile, resource hub | `references/templates-community.md` |

If uncertain, confirm with the user.

## Step 4: Interview (Create Mode)

Ask only what the codebase can't tell you; skip anything the analysis already answered. Universal: the one-line pitch (if the repo has no description) and anything to exclude. Per-type question banks (datasets need provenance/limitations/citation; academic needs paper link and repro requirements; tutorials need skill level; etc.): [references/project-analysis.md](references/project-analysis.md). After drafting, ask: **"Anything I missed or got wrong?"**

## Step 5: Generate, Update, or Review

**Create** — select sections with [references/section-guide.md](references/section-guide.md) (section matrix, writing guide, GitHub Markdown features), then follow the family template file from Step 3. Writing principles:

- **Lead with the problem.** The first thing a reader grasps is what pain this addresses — not how clever the implementation is.
- **Cognitive funneling.** Broad → specific: name → one-liner → visual → usage → install → API → contributing. A reader should get value even if they stop early.
- **Show, don't claim.** Replace "blazing fast" with a benchmark; "easy to use" with a 3-line example.
- **Copy-pasteable commands.** Every command works when pasted; pin versions where it matters.
- **Earn every sentence.** A 50-line README for a small utility beats a 500-line one padded with boilerplate.
- **Trust signals near installation.** Badges (CI, version, license) above the fold.

**Update** — (1) diff the codebase against what the README describes; (2) map changes to sections using the change-mapping table in [references/project-analysis.md](references/project-analysis.md); (3) preserve the existing voice — don't rewrite accurate sections; (4) show proposed changes (before/after for small edits, add/remove/modify list for larger ones) and wait for confirmation; (5) validate cross-references — links, file paths, version numbers.

**Review** — reality-check every claim (install commands, features, file paths); flag staleness (versions, screenshots, examples); assess completeness against the section matrix; run the quality checklist; deliver findings as **Critical** (incorrect information) / **Should Fix** (missing sections, stale content) / **Nice to Have** (polish, badges, format).

## Quality Check

Before delivering, run the checklist in [references/quality-standards.md](references/quality-standards.md) (full Must/Should/Nice ladder, anti-pattern table, exclusion rules). The non-negotiables: first paragraph answers "what is this and why should I care"; reader can get started from the README alone; at least one concrete example; no placeholders, secrets, or broken links; license section matches the LICENSE file. Never duplicate LICENSE/CONTRIBUTING/CHANGELOG/CODE_OF_CONDUCT/SECURITY contents — link to them.

## Examples

Five worked examples — create (library / awesome list / dataset), update, review — live in [references/examples.md](references/examples.md).

## Caveats

- **Scale README to project complexity.** A 3-file utility needs 30-50 lines, not 500. A large framework needs depth.
- **Don't overuse emojis** unless the project's existing style uses them.
- **Screenshots require files to exist.** If images don't exist yet, recommend what to capture and where to store them.
- **This skill writes READMEs, not full docs.** For standalone API/architecture docs or user guides, suggest separate tools.
- **Non-code repos need different instincts.** Datasets: schema and provenance over install steps. Tutorials: prerequisites and learning path. Community repos: contribution flow and navigation.
- **When in doubt, ask.** Project type, audience, and tone are judgment calls.
