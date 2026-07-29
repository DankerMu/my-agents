# Project Analysis Reference

Detail for Steps 2–4: metadata discovery, project-type classification signals, and per-type interview questions.

## Metadata discovery (Step 2)

Read whichever of these exist to extract name, version, description, dependencies, scripts, and entry points:

**Software projects:**
- **JS/TS**: `package.json`, `tsconfig.json`
- **Python**: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`
- **Rust**: `Cargo.toml` | **Go**: `go.mod` | **Ruby**: `Gemfile`, `*.gemspec`
- **Java/Kotlin**: `pom.xml`, `build.gradle`, `build.gradle.kts`
- **PHP**: `composer.json` | **.NET**: `*.csproj`, `*.sln`

**Non-code projects:**
- **Doc sites**: `mkdocs.yml`, `docusaurus.config.js`, `.vitepress/`, `book.toml`, `_config.yml` (Jekyll)
- **Datasets**: `datapackage.json`, `dataset_info.json`, large `.csv`/`.parquet`/`.jsonl` files, `data/` dir
- **Academic**: `paper.tex`, `paper.pdf`, `notebooks/`, `experiments/`, `figures/`
- **Tutorials**: numbered directories (`01-intro/`, `02-basics/`), `exercises/`, `solutions/`
- **Blogs**: `_posts/`, `content/posts/`, `hugo.toml`, `gatsby-config.js`, `astro.config.mjs`
- **Community**: `awesome-*.md`, curated link lists, `.github/` org repo patterns

**Universal checks:**
- `LICENSE` / `LICENSE.md` — detect license type
- `.github/workflows/` — CI/CD pipelines, release workflows
- `Dockerfile`, `docker-compose.yml` — containerization setup
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` — community docs already present
- `.env.example`, `.env.template` — required environment variables
- `Makefile`, `justfile`, `Taskfile.yml` — available commands

**Repository structure**: map the directory tree (2-3 levels); identify code vs content/data/community project; for code: primary language(s), framework(s), entry points, test setup; for content: format, organization pattern, build/deploy pipeline; for data: file formats, size, schema info, provenance; check monorepo indicators (workspaces, lerna, turborepo, nx).

**Existing documentation**: read the existing README (Update/Review); check `docs/`, wiki links, API doc generation; scan key files for inline metadata; review git log briefly for maturity and activity level.

## Classification signals (Step 3)

### Software Projects → `templates.md`

| Type | Typical Signals | Primary Audience | Tone |
|------|----------------|-----------------|------|
| **OSS Library** | Published to package registry, exports API, has tests | Developers evaluating + integrating | Technical, concise, API-focused |
| **Web Service / API** | Server code, routes, database, deployment config | Developers deploying + operating | Operational, setup-heavy |
| **CLI Tool** | Binary/command entry, arg parsing, help text | End users installing + running | User-friendly, command-focused |
| **Personal / Portfolio** | Solo author, experimental, learning focus | Future self, portfolio viewers | Casual, highlights learnings |
| **Internal / Team** | Private repo, team references, internal URLs | Teammates, new hires onboarding | Practical, runbook-style |
| **Monorepo** | Workspace config, multiple packages/services | Contributors scoping to packages | Navigation-focused, per-package pointers |
| **Config / Dotfiles** | Config files, shell scripts, symlinks | Future self (confused) | Pragmatic, explains "why not just what" |

### Content & Education → `templates-content.md`

| Type | Typical Signals | Primary Audience | Tone |
|------|----------------|-----------------|------|
| **Documentation / Knowledge Base** | mkdocs.yml, docusaurus config, docs/ heavy, specification files | Readers seeking info, doc contributors | Clear, navigational, explains structure |
| **Tutorial / Course** | Numbered chapters/modules, exercises/, solutions/, progressive difficulty | Learners at a specific skill level | Encouraging, structured, prerequisite-aware |
| **Blog / Content** | _posts/, content/ dir, static site config (Hugo/Jekyll/Gatsby/Astro) | Readers, potential contributors | Inviting, explains how to read and write |

### Data & Research → `templates-research.md`

| Type | Typical Signals | Primary Audience | Tone |
|------|----------------|-----------------|------|
| **Dataset** | Large CSV/parquet/jsonl files, data/ dir, datapackage.json, data dictionaries | Data scientists, researchers | Precise, schema-focused, provenance-aware |
| **Academic Research** | paper.tex/pdf, notebooks/, experiments/, figures/, ML libs in requirements | Researchers reproducing or extending | Rigorous, reproducibility-focused, citation-ready |

### Community → `templates-community.md` (one template per sub-type — read the matching one)

| Type | Typical Signals | Primary Audience | Tone |
|------|----------------|-----------------|------|
| **Awesome List** | `awesome-*.md` filename, curated categorized links, Awesome badge | Community browsing, contributors adding | Welcoming, scannable, contribution-focused |
| **Organization Profile** | `.github` repo at org level, `profile/README.md` | GitHub visitors, potential contributors | Mission-driven, project showcase |
| **Resource Hub** | Topic collection, roadmaps, cheat sheets, study guides | Learners/practitioners in the topic | Educational, navigation-first |

## Interview question banks (Step 4, Create mode)

Ask only what the codebase can't tell you; skip questions already answered by analysis.

**All project types:**
1. **What's the one-line pitch?** — if the repo has no description. Becomes the opening line.
2. **Anything to exclude?** — sections that don't apply or content to keep private.

**Per type, if not inferable:**
- **Software**: primary audience? key differentiators vs alternatives?
- **Datasets**: how was the data collected/generated? known limitations or biases? preferred citation format (DOI, BibTeX, plain text)?
- **Academic research**: which paper does this accompany (title, venue, link)? hardware/environment requirements to reproduce?
- **Tutorials / courses**: target skill level and prerequisites? self-paced or structured course?
- **Documentation / knowledge bases**: primary reader? where should a first-time reader start?
- **Blogs / content**: intended audience? actively published or curated archive?
- **Community / resource hubs**: what belongs vs out of scope? how are contributions reviewed/maintained?

After drafting, ask: **"Anything I missed or got wrong?"**

## Update-mode change mapping (Step 5)

| Change | README Section(s) to Update |
|-------|----------------------------|
| New feature / export | Features, Usage, API Reference |
| New dependency / runtime | Prerequisites, Installation |
| New env variable | Configuration / Environment Variables |
| New CLI command / flag | Usage |
| Architecture change | Architecture, directory tree, diagrams |
| New deployment target | Deployment |
| Version bump | Badges, title, installation commands |
| New chapter / module (tutorials) | Table of Contents, Curriculum |
| New data file / column (datasets) | Data Description, Schema, File Inventory |
| New curated entry (awesome lists) | Relevant category section |
| New blog post category | Content overview, navigation |
| Paper revision (academic) | Abstract, Results, Citation |
