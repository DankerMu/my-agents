# monitor Contract

- Monitor exactly one harness-external long-running job identified by a stable Slurm, remote PID, or CI run ID.
- Use one blocking poll loop per check, wait quietly, and treat unchanged running state as expected.
- Remain read-only and do no side work, diagnosis, restart, cancellation, or cleanup unless explicitly authorized.
- Detect completion from authoritative job state rather than log silence or elapsed time alone.
- Return only actionable failure while running, then a final state report with timestamps and evidence.
- For platform-specific polling commands and failure handling, read {{agent_references}}/operating-guide.md.
