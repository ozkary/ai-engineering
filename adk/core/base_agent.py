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

class BaseAgent:
    """The foundational architectural block for our agent ecosystem."""
    def __init__(self):
        load_dotenv()

        # Extract the agent's identity directly from the environment
        self.name = os.getenv("AGENT_NAME", "base_agent")
        self.model = os.getenv("LLM_MODEL", "gemini-5.5-flash")
        self.instruction = os.getenv(
            "SYSTEM_PROMPT", 
            ""
        )     

    def build_agent(self) -> Agent:
        """Instantiates the concrete framework primitive."""
        return Agent(
            name=self.name,
            model=self.model,
            instruction=self.instruction
        )
