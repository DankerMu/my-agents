const fs = require("node:fs/promises");
const path = require("node:path");

const { copyPath, fileExists, readJson, listDirs } = require("./fs-utils");
const { buildExcludedRoots, loadProjectionConfig, copySkillDirAtomic } = require("./projection");
const { getExternalAssetManagedKey, withExternalRepositoryCheckout } = require("./external-assets");
const {
  getSkillTargets,
  getAgentTargets,
  getHookTargets,
  getExternalAssetTarget
} = require("./runtime-targets");
const { mergeHooksConfig, removeHooksConfig } = require("./settings-merge");
const { REFERENCE_PLACEHOLDER } = require("./agent-contract");
const { parseSkillFrontmatter } = require("./validate-utils");
const {
  readPackMetadata,
  readProjectManifest,
  expandManifestMembers
} = require("./project-manifest");
const {
  ALL_PLATFORMS,
  PROJECT_SYNC_STATE_PATH,
  unique,
  uniqueSorted,
  difference
} = require("./install-shared");
const {
  normalizeManagedPlatformState,
  normalizeProjectSyncState,
  readProjectSyncState,
  writeProjectSyncState
} = require("./project-sync-state");
const {
  getProjectManifestManagedEntryKey,
  getProjectManifestRuntimeCollisionKey,
  parseProjectManifestManagedEntryKey
} = require("./project-manifest-entries");

async function removeDirRecursive(dir) {
  if (await fileExists(dir)) {
    await fs.rm(dir, { recursive: true, force: true });
    return true;
  }
  return false;
}

async function isUserInvokedSkillDoc(skillDocPath) {
  try {
    const content = await fs.readFile(skillDocPath, "utf8");
    const frontmatter = parseSkillFrontmatter(content);
    return frontmatter["disable-model-invocation"] === true;
  } catch {
    return false;
  }
}

async function installSkill(repoRoot, name, platforms, scope) {
  const skillDir = path.join(repoRoot, "skills", name);
  if (!(await fileExists(skillDir))) {
    console.error(`Skill not found: skills/${name}`);
    return false;
  }

  const skillJsonPath = path.join(skillDir, "skill.json");
  let skillDoc = "SKILL.md";
  if (await fileExists(skillJsonPath)) {
    const meta = await readJson(skillJsonPath);
    skillDoc = meta.entrypoints?.skillDoc ?? "SKILL.md";
  }

  const srcPath = path.join(skillDir, skillDoc);
  if (!(await fileExists(srcPath))) {
    console.error(`Skill doc not found: skills/${name}/${skillDoc}`);
    return false;
  }

  const userInvoked = await isUserInvokedSkillDoc(srcPath);
  const targets = getSkillTargets(name, platforms, scope, { userInvoked });
  const staleTargets = getSkillTargets(name, platforms, scope, { userInvoked: !userInvoked });
  const projectionConfig = await loadProjectionConfig(skillDir);
  let installed = 0;

  for (const target of targets) {
    const excludedRoots = buildExcludedRoots(projectionConfig, target.platformKey);
    await copySkillDirAtomic(skillDir, target.destDir, excludedRoots);
    console.log(`Installed (${target.platform}, ${scope}): ${target.destDir}/`);
    installed += 1;

    // A flag flip moves the codex location; drop the copy left at the old one
    // so the scanned and manual directories never hold the same skill twice.
    const stale = staleTargets.find(
      (entry) => entry.platformKey === target.platformKey && entry.destDir !== target.destDir
    );
    if (stale && (await removeDirRecursive(stale.destDir))) {
      console.log(`Removed stale copy (${stale.platform}, ${scope}): ${stale.destDir}/`);
    }
  }

  if (installed === 0) {
    console.error(`No targets matched for skill ${name}`);
    return false;
  }

  return true;
}

