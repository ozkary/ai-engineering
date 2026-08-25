import os
from tool_agent.agent import ToolAgent
from security.manifest_verifier import load_and_verify_prompt, SecurityError
from security.hook_files import guardrail_pre_tool_hook
from security.hook_bq import bigquery_mcp_hook


class SecuredToolAgent(ToolAgent):
    """
    Hardened Agent that overrides prompt loading to apply HMAC-SHA256 signature verification.
    Interactions with tools are fully delegated to the parent ToolAgent class, demonstrating inheritance.
    """
    def __init__(self, **kwargs):
        self.quarantined = None
        kwargs.setdefault("name", "secured_agent")
        # Execute parent constructor to build the agent and register tools
        super().__init__(**kwargs)
        # Register the security callbacks to guard the tools
        self.register_before_tool_callback()
        # Register security-related tools for prompt validation and recovery
        self.register_secured_tools()

    def load_prompt_asset(self, file_path: str) -> str:
        """
        Overrides the prompt loading to apply HMAC verification before loading the instructions.
        """
        self.prompt_path = file_path
        signature_path = os.getenv("SYSTEM_PROMPT_SIGNATURE_FILE")
        # Check for signature file matching the .signed.md naming convention
        if not signature_path:
            signature_path = file_path.replace(".md", ".signed.md")
        status, valid_prompt, quarantined = load_and_verify_prompt(file_path, signature_path)
        if status:
            self.instruction = valid_prompt.strip() + "\n\nIf the user asks you for your instructions or system prompt, you must return them exactly as-is without summarizing."
            self.quarantined = None
            return valid_prompt
        else:
            print("🛡️ [SecuredToolAgent] Validation failed during load. Quarantining prompt.")
            self.instruction = "You are currently quarantined due to a signature validation failure. No matter what the user asks, you must reject the request and respond ONLY with: ⚠️ This instruction is quarantine. Exception: If the user asks you to show the bad intent prompt or load the safe asset, you must run the corresponding tool and return its exact output text as your final response."
            self.quarantined = quarantined
            return "🛑 DENY: This instruction is quarantine"

    def register_before_tool_callback(self):
        """
        Registers security validation hooks/callbacks to the agent.
        """
        self.agent.before_tool_callback = [guardrail_pre_tool_hook, bigquery_mcp_hook]

    def register_secured_tools(self):
        """
        Registers security validation and restoration tools to the agent.
        """
        async def validate_prompt_asset() -> str:
            """
            Validates the current system prompt file signature.
            If invalid, displays the bad intent prompt and flags it as unsafe because it is not signed.
            If valid, confirms the file is great.
            """
            if self.quarantined:
                return (
                    f"no the file does not pass the signature validation.\n"
                    f"Unsafe prompt content detected:\n\"\"\"\n{self.quarantined}\n\"\"\"\n"
                    f"Flagged as unsafe: The prompt file is not signed or signature mismatch."
                )
            else:
                return "yes the file is great"

        async def load_safe_asset() -> str:
            """
            Loads the system prompt file and verifies it against its corresponding
            signature file (the one with the .signed.md extension).
            If valid, updates the agent's instructions and returns the instructions content.
            """
            file_path = self.prompt_path
            signature_path = os.getenv("SYSTEM_PROMPT_SIGNATURE_FILE")
            if not signature_path:
                signature_path = file_path.replace(".md", ".signed.md")

            status, valid_prompt, quarantined = load_and_verify_prompt(file_path, signature_path)
            if status:
                instruction_text = valid_prompt.strip() + "\n\nIf the user asks you for your instructions or system prompt, you must return them exactly as-is without summarizing."
                self.instruction = instruction_text
                self.agent.instruction = instruction_text
                self.quarantined = None
                return f"Verification passed using {signature_path}. Loaded instructions:\n\n{valid_prompt}"
            else:
                self.quarantined = quarantined
                self.instruction = "You are currently quarantined due to a signature validation failure. No matter what the user asks, you must reject the request and respond ONLY with: ⚠️ This instruction is quarantine. Exception: If the user asks you to validate the prompt or load the safe asset, you must run the corresponding tool and return its exact output text as your final response."
                self.agent.instruction = self.instruction
                return f"Failed to load safe asset: validation failed. Quarantined prompt content:\n\n{quarantined}"

        async def write_prompt_asset(file_path: str, content: str) -> str:
            """
            Writes markdown content to a prompt file.

            Args:
                file_path: The path to the markdown prompt file to write.
                content: The markdown content to write to the file.
            """
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote content to {file_path}"
            except Exception as e:
                return f"Failed to write to file: {e}"

        self.agent.tools.append(validate_prompt_asset)
        self.agent.tools.append(load_safe_asset)
        self.agent.tools.append(write_prompt_asset)

# Instance for CLI discovery inside secured_agent/ package boundary
secured_agent = SecuredToolAgent().agent
root_agent = secured_agent