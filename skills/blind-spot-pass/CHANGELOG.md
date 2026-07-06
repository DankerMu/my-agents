# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-07-06
- Initial release: pre-work blind-spot reconnaissance for unfamiliar territory, adapted from Thariq's "A Field Guide to Fable: Finding Your Unknowns". Inverse arrow of `grill-me` — digs the territory (codebase archaeology: history, sibling paradigms, tacit conventions, danger zones, adjacent surfaces) instead of interrogating the map (an existing plan).
- Hard rules: recon only, no implementation and no project-file writes; every blind spot carries evidence (file:line / commit / output) or is marked an assumption; consumes existing baselines (project profile, glossary, ADRs) instead of re-digging; only action-changing findings make the list.
- Deliverables: evidence-backed blind-spot list, a rewritten (better) task prompt, and a reference list. Exit routing: decision points → `grill-me`, tacit conventions worth persisting → `grill-with-docs`, out-of-scope landmines → `issue-scribe`/`gh-create-issue`, undecided direction → `brainstorming`.