async function installAgent(repoRoot, name, platforms, scope) {
  const agentDir = path.join(repoRoot, "agents", name);
  if (!(await fileExists(agentDir))) {
    console.error(`Agent not found: agents/${name}`);
    return false;
  }

  const targets = getAgentTargets(name, platforms, scope);
  const referencesDir = path.join(agentDir, "references");
  const hasReferences = await fileExists(referencesDir);
  let installed = 0;

  for (const target of targets) {
    const srcPath = path.join(agentDir, target.srcFile);
    if (await fileExists(srcPath)) {
      await fs.mkdir(target.destDir, { recursive: true });
      const source = await fs.readFile(srcPath, "utf8");
      if (source.includes(REFERENCE_PLACEHOLDER) && !hasReferences) {
        console.error(
          `agents/${name}/${target.srcFile}: references ${REFERENCE_PLACEHOLDER} but agents/${name}/references is missing`
        );
        return false;
      }

      if (hasReferences) {
        await copyPath(referencesDir, target.referencesDestDir);
      } else {
        await removeDirRecursive(target.supportDestDir);
      }

      const portableReferencesPath = target.referencesDestDir.split(path.sep).join("/");
      const installedSource = source.replaceAll(REFERENCE_PLACEHOLDER, portableReferencesPath);
      await fs.writeFile(target.destPath, installedSource, "utf8");
      console.log(`Installed (${target.platform}, ${scope}): ${target.destPath}`);
      if (hasReferences) {
        console.log(
          `Installed (${target.platform}, ${scope}): agent references -> ${target.referencesDestDir}/`
        );
      }
      installed += 1;
    }
  }

  if (installed === 0) {
    console.error(`No platform files found in agents/${name}`);
    return false;
  }

  return true;
}

async function installHook(repoRoot, name, platforms, scope) {
  const hookDir = path.join(repoRoot, "hooks", name);
  if (!(await fileExists(hookDir))) {
    console.error(`Hook not found: hooks/${name}`);
    return false;
  }

  const targets = getHookTargets(name, platforms, scope);
  const scriptsDir = path.join(hookDir, "scripts");
  const hasScripts = await fileExists(scriptsDir);
  let installed = 0;

  for (const target of targets) {
    const fragmentPath = path.join(hookDir, target.fragmentFile);
    if (!(await fileExists(fragmentPath))) {
      continue;
    }

    let fragment;
    try {
      fragment = await readJson(fragmentPath);
    } catch (err) {
      console.error(`hooks/${name}/${target.fragmentFile}: invalid JSON (${err.message})`);
      return false;
    }

    if (hasScripts) {
      await fs.rm(target.scriptsDestDir, { recursive: true, force: true });
      await copyPath(scriptsDir, target.scriptsDestDir);
    }

    const added = await mergeHooksConfig(target.configPath, fragment.hooks);
    console.log(
      `Installed (${target.platform}, ${scope}): hook ${name} -> ${target.configPath} (${added} new entries)`
    );
    installed += 1;
  }

  if (installed === 0) {
    console.error(`No platform files found in hooks/${name} (claude-code.json or codex.json)`);
    return false;
  }

  return true;
}

async function uninstallHook(repoRoot, name, platforms, scope) {
  const hookDir = path.join(repoRoot, "hooks", name);
  const targets = getHookTargets(name, platforms, scope);

  for (const target of targets) {
    const fragmentPath = path.join(hookDir, target.fragmentFile);
    if (await fileExists(fragmentPath)) {
      try {
        const fragment = await readJson(fragmentPath);
        const removed = await removeHooksConfig(target.configPath, fragment.hooks);
        if (removed > 0) {
          console.log(
            `Uninstalled (${target.platform}, ${scope}): hook ${name} (${removed} entries from ${target.configPath})`
          );
        } else {
          console.log(`Not installed (${target.platform}, ${scope}): hook ${name}`);
        }
      } catch (err) {
        console.error(`hooks/${name}/${target.fragmentFile}: invalid JSON (${err.message})`);
      }
    }

    if (await removeDirRecursive(target.scriptsDestDir)) {
      console.log(`Removed (${target.platform}, ${scope}): ${target.scriptsDestDir}/`);
    }
  }

  return true;
}

