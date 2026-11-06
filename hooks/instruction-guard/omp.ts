// omp extension shim for instruction-guard. Installed at
// <config>/hooks/pre/instruction-guard.ts; delegates to the canonical shell
// guard copied to ../instruction-guard/instruction-guard.sh. omp's exec API has
// no stdin option, so the tool JSON is piped in via bash argv.
// edit / write calls pass their full input (path + content, replace strings,
// apply_patch or hashline text), so the guard can find the target files and
// compute the result where the edit mode allows; bash calls pass the command.
// Exit code 2 means a size-limit violation: the call is blocked with the guard's
// reason, which tells the model how to slim the file. Any other exit code lets
// the call through.
const SCRIPT = decodeURIComponent(
  new URL("../instruction-guard/instruction-guard.sh", import.meta.url).pathname
);
// A file tool can only reach a guarded file by naming it.
const GUARD_HINT = /AGENTS\.md|CLAUDE\.md/;

export default function hook(pi: any): void {
  pi.on("tool_call", async (event: any) => {
    const tool = event.toolName;
    if (tool !== "edit" && tool !== "write" && tool !== "bash") return;
    const input = event.input ?? {};
    const hinted = GUARD_HINT.test(JSON.stringify(input));
    if (tool !== "bash" && !hinted) return;
    const payload = JSON.stringify({
      tool_name: tool === "bash" ? "Bash" : tool,
      tool_input: tool === "bash" ? { command: String(input.command ?? "") } : input,
      cwd: process.cwd()
    });
    let result: any;
    try {
      result = await pi.exec(
        "bash",
        ["-c", 'printf %s "$1" | bash "$2" --platform omp', "omp-hook", payload, SCRIPT],
        { timeout: 15000 }
      );
    } catch {
      // Fail closed only when the call names an instruction file; anything else
      // stays non-blocking, same as a non-2 exit code.
      if (!hinted) return;
      return {
        block: true,
        reason: "instruction-guard: could not check this AGENTS.md / CLAUDE.md change"
      };
    }
    if (result.code !== 2) return;
    return {
      block: true,
      reason: result.stderr.trim() || "instruction-guard: AGENTS.md / CLAUDE.md size limit"
    };
  });
}
