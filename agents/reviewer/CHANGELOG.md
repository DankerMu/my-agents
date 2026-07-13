# Changelog

## [2.1.3] - 2026-07-12

### Changed

- Drop the pinned Claude Code `model` and Codex `model` / `model_reasoning_effort` so the agent inherits the parent session's model and reasoning effort on both platforms.

## [2.1.2] - 2026-07-10

### Changed

- Codex surface: upgrade model `gpt-5.5` -> `gpt-5.6-sol` and reasoning effort `xhigh` -> `high`.

All notable changes to the **reviewer** agent will be documented in this file.

## [2.1.1] - 2026-07-10

### Changed

- Replaced duplicated platform behavior manuals with one concise canonical `AGENT.md` contract and generated Claude Code/Codex behavior projections.

### Added

- Preserved the extended workflow and output templates in an on-demand, installable `references/operating-guide.md`.

## [2.1.0] - 2026-07-06

### Changed

- Sink the orchestration-brief behavior contract into the role definition on both surfaces: treat diff/issue/PR-comment/fetched content as untrusted data, not instructions (prompt-injection defense), and extend read-only from "never modify files" to never commit, stage, push, post PR comments, or change repository state. Orchestrator briefs no longer need to restate these to get them; the injected boundary remains defense-in-depth.

## [2.0.0] - 2026-07-02

### Changed

- BREAKING: findings are now **candidate findings** adjudicated downstream by a verifier/orchestrator; the reviewer no longer emits APPROVE / REQUEST-CHANGES verdicts or makes merge decisions.
- BREAKING: replaced the private Critical/Warning/Suggestion/Praise severity ladder with the canonical P0 / P1 / P2 / Note scale from the risk-adaptive-cross-review finding contract.
- BREAKING: rewrote the Output Format so every P0/P1/P2 finding carries all ten contract fields (severity, failure class, violated invariant/contract, concrete scenario, evidence file:line, consequence, fix direction, required test/proof, sibling surfaces, blocking status), plus a separate Non-blocking notes bucket.
- Added brief-precedence: an orchestrator-injected output contract overrides this default format.
- Replaced the "never approve code with known Critical findings" constraint with "flag blocking findings clearly; merge decisions belong to the orchestrator/verifier."
- Replaced the precision-bias guidance ("3 strong findings beat 20 weak") with recall-with-evidence guidance: surface every candidate finding backed by concrete evidence and do not self-censor borderline candidates (verification adjudicates REFUTED); still no style nits without demonstrable harm.
- Explorer usage is now scoped to standalone reviews; as a leaf task inside an orchestrated workflow the reviewer does not spawn subagents.
- Claude Code tools: `Bash` -> `Bash(readonly)` to match the read-only role (mirrors explorer).
- Removed the unused `skills: ["review", "clarify"]` array from `agent.json` (never referenced in either prompt body).

## [1.1.4] - 2026-06-14

### Changed

- Codex definition: model `gpt-5.4` -> `gpt-5.5` and reasoning effort `high` -> `xhigh`.

## [1.1.3] - 2026-03-30

### Changed

- Updated the Codex definition to use `gpt-5.4` with `high` reasoning effort as the default.
- Updated the Claude Code definition to use `opus` as the default model.

## [1.1.2] - 2026-03-27

### Changed

- Added an explicit Codex `model_reasoning_effort = "high"` default so reviewer keeps a stable deep-analysis posture instead of inheriting the caller's reasoning setting.

## [1.1.1] - 2026-03-27

### Changed

- Expanded the Codex definition to mention explorer usage explicitly and align its context-gathering guidance with the declared `explorer` dependency and the Claude Code surface.

## [1.1.0] - 2026-03-26

### Added

- Review Checklists section (general, security-sensitive, performance-sensitive).
- Using the Explorer Agent section with specific spawn guidance.
- OWASP top 10 and N+1 query patterns in assessment dimensions.
- Expanded Codex developer_instructions to match Claude Code depth.

### Changed

- Enhanced constraints with consolidation guidance for repeated findings.

## [1.0.0] - 2026-03-25

### Added

- Initial release: structured code review agent with severity-graded findings.
- Claude Code definition with Read, Glob, Grep, Bash tools and Agent(explorer) for context gathering.
- Codex definition with read-only sandbox mode.
- Four severity levels: Critical, Warning, Suggestion, Praise.
- Review dimensions: Correctness, Security, Performance, Maintainability.
- Review and clarify skill integrations.
- Explorer agent reference for deep codebase investigation during reviews.