async function uninstallSkill(name, platforms, scope) {
  // Cover both codex locations so a copy installed before/after a
  // disable-model-invocation flag change is still removed.
  const targets = [
    ...getSkillTargets(name, platforms, scope),
    ...getSkillTargets(name, platforms, scope, { userInvoked: true })
  ];
  const removedByPlatform = new Map();
  const seen = new Set();
  for (const target of targets) {
    if (seen.has(target.destDir)) continue;
    seen.add(target.destDir);
    if (await removeDirRecursive(target.destDir)) {
      removedByPlatform.set(target.platformKey, true);
      console.log(`Uninstalled (${target.platform}, ${scope}): ${target.destDir}/`);
    } else if (!removedByPlatform.has(target.platformKey)) {
      removedByPlatform.set(target.platformKey, false);
    }
  }
  for (const target of targets) {
    if (removedByPlatform.get(target.platformKey) === false) {
      removedByPlatform.set(target.platformKey, true);
      console.log(`Not installed (${target.platform}, ${scope}): ${target.destDir}/`);
    }
  }
  return true;
}

async function uninstallAgent(name, platforms, scope) {
  const targets = getAgentTargets(name, platforms, scope);
  for (const target of targets) {
    if (await fileExists(target.destPath)) {
      await fs.unlink(target.destPath);
      console.log(`Uninstalled (${target.platform}, ${scope}): ${target.destPath}`);
    } else {
      console.log(`Not installed (${target.platform}, ${scope}): ${target.destPath}`);
    }
    if (await removeDirRecursive(target.supportDestDir)) {
      console.log(`Removed (${target.platform}, ${scope}): ${target.supportDestDir}/`);
    }
  }
  return true;
}

async function installExternalAsset(kind, entry, scope) {
  let target;
  try {
    target = getExternalAssetTarget(kind, entry, scope);
  } catch (err) {
    console.error(err.message);
    return false;
  }

  try {
    await withExternalRepositoryCheckout(entry.repo, entry.resolvedCommit, async (checkoutPath) => {
      const srcPath = path.join(checkoutPath, ...entry.path.split("/"));
      if (!(await fileExists(srcPath))) {
        throw new Error(
          `External asset path not found at ${entry.repo}@${entry.resolvedCommit}:${entry.path}`
        );
      }

      const stats = await fs.stat(srcPath);
      if (kind === "skills") {
        if (!stats.isDirectory()) {
          throw new Error(`External skill must point to a directory: ${entry.sourceUrl}`);
        }

        const skillDocPath = path.join(srcPath, "SKILL.md");
        if (!(await fileExists(skillDocPath))) {
          throw new Error(`External skill directory is missing SKILL.md: ${entry.sourceUrl}`);
        }
      } else if (!stats.isFile()) {
        throw new Error(`External agent must point to a file: ${entry.sourceUrl}`);
      }

      await copyPath(srcPath, target.destPath);
    });
  } catch (err) {
    console.error(err.message);
    return false;
  }

  console.log(`Installed (${target.platform}, ${scope}): ${target.destPath}`);
  return true;
}

async function uninstallExternalAsset(kind, platform, name, scope) {
  const target = getExternalAssetTarget(kind, { platform, name }, scope);

  if (target.destType === "directory") {
    if (await removeDirRecursive(target.destPath)) {
      console.log(`Uninstalled (${target.platform}, ${scope}): ${target.destPath}/`);
    } else {
      console.log(`Not installed (${target.platform}, ${scope}): ${target.destPath}/`);
    }
    return true;
  }

  if (await fileExists(target.destPath)) {
    await fs.unlink(target.destPath);
    console.log(`Uninstalled (${target.platform}, ${scope}): ${target.destPath}`);
  } else {
    console.log(`Not installed (${target.platform}, ${scope}): ${target.destPath}`);
  }

  return true;
}

