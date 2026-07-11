# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-07-11

- Compress When Not To Use into one-line arrows (slimming batch 4); all boundaries and redirect targets preserved.

## [0.1.2] - 2026-07-11

- Remove the body `## Example Prompts` section — dead weight once the skill is already invoked; git history keeps the prompts as trigger-eval candidates.
- Remove the `## Invocation Posture` section; posture lives in frontmatter/description and the scope boundary stays in When Not To Use.

## [0.1.1] - 2026-07-11
- Tighten the description to a lean identity + explicit-invocation clause (slimming batch 2): this skill is reached by name — by the user or an orchestrating skill — so trigger vocabulary and negative boundary lists move out of standing context into the body/router. Body and behavior unchanged.

## [0.1.0] - 2026-03-29

### Added
- Initial `project-documentation` skill focused on `docs/` directory governance, consolidation, refresh, and verification.
- Core `Structure`, `Refresh`, and `Verify` workflow with explicit boundaries against README-only, review, and research workflows.
- Docs-governance selection and verification reference guides for progressive disclosure.
- Lightweight trigger and qualitative eval fixtures plus projection settings for cross-platform installs.
