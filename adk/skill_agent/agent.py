"""
Skill Agent Runtime.
Agnostic execution kernel that extends SecuredToolAgent.
Carries NO hardcoded domain persona or static domain instructions.
Base instructions are loaded via inheritance, and domain intelligence is
specialized dynamically through injected skills and commands.
"""

import os
import sys
from typing import Dict, Any, List, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from secured_agent.agent import SecuredToolAgent  # noqa: E402
from skill_agent.skill_loader import SkillLoader  # noqa: E402
from skill_agent.hook_binder import hook_binder  # noqa: E402


class SkillAgent(SecuredToolAgent):
    """
    Stateless, domain-agnostic agent kernel extending SecuredToolAgent.
    Carries NO hardcoded domain persona or static domain intelligence.
    Bridges domain skills and deterministic commands injected via constructor (IoC).
    """

    def __init__(
        self,
        skills: Optional[List[str]] = None,
        commands: Optional[List[Any]] = None,
        **kwargs,
    ):
        kwargs.setdefault("name", "skill_agent")
        # Injected collections: zero hardcoded defaults inside the class
        self.skills = skills or []
        self.commands = commands or []

        # 1. Inherit core foundation: ToolAgent and SecuredToolAgent
        # ToolAgent registers BigQueryToolset and GCSToolset on self.agent.tools.
        # SecuredToolAgent registers security hooks and verifies system prompt signatures.
        super().__init__(**kwargs)

        self.skill_loader = SkillLoader()
        self.mounted_skills: Dict[str, Dict[str, Any]] = {}
        self.hook_binder = hook_binder

        # 2. Specialize instructions by mounting injected domain skills
        # Preserves inherited base instructions and appends signed skill prompt content
        self.register_skills()

        # 3. Mount injected commands as callable tools on the ADK agent
        self.register_command_tools()

    def register_skills(self):
        """
        Loads and verifies cryptographic HMAC signatures for each injected skill,
        specializing the agent's instructions with domain vocabulary and heuristics.
        """
        for skill_name in self.skills:
            self.mount_skill(skill_name)

    def mount_skill(self, skill_name: str):
        """
        Mounts a single domain skill by name into the agent envelope.
        Verifies cryptographic HMAC-SHA256 signature and appends prompt instructions.
        """
        print(f"🧩 [SkillAgent] Mounting skill: '{skill_name}'...")
        skill_data = self.skill_loader.load_skill(skill_name)
        self.mounted_skills[skill_name] = skill_data

        skill_prompt = (
            f"\n\n--- MOUNTED SKILL: {skill_data['name']} (v{skill_data['version']}) ---\n"
            f"{skill_data['instructions']}\n"
        )
        self.instruction = (self.instruction or "") + skill_prompt
        self.agent.instruction = self.instruction
        print(f"✅ [SkillAgent] Verified signature and mounted skill '{skill_name}'.")

    def register_command_tools(self):
        """
        Registers each injected command as a callable tool on the agent.
        The command's docstring serves as documentation for LLM tool invocation.
        """
        for cmd in self.commands:
            if hasattr(cmd, "get_tool_function"):
                self.agent.tools.append(cmd.get_tool_function())
            elif callable(cmd):
                self.agent.tools.append(cmd)


# =====================================================================
# Composition Root for Discovery & Harness (test_main.py, adk web)
# =====================================================================

def build_default_skill_agent() -> SkillAgent:
    """
    Composition root configuring the default skill agent for discovery.
    Injects:
      - Skills: 'mta' (domain drift heuristics) and 'bq' (warehouse constraints)
      - Commands: GetFileSampleCommand (GCS inspection) and IngestFileCommand (table provisioning)
    """
    from commands.gcs.get_file_sample import GetFileSampleCommand
    from commands.gcs.process_file import IngestFileCommand
    from commands.bq.create_external_table import bq_table_strategy
    from commands.snowflake.create_external_table import snowflake_table_strategy

    get_sample_command = GetFileSampleCommand()
    ingest_command = IngestFileCommand(
        strategies={
            "bigquery": bq_table_strategy,
            "snowflake": snowflake_table_strategy,
        },
        routing_config_path=os.path.join(ADK_ROOT, "config", "routing.yaml"),
    )

    agent_wrapper = SkillAgent(
        skills=["mta", "bq"],
        commands=[get_sample_command, ingest_command],
    )
    return agent_wrapper


# Singleton instance and discovery endpoints for ADK web & test_main.py
skill_agent_wrapper = build_default_skill_agent()
skill_agent = skill_agent_wrapper.agent
root_agent = skill_agent
