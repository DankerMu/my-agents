# Quality Standards

Run before delivering. The Must Pass list also appears in SKILL.md; this file adds the full ladder, anti-patterns, and exclusion rules.

## Quality checklist

### Must Pass
- [ ] First paragraph answers "what is this and why should I care?"
- [ ] Reader can get started (install, read, or navigate) from the README alone
- [ ] At least one concrete example (code snippet, data sample, content preview, or screenshot)
- [ ] No placeholder text (`[TODO]`, `Lorem ipsum`, `your-name-here`)
- [ ] No secrets, internal URLs, or private information
- [ ] All links and file paths are valid
- [ ] License section matches actual LICENSE file (if one exists)

### Should Pass
- [ ] Badges reflect real status (not placeholder URLs)
- [ ] Section order follows cognitive funneling (broad → specific)
- [ ] No marketing-speak or unsubstantiated superlatives
- [ ] Commands (if any) show expected output or error recovery
- [ ] Headings are descriptive, not generic

### Nice to Have
- [ ] Visual element present (screenshot, diagram, recording)
- [ ] Collapsible sections for verbose content
- [ ] GitHub admonitions for important callouts
- [ ] Dark/light mode images where applicable

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Wall of text, no structure | Readers scan, not read | Headers, tables, lists, code blocks |
| "Easy to use" / "blazing fast" | Unsubstantiated claims erode trust | Show a code example or benchmark |
| 10+ badges | Obscures the description | 3-5 meaningful badges |
| No install steps | "Just run it" isn't obvious | Full commands with prerequisites |
| Stale screenshots | Creates confusion | Use generated diagrams, or date screenshots |
| 500-line API dump | Nobody reads it | Link to API docs, show top examples |
| Duplicating CONTRIBUTING.md | Diverges over time | Link to the file, don't copy |
| "Active development" + no commits in 2 years | Dishonest | Reflect actual project status |
| README longer than the code | Overkill for small projects | Scale README to project size |

## Exclusion rules

Do not duplicate the full contents of dedicated repo files inside the README. Brief navigational sections pointing to these files are acceptable; do not copy the full text:

- LICENSE → link to `LICENSE` file
- CONTRIBUTING → link to `CONTRIBUTING.md`
- CHANGELOG → link to `CHANGELOG.md` or GitHub Releases
- CODE_OF_CONDUCT → link to `CODE_OF_CONDUCT.md`
- SECURITY → link to `SECURITY.md`

If these files exist, link or add a very short navigational summary. If they don't exist, don't invent them inside the README.
