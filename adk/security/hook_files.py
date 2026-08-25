import os
import re

async def guardrail_pre_tool_hook(tool, args: dict, tool_context) -> dict | None:
    """
    Standard ADK before_tool_callback that acts as a runtime security guardrail.
    Prevents specs and signature file modifications, and scans for token/env exfiltration.
    """
    tool_name = getattr(tool, "name", str(tool))

    # 1. Prevent specs and signature file modifications
    for arg_name, arg_val in args.items():
        if isinstance(arg_val, str):
            if arg_val.endswith((".md", ".sig", ".signed.md")) or "specs/" in arg_val or "/specs/" in arg_val:
                print(f"🛑 [PreToolUse] DENY: Blocked access/modification to system file or spec path: {arg_val}")
                raise PermissionError(f"🛑 [PreToolUse] DENY: Access/modification to system files or spec paths ({arg_val}) is forbidden.")

    # 2. Prevent token/env variable exfiltration
    for arg_name, arg_val in args.items():
        if isinstance(arg_val, str):
            # Check for secret tokens
            if any(pattern in arg_val for pattern in ["hf_", "postgres://", "os.environ", "os.getenv", "environ"]):
                print(f"🛑 [PreToolUse] DENY: Detected sensitive token/env pattern in argument '{arg_name}'")
                raise PermissionError("🛑 [PreToolUse] DENY: Secret tokens or environment variable access cannot be passed as tool arguments.")
            
            # Check for env variable exfiltration patterns
            if re.search(r'\$\{[a-zA-Z_][a-zA-Z0-9_]*\}|\$[a-zA-Z_][a-zA-Z0-9_]*', arg_val):
                print(f"🛑 [PreToolUse] DENY: Detected environment variable placeholder in argument '{arg_name}'")
                raise PermissionError("🛑 [PreToolUse] DENY: Environment variable references are not allowed in tool arguments.")

    print(f"✅ [PreToolUse] ALLOW: Tool '{tool_name}' execution permitted.")
    return None
