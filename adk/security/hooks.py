from google.adk.hooks import PreToolUseContext, PreToolUseDecision

def guardrail_pre_tool_hook(context: PreToolUseContext) -> PreToolUseDecision:
    """Provides pretooluse hooks for the agents"""
    tool_name = context.tool_name
    args = context.args

    # Policy 1: Protect System Prompt Files on Disk
    if "prompt_path" in args or "target_prompt_path" in args:
        target_file = args.get("target_prompt_path") or args.get("prompt_path")
        if target_file and target_file.endswith((".md", ".sig")):
            print(f"🛡️ [PreToolUse] DENY: Blocked unauthorized write/modify to {target_file}")
            return PreToolUseDecision.DENY(
                reason="Security Policy: System prompt files are read-only."
            )

    # Policy 2: Scan for Token Exfiltration in Tool Arguments
    for arg_name, arg_val in args.items():
        if isinstance(arg_val, str) and ("hf_" in arg_val or "postgres://" in arg_val):
            print(f"🛡️ [PreToolUse] DENY: Detected sensitive token leak in tool argument '{arg_name}'")
            return PreToolUseDecision.DENY(
                reason="Security Policy: Secret tokens cannot be passed as tool arguments."
            )

    return PreToolUseDecision.ALLOW()

# usage - register the hook on the ADK Agent or Runner
# agent.add_hook("pre_tool_use", guardrail_pre_tool_hook)