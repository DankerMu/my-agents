#!/usr/bin/env node

const path = require("node:path");

const { syncAllAgentContracts, validateAllAgentContracts } = require("./lib/agent-contract");

async function main() {
  const repoRoot = path.resolve(__dirname, "..");
  const check = process.argv.slice(2).includes("--check");

  if (check) {
    const errors = await validateAllAgentContracts(repoRoot);
    if (errors.length > 0) {
      console.error("Generated agent contracts are out of date:");
      for (const error of errors) console.error(`- ${error}`);
      process.exitCode = 1;
      return;
    }
    console.log("Generated agent contracts are up to date.");
    return;
  }

  await syncAllAgentContracts(repoRoot);
  console.log("Synchronized agent contract projections.");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
