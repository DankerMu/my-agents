# User-Invoked Skill Flags

User-invoked skills set `disable-model-invocation: true` in SKILL.md frontmatter. Consult this when adding, renaming, removing, or re-flagging a skill.

Per-platform behavior of the flag:

- **Claude Code** drops flagged skills from standing context — only `/name` reaches them.
- **Codex** installs/projections land in `.agents/skills-manual/` instead of `.agents/skills/`.
- **omp** honors the flag natively, so its copies stay in `.omp/skills/`.

Routing contract:

- The `ask-danker` router skill is the discovery surface for flagged skills. When you add, rename, remove, or re-flag any skill, or change a flow, update the router map in the same change.
- Validation fails if any skill — user-invoked especially — is missing from the router map.
- Never flag a skill that other skills or pipelines invoke mid-run: the flag would hide it from the model exactly when the pipeline needs it.
