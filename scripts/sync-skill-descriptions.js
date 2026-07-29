#!/usr/bin/env node
// Sync skill.json `description` from the SKILL.md frontmatter description.
// The frontmatter is the source of truth: it is what the model reads for
// routing, so the catalog metadata must follow it, not the other way around.
//
// Usage:
//   node scripts/sync-skill-descriptions.js          # rewrite drifted skill.json files
//   node scripts/sync-skill-descriptions.js --check  # exit 1 if any drift exists

const fs = require("fs/promises");
const path = require("path");
const { parseSkillFrontmatter } = require("./lib/validate-utils");

const repoRoot = path.resolve(__dirname, "..");

function normalizeDescription(value) {
  return String(value ?? "")
    .replace(/\s+/g, " ")
    .trim();
}

async function listDirs(dirPath) {
  const entries = await fs.readdir(dirPath, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

async function main() {
  const checkOnly = process.argv.includes("--check");
  const skillsRoot = path.join(repoRoot, "skills");
  const drifted = [];

  for (const dirName of await listDirs(skillsRoot)) {
    const skillJsonPath = path.join(skillsRoot, dirName, "skill.json");
    const skillDocPath = path.join(skillsRoot, dirName, "SKILL.md");

    let skill;
    let docContent;
    try {
      skill = JSON.parse(await fs.readFile(skillJsonPath, "utf8"));
      docContent = await fs.readFile(skillDocPath, "utf8");
    } catch {
      continue; // Missing files are validate.js's problem, not ours.
    }

    let frontmatter;
    try {
      frontmatter = parseSkillFrontmatter(docContent);
    } catch {
      continue;
    }

    const canonical = normalizeDescription(frontmatter.description);
    if (!canonical) continue;

    if (normalizeDescription(skill.description) !== canonical) {
      drifted.push(dirName);
      if (!checkOnly) {
        skill.description = canonical;
        await fs.writeFile(skillJsonPath, `${JSON.stringify(skill, null, 2)}\n`, "utf8");
      }
    }
  }

  if (drifted.length === 0) {
    console.log("skill descriptions: all in sync");
    return;
  }

  if (checkOnly) {
    console.error(
      `skill descriptions drifted from SKILL.md frontmatter in ${drifted.length} package(s):\n` +
        drifted.map((name) => `  - skills/${name}`).join("\n") +
        "\nRun `npm run sync-descriptions` to update skill.json from the frontmatter."
    );
    process.exitCode = 1;
    return;
  }

  console.log(`synced skill.json description from frontmatter for: ${drifted.join(", ")}`);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
