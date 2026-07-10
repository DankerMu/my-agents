# Changelog

All notable changes to this pack will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-07-10

- Document coupling with `research-engineering`: approved scientific evidence may become a bounded product/operational input, while the PM workflow owns PRD, user outcomes, prioritization and backlog without broadening the scientific claim beyond its recorded scope.

## [0.3.0] - 2026-07-02

- Add `prd-authoring` (new skill, 0.1.0): the requirements-authoring capability the persona was missing — no PRD skill existed anywhere in the repo. It bridges the discovery skills (`clarify`/`brainstorming`/`deep-research`/`business-plan`) and `gh-create-issue`.

## [0.2.0] - 2026-07-02

- Add `gh-create-issue` and `project-documentation`: the pack previously stopped before backlog creation and docs governance; these close the discovery → backlog handoff for the PM persona.
- Fix README drift: `implementation-planning` was missing from the Included Skills list since 0.1.1; the skill list now matches `pack.json` and carries one-line rationales.
- Modernize the README install command to `npx my-agents install pack` (the `npm run install-pack --` form still works but sibling packs use the newer CLI form).

## [0.1.1] - 2026-03-28

- Added `implementation-planning` because the pack includes the `planner` agent and should install its deep-planning dependency explicitly.

## [0.1.0] - 2026-03-27

- Initial release.
