"""
Worker Agent: Foundational Worker Persona Extension.

Derived from BaseAgent to encapsulate subagent workers in multi-agent workflows.
Abstracts the LLM model resolution and framework primitive instantiation,
allowing callers to configure name, instructions, tools, and output_key cleanly.
"""

import os
import sys
from typing import List, Any, Optional
from dotenv import load_dotenv
from google.adk import Agent

# Path resolution to enable root-level imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from core.base_agent import BaseAgent  # noqa: E402

load_dotenv(override=True)


class WorkerAgent(BaseAgent):
    """
    Specialized worker agent derived from BaseAgent.
    Abstracts model resolution and framework primitives from workflow sub-agents.
    """

    def __init__(
        self,
        name: str,
        instruction: str = "",
        instructions: str = "",
        tools: Optional[List[Any]] = None,
        output_key: Optional[str] = None,
        output_schema: Optional[Any] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        """
        Initializes the WorkerAgent.

        Args:
            name: The identity and name of the worker agent.
            instruction: System instructions / prompt defining the worker's task.
            instructions: Alias for instruction.
            tools: Optional list of tools / functions assigned to this worker.
            output_key: Optional session state key where the worker's response is stored.
            output_schema: Optional Pydantic BaseModel class for structured output.
            description: Optional human-readable description for multi-agent delegation.
            **kwargs: Additional configuration parameters passed to BaseAgent.
        """
        # Resolve instruction or instructions alias
        resolved_instruction = instruction or instructions
        kwargs["name"] = name
        kwargs["instruction"] = resolved_instruction
        super().__init__(**kwargs)

        self.tools = tools or []
        self.output_key = output_key
        self.output_schema = output_schema
        self.description = description or f"Specialized worker agent: {name}"

        # Build concrete framework primitive with abstracted model
        self.agent = self.build_agent()

    def build_agent(self) -> Agent:
        """
        Instantiates the concrete ADK Agent primitive with abstracted model,
        configured tools, output_key, and output_schema.
        """
        agent_kwargs = {
            "name": self.name,
            "model": self.model,  # Inherited from BaseAgent (resolved from LLM_MODEL env)
            "instruction": self.instruction,
            "description": self.description,
        }
        if self.tools:
            agent_kwargs["tools"] = self.tools
        if self.output_key:
            agent_kwargs["output_key"] = self.output_key
        if self.output_schema:
            agent_kwargs["output_schema"] = self.output_schema

        return Agent(**agent_kwargs)


# Instance for CLI discovery inside worker_agent package boundary
worker_agent = WorkerAgent(
    name="worker_agent",
    instruction="You are a specialized worker agent executing domain tasks in a multi-agent workflow.",
).agent
root_agent = worker_agent
