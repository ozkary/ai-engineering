import os
import sys

#  single import directives for the entire project
from dotenv import load_dotenv
from google.adk import Agent


# =====================================================================
# core base agent namespace
# =====================================================================

# path resolution to enable the import of this library
ADK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

load_dotenv()


class BaseAgent:
    """The foundational architectural block for our agent ecosystem."""

    def __init__(self, **kwargs):
        # project root for file based prompt resolution
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(base_dir)

        # Extract the agent's identity directly from the environment or kwargs
        self.name = kwargs.get("name") or os.getenv("AGENT_NAME", "base_agent")
        self.model = os.getenv("LLM_MODEL", "gemini-1.5-pro")  # Safe fallback model
        self.instruction = os.getenv("SYSTEM_PROMPT", "")
        self.agent = None
        for key, value in kwargs.items():
            if key != "name":
                setattr(self, key, value)


    def build_agent(self) -> Agent:
        """Instantiates the concrete framework primitive."""
        return Agent(name=self.name, model=self.model, instruction=self.instruction)

    def load_prompt_asset(self, file_path: str) -> str:
        """
        Safely resolves and reads the target Markdown specification asset.
        """
        try:
            # Resolves path cleanly relative to your active execution root
            clean_path = file_path.lstrip("./")
            absolute_path = os.path.join(self.project_root, clean_path)
            if os.path.exists(absolute_path):
                with open(absolute_path, "r", encoding="utf-8") as f:
                    self.instruction += f"\n\n {f.read().strip()}"
                    return

            print(f"Warning: Specification file not found at {absolute_path}")
            return ""
        except Exception as e:
            print(f"Error loading system prompt asset: {e}")
            return ""
