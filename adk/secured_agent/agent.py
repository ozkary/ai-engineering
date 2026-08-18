import os
from tool_agent.agent import ToolAgent
from security.manifest_verifier import load_and_verify_prompt, SecurityError


class SecuredToolAgent(ToolAgent):
    """
    Hardened Agent that overrides prompt loading to apply HMAC-SHA256 signature verification.
    Interactions with tools are fully delegated to the parent ToolAgent class, demonstrating inheritance.
    """
    def __init__(self, **kwargs):
        # Execute parent constructor to build the agent and register tools
        super().__init__(**kwargs)

    def load_prompt_asset(self, file_path: str) -> str:
        """
        Overrides the prompt loading to apply HMAC verification before loading the instructions.
        """
        print(f"🛡️ [SecuredToolAgent] Securely loading and verifying prompt asset: {file_path}")
        signature_path = os.getenv("SYSTEM_PROMPT_SIGNATURE_FILE")
        content = load_and_verify_prompt(file_path, signature_path)
        self.instruction += f"\n\n {content.strip()}"
        return content

# Instance for CLI discovery inside secured_agent/ package boundary
secured_agent = SecuredToolAgent().agent
root_agent = SecuredToolAgent().agent


