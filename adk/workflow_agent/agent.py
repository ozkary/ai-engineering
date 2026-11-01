"""
Workflow Agent: Orchestration Suite for NYC Transit Geo-Zone Commuter Intelligence.

This class inherits directly from `SecuredToolAgent` to maintain enterprise software engineering
reusability and strict security controls:
  - Cryptographic HMAC-SHA256 / SHA-256 prompt signature verification (.signed.md)
  - Native BigQuery and GCS toolsets for data warehouse operations
  - Self-training startup guide rendered from `skills/geo_fencing/SKILL.md`
  - Delegation to `WorkflowFactory` to resolve and build the active workflow strategy
"""

import os
import sys
from dotenv import load_dotenv
from security.manifest_verifier import load_and_verify_prompt
from secured_agent.agent import SecuredToolAgent  # noqa: E402
from workflow_agent.factory import WorkflowFactory  # noqa: E402
from workflow_agent.geo_tools import print_workflow_welcome_banner  # noqa: E402


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

load_dotenv(os.path.join(CURRENT_DIR, ".env"), override=True)


class WorkflowAgent(SecuredToolAgent):
    """
    Enterprise Workflow Agent extending SecuredToolAgent.
    Resolves the concrete workflow strategy via WorkflowFactory based on workflow_type,
    verifies prompt signatures, and displays a Skill-driven onboarding guide at startup.
    """

    def __init__(
        self,
        workflow_type: str = "sequential",
        **kwargs,
    ):
        """
        Initializes the WorkflowAgent, verifies cryptographic signatures, builds the
        active workflow primitive, and displays the workflow's self-training guide.

        Args:
            workflow_type: Target pattern ('sequential', 'parallel', 'loop', 'custom').
            **kwargs: Additional keyword arguments passed to parent constructors.
        """
        self.workflow_type = workflow_type.lower()
        kwargs.setdefault("name", "workflow_agent")

        full_prompt_path = WorkflowFactory.get_prompt_path_for_strategy(self.workflow_type)
        self.prompt_path = full_prompt_path

        os.environ["SYSTEM_PROMPT_FILE"] = full_prompt_path
        os.environ["SYSTEM_PROMPT_SIGNATURE_FILE"] = full_prompt_path.replace(".md", ".signed.md")

        super().__init__(**kwargs)

        self.strategy = WorkflowFactory.get_strategy(self.workflow_type)
        self.active_workflow = self.build_workflow()
        print_workflow_welcome_banner(self.workflow_type)

    def load_prompt_asset(self, file_path: str) -> str:
        """
        Loads prompt asset from resolved path and verifies cryptographic signature.
        """
        resolved_path = file_path if os.path.isabs(file_path) else os.path.abspath(os.path.join(CURRENT_DIR, file_path))
        folder = os.path.dirname(resolved_path)

        if not os.path.exists(folder) or not os.path.isdir(folder):
            print(f"❌ Configuration Error: Prompt folder '{folder}' does not exist.")
            sys.exit(1)

        if not os.path.exists(resolved_path):
            print(f"❌ Configuration Error: Prompt file '{resolved_path}' does not exist.")
            sys.exit(1)

        signature_path = resolved_path.replace(".md", ".signed.md")
        status, valid_prompt, quarantined = load_and_verify_prompt(resolved_path, signature_path)
        if status:
            self.instruction = valid_prompt.strip()
            self.prompt_path = resolved_path
            self.quarantined = None
            WorkflowFactory.prompt_cache[self.workflow_type] = self.instruction
            return valid_prompt
        else:
            self.quarantined = quarantined
            return "🛑 DENY: This instruction is quarantine"

    def build_workflow(self, **kwargs):
        """Builds the concrete workflow primitive for the active strategy."""
        return self.strategy.build(instruction=self.instruction, **kwargs)


# =============================================================================
# CLI and ADK Framework Discovery Instances
# =============================================================================
workflow_type_env = os.getenv("WORKFLOW_TYPE", "sequential")
workflow_agent_instance = WorkflowAgent(workflow_type=workflow_type_env)
workflow_agent = workflow_agent_instance.active_workflow
root_agent = workflow_agent
