# Worked Examples

> Moved from SKILL.md: five end-to-end walkthroughs of the Detect → Analyze → Classify → Generate flow.

**Example 1: Creating a README for a new npm library**
```
User: "Write a README for this project"
→ Detect: no README.md exists → Create mode
→ Analyze: package.json (name: "retry-fetch", exports, deps), src/ has 3 modules, jest tests, MIT license
→ Classify: OSS Library (npm package, exports API)
→ Interview: "This looks like an npm library for HTTP retries. Any key differentiators?"
→ Generate: Title + 3 badges, one-liner, install, quick usage example, API reference, testing, contributing link, license
→ Quality check: all commands verified, no placeholders
→ Deliver with summary of design choices
```

**Example 2: Updating after adding features**
```
User: "I added WebSocket support and a new --verbose flag, update the README"
→ Detect: README exists + user specifies changes → Update mode
→ Map: WebSocket → Features + Usage + API; --verbose → Usage/CLI section
→ Preserve: existing tone, badge style, section ordering
→ Show diff before applying
```

**Example 3: Auditing an existing README**
```
User: "Is this README still accurate?"
→ Detect: review request → Review mode
→ Compare: README claims vs codebase reality
→ Find: badge shows v1.2 but package.json is v2.0; install command missing new peer dep; screenshot shows old UI
→ Report: 3 Critical, 2 Should Fix, 1 Nice to Have — with specific fixes for each
```

**Example 4: Creating a README for an awesome list**
```
User: "Write a README for this repo, it's a curated list of AI tools"
→ Detect: no README → Create mode
→ Analyze: awesome-ai-tools.md with 200+ links, organized by category, CONTRIBUTING.md with submission rules
→ Classify: Community / Organization (awesome list pattern)
→ Generate: Title + badges (awesome badge, PR welcome), description, table of contents, content overview by category, contributing guidelines, license
→ Quality check: all links verified, categories complete
```

**Example 5: Creating a README for a dataset**
```
User: "Create a README for this dataset repo"
→ Detect: no README → Create mode
→ Analyze: data/ with 3 parquet files, datapackage.json, LICENSE (CC-BY-4.0), notebooks/ with analysis examples
→ Classify: Dataset (data files, schema metadata, CC license)
→ Generate: Title + badges, description, data overview table (files, rows, columns, size), schema, how to load (Python/R examples), citation, license, provenance
```
