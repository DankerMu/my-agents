const fs = require("node:fs/promises");
const path = require("node:path");

const DEFAULT_CONTRACT_FILE = "AGENT.md";
const REFERENCE_PLACEHOLDER = "{{agent_references}}";
const OPERATING_GUIDE = path.join("references", "operating-guide.md");

function normalizeContract(content) {
  return `${content.trim()}\n`;
}

function behaviorBullets(content) {
  return content.split(/\r?\n/).filter((line) => /^-\s+\S/.test(line));
}

function validateContractContent(content) {
  const errors = [];
  const normalized = normalizeContract(content);
  const bullets = behaviorBullets(normalized);

  if (!normalized.startsWith("# ")) {
    errors.push("AGENT.md must start with a level-one contract heading");
  }
  if (normalized.trim().length < 200) {
    errors.push(`AGENT.md is too short (${normalized.trim().length} chars, minimum 200)`);
  }
  if (bullets.length < 5 || bullets.length > 8) {
    errors.push(`AGENT.md must contain 5-8 behavior bullets (found ${bullets.length})`);
  }
  if (/\bTODO\b/.test(normalized)) {
    errors.push("AGENT.md must not contain TODO placeholders");
  }
  if (normalized.includes('"""')) {
    errors.push("AGENT.md cannot contain triple double quotes because it is projected into TOML");
  }

  return errors;
}

function renderFrontmatterProjection(existingContent, contractContent, label) {
  const match = existingContent.match(/^---\s*\r?\n[\s\S]*?\r?\n---/);
  if (!match) {
    throw new Error(`${label} must start with closed YAML frontmatter`);
  }
  return `${match[0]}\n\n${normalizeContract(contractContent)}`;
}

function renderClaudeProjection(existingContent, contractContent) {
  return renderFrontmatterProjection(existingContent, contractContent, "claude-code.md");
}

function renderOmpProjection(existingContent, contractContent) {
  return renderFrontmatterProjection(existingContent, contractContent, "omp.md");
}

function renderCodexProjection(existingContent, contractContent) {
  const pattern = /developer_instructions\s*=\s*"""[\s\S]*?"""/;
  if (!pattern.test(existingContent)) {
    throw new Error('codex.toml must contain a developer_instructions = """...""" block');
  }
  const replacement = `developer_instructions = """\n${contractContent.trim()}\n"""`;
  return existingContent.replace(pattern, replacement);
}

async function loadContractPath(agentDir) {
  const metadataPath = path.join(agentDir, "agent.json");
  const metadata = JSON.parse(await fs.readFile(metadataPath, "utf8"));
  const contractName = metadata.entrypoints?.contract ?? DEFAULT_CONTRACT_FILE;
  return path.join(agentDir, contractName);
}

async function expectedAgentProjections(agentDir) {
  const contractPath = await loadContractPath(agentDir);
  const contractContent = await fs.readFile(contractPath, "utf8");
  const projections = new Map();

  const claudePath = path.join(agentDir, "claude-code.md");
  try {
    const claudeContent = await fs.readFile(claudePath, "utf8");
    projections.set(claudePath, renderClaudeProjection(claudeContent, contractContent));
  } catch (err) {
    if (err.code !== "ENOENT") throw err;
  }

  const codexPath = path.join(agentDir, "codex.toml");
  try {
    const codexContent = await fs.readFile(codexPath, "utf8");
    projections.set(codexPath, renderCodexProjection(codexContent, contractContent));
  } catch (err) {
    if (err.code !== "ENOENT") throw err;
  }

  const ompPath = path.join(agentDir, "omp.md");
  try {
    const ompContent = await fs.readFile(ompPath, "utf8");
    projections.set(ompPath, renderOmpProjection(ompContent, contractContent));
  } catch (err) {
    if (err.code !== "ENOENT") throw err;
  }

  return { contractContent, contractPath, projections };
}

async function validateAgentContractPackage(agentDir) {
  const errors = [];
  let expected;
  try {
    expected = await expectedAgentProjections(agentDir);
  } catch (err) {
    return [err.message];
  }

  errors.push(...validateContractContent(expected.contractContent));

  const guidePath = path.join(agentDir, OPERATING_GUIDE);
  let guideExists = false;
  try {
    const guide = await fs.readFile(guidePath, "utf8");
    guideExists = true;
    if (guide.trim().length < 200) {
      errors.push(`${OPERATING_GUIDE} is too short (${guide.trim().length} chars, minimum 200)`);
    }
  } catch (err) {
    if (err.code !== "ENOENT") throw err;
  }

  const hasReferencePlaceholder = expected.contractContent.includes(REFERENCE_PLACEHOLDER);
  if (guideExists && !hasReferencePlaceholder) {
    errors.push(
      `${OPERATING_GUIDE} exists but AGENT.md does not reference ${REFERENCE_PLACEHOLDER}`
    );
  }
  if (hasReferencePlaceholder && !guideExists) {
    errors.push(`AGENT.md references ${REFERENCE_PLACEHOLDER} but ${OPERATING_GUIDE} is missing`);
  }

  for (const [projectionPath, projectedContent] of expected.projections) {
    const actual = await fs.readFile(projectionPath, "utf8");
    if (actual !== projectedContent) {
      errors.push(`${path.basename(projectionPath)} contract projection is out of date`);
    }
  }

  if (expected.projections.size === 0) {
    errors.push("agent must have at least one platform projection");
  }

  return errors;
}

async function syncAgentContractPackage(agentDir) {
  const expected = await expectedAgentProjections(agentDir);
  const contractErrors = validateContractContent(expected.contractContent);
  if (contractErrors.length > 0) {
    throw new Error(contractErrors.join("; "));
  }

  for (const [projectionPath, projectedContent] of expected.projections) {
    await fs.writeFile(projectionPath, projectedContent, "utf8");
  }
}

async function listAgentDirs(repoRoot) {
  const agentsRoot = path.join(repoRoot, "agents");
  const entries = await fs.readdir(agentsRoot, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(agentsRoot, entry.name))
    .sort();
}

async function syncAllAgentContracts(repoRoot) {
  for (const agentDir of await listAgentDirs(repoRoot)) {
    await syncAgentContractPackage(agentDir);
  }
}

async function validateAllAgentContracts(repoRoot) {
  const errors = [];
  for (const agentDir of await listAgentDirs(repoRoot)) {
    const name = path.basename(agentDir);
    for (const error of await validateAgentContractPackage(agentDir)) {
      errors.push(`agents/${name}: ${error}`);
    }
  }
  return errors;
}

module.exports = {
  DEFAULT_CONTRACT_FILE,
  OPERATING_GUIDE,
  REFERENCE_PLACEHOLDER,
  behaviorBullets,
  expectedAgentProjections,
  normalizeContract,
  renderClaudeProjection,
  renderCodexProjection,
  renderOmpProjection,
  syncAgentContractPackage,
  syncAllAgentContracts,
  validateAgentContractPackage,
  validateAllAgentContracts,
  validateContractContent
};
