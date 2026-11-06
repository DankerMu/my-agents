// omp extension shim for instruction-guard. Installed at
// <config>/hooks/pre/instruction-guard.ts; delegates to the canonical shell
// guard copied to ../instruction-guard/instruction-guard.sh. omp's exec API has
// no stdin option, so the Claude-style tool JSON is piped in via bash argv.
// Exit code 2 means "needs the user's approval": with a UI, omp's own confirm
// dialog asks (dialog wait time does not count toward the handler timeout);
// without one, the call is blocked with the guard's reason, which tells the
// model how the user can approve. Any other exit code lets the call through.
const SCRIPT = decodeURIComponent(
  new URL("../instruction-guard/instruction-guard.sh", import.meta.url).pathname
);

export default function hook(pi: any): void {
  pi.on("tool_call", async (event: any, ctx: any) => {
    const tool = event.toolName;
    if (tool !== "edit" && tool !== "write" && tool !== "bash") return;
    const input = event.input ?? {};
    const toolInput =
      tool === "bash"
        ? { command: String(input.command ?? "") }
        : {
            paths: Array.isArray(input.paths)
              ? input.paths.map(String)
              : input.path
                ? [String(input.path)]
                : []
          };
    const payload = JSON.stringify({
      tool_name: tool === "bash" ? "Bash" : tool,
      tool_input: toolInput,
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
      return; // Script or runtime failure is non-blocking, same as a non-2 exit code.
    }
    if (result.code !== 2) return;
    const reason =
      result.stderr.trim() || "instruction-guard: AGENTS.md / CLAUDE.md change needs approval";
    if (ctx?.hasUI && typeof ctx.ui?.confirm === "function") {
      const approved = await ctx.ui.confirm("Allow this AGENTS.md / CLAUDE.md change?", reason);
      if (approved) return;
      return {
        block: true,
        reason: "instruction-guard: the user declined this AGENTS.md / CLAUDE.md change"
      };
    }
    return { block: true, reason };
  });
}