async function installPack(repoRoot, name, platforms, scope) {
  const pack = await readPackMetadata(repoRoot, name);
  if (!pack) {
    return false;
  }

  console.log(`Installing pack: ${name}`);
  let ok = true;

  for (const skillName of unique(pack.skills)) {
    if (!(await installSkill(repoRoot, skillName, platforms, scope))) {
      console.error(`Pack ${name}: failed to install skill "${skillName}"`);
      ok = false;
    }
  }

  for (const agentName of unique(pack.agents)) {
    if (!(await installAgent(repoRoot, agentName, platforms, scope))) {
      console.error(`Pack ${name}: failed to install agent "${agentName}"`);
      ok = false;
    }
  }

  for (const hookName of unique(pack.hooks)) {
    if (!(await installHook(repoRoot, hookName, platforms, scope))) {
      console.error(`Pack ${name}: failed to install hook "${hookName}"`);
      ok = false;
    }
  }

  if (ok) {
    console.log(`Installed pack: ${name}`);
  }

  return ok;
}

async function uninstallPack(repoRoot, name, platforms, scope) {
  const pack = await readPackMetadata(repoRoot, name);
  if (!pack) {
    return false;
  }

  console.log(`Uninstalling pack: ${name}`);
  for (const skillName of unique(pack.skills)) {
    await uninstallSkill(skillName, platforms, scope);
  }
  for (const agentName of unique(pack.agents)) {
    await uninstallAgent(agentName, platforms, scope);
  }
  for (const hookName of unique(pack.hooks)) {
    await uninstallHook(repoRoot, hookName, platforms, scope);
  }
  console.log(`Uninstalled pack: ${name}`);
  return true;
}

function buildDesiredManagedEntry(platform, expanded) {
  return {
    packs: uniqueSorted(expanded.packs),
    skills: uniqueSorted([
      ...expanded.effectiveLocalSkills.map((name) =>
        getProjectManifestManagedEntryKey("skill", name)
      ),
      ...expanded.externalSkills
        .filter((entry) => entry.platform === platform)
        .map((entry) => getExternalAssetManagedKey("skills", entry))
    ]),
    agents: uniqueSorted([
      ...expanded.effectiveLocalAgents.map((name) =>
        getProjectManifestManagedEntryKey("agent", name)
      ),
      ...expanded.externalAgents
        .filter((entry) => entry.platform === platform)
        .map((entry) => getExternalAssetManagedKey("agents", entry))
    ]),
    hooks: uniqueSorted(
      expanded.effectiveLocalHooks.map((name) => getProjectManifestManagedEntryKey("hook", name))
    )
  };
}

function collectRuntimeDestinationCollisions(expanded, effectivePlatforms) {
  const destinations = new Map();
  const errors = [];

  function record(kind, platform, name, label) {
    const key = getProjectManifestRuntimeCollisionKey(kind, platform, name);
    if (!destinations.has(key)) {
      destinations.set(key, label);
      return;
    }

    errors.push(
      `Runtime destination collision for ${platform} ${kind} "${name}": ${destinations.get(key)} conflicts with ${label}`
    );
  }

  for (const platform of effectivePlatforms) {
    for (const name of expanded.effectiveLocalSkills) {
      record("skill", platform, name, `local skill "${name}"`);
    }

    for (const name of expanded.effectiveLocalAgents) {
      record("agent", platform, name, `local agent "${name}"`);
    }

    for (const name of expanded.effectiveLocalHooks) {
      record("hook", platform, name, `local hook "${name}"`);
    }
  }

  for (const entry of expanded.externalSkills) {
    if (!effectivePlatforms.includes(entry.platform)) {
      errors.push(
        `External skill "${entry.name}" requires platform "${entry.platform}" but the selected platforms are ${effectivePlatforms.join(", ")}`
      );
      continue;
    }

    record("skill", entry.platform, entry.name, `external skill "${entry.name}"`);
  }

  for (const entry of expanded.externalAgents) {
    if (!effectivePlatforms.includes(entry.platform)) {
      errors.push(
        `External agent "${entry.name}" requires platform "${entry.platform}" but the selected platforms are ${effectivePlatforms.join(", ")}`
      );
      continue;
    }

    record("agent", entry.platform, entry.name, `external agent "${entry.name}"`);
  }

  return errors;
}

