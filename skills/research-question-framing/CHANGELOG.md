# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-07-11

- Tighten the hybrid trigger description from 439 to 376 characters (slimming batch 6), eval-gated by the new cross-skill routing suite (`skill-lifecycle-manager/eval/cross-skill-routing-cases.json`): three A/B runs, zero per-case routing regressions, candidate 27/27 on the final run (deepseek-v4-pro-guan judge via dmxapi). All negative redirects preserved.

## [0.1.2] - 2026-07-11

- Move the research-contract section template and the snow-module worked example to `references/research-contract.md` (slimming batch 5). Downstream routing stays in the body.

## [0.1.1] - 2026-07-10

- Converge the pressure-test step on the canonical gate contract owned by `research-lifecycle` (single skip criterion, non-simulated interactive grills).

## [0.1.0] - 2026-07-10

- Initial framing workflow for explanatory questions, scientific capability gaps, methods, data products and qualification decisions without imposing a closed task taxonomy.
