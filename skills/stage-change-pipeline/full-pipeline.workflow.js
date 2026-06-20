export const meta = {
  name: "stage-pipeline-run",
  description: "Single invocation for Stage 3→5.5: review-loop, issue creation, issue-alignment",
  phases: [
    { title: "Review Loop", detail: "Stage 3→4→4.5 review-fix-verify" },
    {
      title: "Issue Creation",
      detail: "Stage 5 GitHub issue creation"
    },
    {
      title: "Alignment Review",
      detail: "Stage 5.5 issue-change alignment"
    }
  ]
};

// args: {
//   changeName: string,
//   designDocs?: string[],
//   stageLabel?: string,
//   skillDir?: string       — directory containing the companion workflow scripts
// }

const ISSUE_RESULT_SCHEMA = {
  type: "object",
  properties: {
    epicNumber: {
      type: "number",
      description: "The GitHub issue number of the created Epic"
    },
    subIssueNumbers: {
      type: "array",
      items: { type: "number" },
      description: "GitHub issue numbers of created sub-issues"
    }
  },
  required: ["epicNumber", "subIssueNumbers"]
};

const changeName = args.changeName;
const changePath = `openspec/changes/${changeName}`;
const designDocs = args.designDocs || [];
const stageLabel = args.stageLabel || "";
const skillDir = args.skillDir || "skills/stage-change-pipeline";

// ── Stage 3→4.5: Review Loop ───────────────────────────────────

phase("Review Loop");
log(`Starting review loop for change: ${changeName}`);

const reviewResult = await workflow(
  { scriptPath: `${skillDir}/review-loop.workflow.js` },
  { changeName, designDocs }
);

log(
  `Review loop: ${reviewResult.verdict} (${reviewResult.rounds} rounds, ${reviewResult.residual.length} residual, ${reviewResult.whackAMoleCount || 0} whack-a-mole)`
);

const residualNote =
  reviewResult.residual.length > 0
    ? `\n\nThe following findings were NOT fully resolved after ${reviewResult.rounds} rounds. Mark each in the relevant sub-issue body with **needs-followup** and record it in the Epic:\n${reviewResult.residual.map((f) => `- [${f.severity}] ${f.id}: ${f.title}`).join("\n")}`
    : "";

// ── Stage 5: Issue Creation ────────────────────────────────────

phase("Issue Creation");
log("Creating GitHub issues from reviewed change");

const issueResult = await agent(
  `Create GitHub issues for the reviewed OpenSpec change at "${changePath}".

Instructions:
1. Run: gh auth status — confirm authenticated
2. Create labels (epic, sub-task, priority, stage labels) using: gh label create <name> --color <hex> --description "<desc>" --force
3. Create an Epic issue with: overview, design doc references, sub-task placeholders, dependency graph
4. Read tasks.md from the change, generate sub-issue groupings — one module per issue, small-PR scope
5. Create sub-issues, each with:
   - Part of #<epic> link
   - Dependencies: #<dep1>, #<dep2>
   - Module / Scope: <module-or-path>
   - In Scope / Out of Scope
   - PR Boundary
   - Task checklist (from tasks.md, checkbox format)
   - Required reading docs with priority and focus sections
   - Acceptance criteria
   - Implementation Ready: yes
6. Backfill the Epic with the final sub-issue list and dependency graph
${residualNote}

Return the Epic number and all sub-issue numbers as structured output.`,
  {
    label: "create-issues",
    phase: "Issue Creation",
    schema: ISSUE_RESULT_SCHEMA
  }
);

if (!issueResult || !issueResult.epicNumber) {
  log("Issue creation failed or returned no Epic number — cannot run alignment review");
  return {
    reviewResult,
    issueCreation: issueResult,
    alignmentResult: null,
    verdict: "error"
  };
}

log(
  `Created Epic #${issueResult.epicNumber} with ${issueResult.subIssueNumbers.length} sub-issues`
);

// ── Stage 5.5: Issue-Change Alignment ──────────────────────────

phase("Alignment Review");
log(`Starting alignment review: Epic #${issueResult.epicNumber} vs change ${changeName}`);

const alignmentResult = await workflow(
  { scriptPath: `${skillDir}/issue-alignment.workflow.js` },
  { changeName, epicNumber: issueResult.epicNumber, stageLabel }
);

log(
  `Alignment review: ${alignmentResult.verdict} (${alignmentResult.rounds} rounds, ${alignmentResult.residual.length} residual)`
);

const overallVerdict =
  reviewResult.verdict === "clean" && alignmentResult.verdict === "clean" ? "clean" : "residual";

return {
  verdict: overallVerdict,
  reviewResult,
  epicNumber: issueResult.epicNumber,
  subIssueCount: issueResult.subIssueNumbers.length,
  alignmentResult
};