async function uninstallManagedProjectEntry(repoRoot, kind, managedKey, platform, scope) {
  const parsed = parseProjectManifestManagedEntryKey(managedKey);
  if (!parsed) {
    console.error(`Invalid managed entry key: ${managedKey}`);
    return false;
  }

  if (parsed.kind && parsed.kind !== kind) {
    console.error(`Managed entry kind mismatch for key: ${managedKey}`);
    return false;
  }

  if (parsed.source === "local") {
    if (kind === "skill") {
      return uninstallSkill(parsed.name, [platform], scope);
    }

    if (kind === "hook") {
      return uninstallHook(repoRoot, parsed.name, [platform], scope);
    }

    return uninstallAgent(parsed.name, [platform], scope);
  }

  return uninstallExternalAsset(
    kind === "skill" ? "skills" : "agents",
    parsed.platform,
    parsed.name,
    scope
  );
}

async function pruneManagedMembers(repoRoot, previousEntry, desiredEntry, platform) {
  let ok = true;

  for (const agentKey of difference(previousEntry.agents, desiredEntry.agents)) {
    if (!(await uninstallManagedProjectEntry(repoRoot, "agent", agentKey, platform, "project"))) {
      ok = false;
    }
  }

  for (const skillKey of difference(previousEntry.skills, desiredEntry.skills)) {
    if (!(await uninstallManagedProjectEntry(repoRoot, "skill", skillKey, platform, "project"))) {
      ok = false;
    }
  }

  for (const hookKey of difference(previousEntry.hooks, desiredEntry.hooks)) {
    if (!(await uninstallManagedProjectEntry(repoRoot, "hook", hookKey, platform, "project"))) {
      ok = false;
    }
  }

  return ok;
}

