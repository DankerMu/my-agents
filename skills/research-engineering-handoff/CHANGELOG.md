# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-10

- Own the delivery boundary gate one-way: verify `ENGINEERING_HANDOFF_READY` plus recorded human approval before invoking the pipeline, and state that the handoff pressure-test does not satisfy the delivery pipeline's own Stage-1 grill gate.
- Converge the pressure-test step on the canonical contract owned by `research-lifecycle`.
- Generalize the handoff template's coordinate/grid field for non-geospatial domains.

## [0.1.0] - 2026-07-10

- Initial bridge from approved research evidence to OpenSpec and issue delivery, preserving scientific invariants, oracle separation, verification/evaluation obligations, rollback, and human gates.
