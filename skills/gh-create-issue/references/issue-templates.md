# Issue Body Templates

> Moved from SKILL.md. The required-vs-optional field contract stays in SKILL.md — these are the full body skeletons.

**Epic:**
```markdown
## Overview
<feature description>

## Sub-tasks
- [ ] #101 Task 1
- [ ] #102 Task 2

## Milestones
<phase goals>
```

**Sub-issue:**
```markdown
Part of #<epic_number>

Implementation Ready: yes

**Module / Scope:** <single module, package, service, or directory boundary>

Depends on #<dep1>
Depends on #<dep2>

**OpenSpec change:** <change-name>   <!-- optional; required when driven by stage-change-pipeline -->

## In Scope
- <behavior, files, or deliverables this issue includes>

## Out of Scope
- <adjacent modules or follow-up work explicitly excluded>

## Description
<task details>

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

**PR Boundary:** <expected change surface; adjacent modules explicitly not touched>
```
