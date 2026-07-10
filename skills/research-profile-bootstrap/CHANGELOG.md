# Changelog

All notable changes to this skill will be documented in this file.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-10

- Guarantee bootstrap always persists `research/project-profile.md`, stamped Generic when the scan finds nothing project-specific, so downstream workflows never branch on a missing profile.
- Reference the canonical pressure-test contract owned by `research-lifecycle` from Step 5.
- Replace the `earth-science` tag with `domain-adaptive` to match the cross-domain contract.

## [0.1.0] - 2026-07-10

- Initial project-local research profile bootstrap and maintenance workflow.
- Separates scientific research profiles from the software-risk profile owned by `subagent-workflow` while defining an explicit handoff bridge.