async function syncProject(repoRoot, manifestPath, cliPlatforms, platformsSpecified, prune) {
  const { manifest, resolvedPath } = await readProjectManifest(repoRoot, manifestPath);
  if (!manifest) {
    return false;
  }

  const expanded = await expandManifestMembers(repoRoot, manifest);
  if (!expanded.ok) {
    return false;
  }

  const effectivePlatforms = platformsSpecified
    ? cliPlatforms
    : manifest.platforms?.length
      ? manifest.platforms
      : [...ALL_PLATFORMS];
  const collisionErrors = collectRuntimeDestinationCollisions(expanded, effectivePlatforms);
  if (collisionErrors.length > 0) {
    for (const error of collisionErrors) {
      console.error(error);
    }
    return false;
  }

  const statePath = path.join(process.cwd(), PROJECT_SYNC_STATE_PATH);
  let previousState;
  try {
    previousState = await readProjectSyncState(statePath, { strict: prune });
  } catch (err) {
    console.error(err.message);
    return false;
  }

  const relativeManifestPath = path.relative(process.cwd(), resolvedPath) || manifestPath;
  console.log(`Syncing project manifest: ${relativeManifestPath}${prune ? " (prune)" : ""}`);

  let ok = true;
  for (const packName of expanded.packs) {
    if (!(await installPack(repoRoot, packName, effectivePlatforms, "project"))) {
      console.error(`Project manifest: failed to install pack "${packName}"`);
      ok = false;
    }
  }

  for (const skillName of expanded.directLocalSkills) {
    if (expanded.packSkills.includes(skillName)) {
      continue;
    }
    if (!(await installSkill(repoRoot, skillName, effectivePlatforms, "project"))) {
      console.error(`Project manifest: failed to install skill "${skillName}"`);
      ok = false;
    }
  }

  for (const agentName of expanded.directLocalAgents) {
    if (expanded.packAgents.includes(agentName)) {
      continue;
    }
    if (!(await installAgent(repoRoot, agentName, effectivePlatforms, "project"))) {
      console.error(`Project manifest: failed to install agent "${agentName}"`);
      ok = false;
    }
  }

  for (const hookName of expanded.directLocalHooks) {
    if (expanded.packHooks.includes(hookName)) {
      continue;
    }
    if (!(await installHook(repoRoot, hookName, effectivePlatforms, "project"))) {
      console.error(`Project manifest: failed to install hook "${hookName}"`);
      ok = false;
    }
  }

  for (const entry of expanded.externalSkills) {
    if (!(await installExternalAsset("skills", entry, "project"))) {
      console.error(`Project manifest: failed to install external skill "${entry.name}"`);
      ok = false;
    }
  }

  for (const entry of expanded.externalAgents) {
    if (!(await installExternalAsset("agents", entry, "project"))) {
      console.error(`Project manifest: failed to install external agent "${entry.name}"`);
      ok = false;
    }
  }

  if (!ok) {
    return false;
  }

  const nextState = normalizeProjectSyncState(previousState);
  for (const platform of effectivePlatforms) {
    const previousEntry = normalizeManagedPlatformState(nextState.platforms[platform]);
    const desiredEntry = buildDesiredManagedEntry(platform, expanded);

    if (prune) {
      if (!(await pruneManagedMembers(repoRoot, previousEntry, desiredEntry, platform))) {
        ok = false;
      }
      nextState.platforms[platform] = desiredEntry;
    } else {
      nextState.platforms[platform] = {
        packs: desiredEntry.packs,
        skills: uniqueSorted([...previousEntry.skills, ...desiredEntry.skills]),
        agents: uniqueSorted([...previousEntry.agents, ...desiredEntry.agents]),
        hooks: uniqueSorted([...previousEntry.hooks, ...desiredEntry.hooks])
      };
    }
  }

  if (!ok) {
    return false;
  }

  nextState.schemaVersion = 1;
  nextState.updatedAt = new Date().toISOString();
  nextState.manifestPath = relativeManifestPath;
  await writeProjectSyncState(statePath, nextState);

  console.log(`Wrote sync state: ${path.relative(process.cwd(), statePath)}`);
  console.log(`Synced project manifest: ${relativeManifestPath}`);
  return true;
}

async function runAll(repoRoot, type, platforms, scope, isUninstall) {
  const dirName =
    type === "agent" ? "agents" : type === "pack" ? "packs" : type === "hook" ? "hooks" : "skills";
  const names = (await listDirs(path.join(repoRoot, dirName))).sort((left, right) =>
    left.localeCompare(right)
  );
  let ok = true;

  for (const name of names) {
    let currentOk;
    if (type === "agent") {
      currentOk = isUninstall
        ? await uninstallAgent(name, platforms, scope)
        : await installAgent(repoRoot, name, platforms, scope);
    } else if (type === "pack") {
      currentOk = isUninstall
        ? await uninstallPack(repoRoot, name, platforms, scope)
        : await installPack(repoRoot, name, platforms, scope);
    } else if (type === "hook") {
      currentOk = isUninstall
        ? await uninstallHook(repoRoot, name, platforms, scope)
        : await installHook(repoRoot, name, platforms, scope);
    } else {
      currentOk = isUninstall
        ? await uninstallSkill(name, platforms, scope)
        : await installSkill(repoRoot, name, platforms, scope);
    }
    ok = currentOk && ok;
  }

  console.log(`\n${isUninstall ? "Uninstalled" : "Installed"} all ${names.length} ${dirName}.`);
  return ok;
}

module.exports = {
  installSkill,
  installAgent,
  installHook,
  installPack,
  uninstallSkill,
  uninstallAgent,
  uninstallHook,
  uninstallPack,
  syncProject,
  runAll
};
