"""
Workflow Factory & Strategy Module for Google ADK Workflow Agents.

Implements the Strategy and Factory design patterns for NYC Transit Geo-Zone workflows:
  - WorkflowStrategy: Abstract interface for building and running workflow primitives.
  - Concrete Strategies: SequentialWorkflowStrategy, ParallelWorkflowStrategy,
    LoopWorkflowStrategy, CustomWorkflowStrategy.
  - WorkflowFactory: Central factory resolving strategies, lazily loading prompts
    from environment variables (using uppercase strategy name as key, e.g. SEQUENTIAL=prompts/...),
    and instantiating concrete workflow primitives.
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from workflow_agent.workflows import (  # noqa: E402
    build_sequential_agent,
    build_parallel_agent,
    build_loop_agent,
    build_custom_agent,
)


class WorkflowStrategy(ABC):
    """
    Abstract Base Strategy for Google ADK Workflow primitives.
    Encapsulates graph compilation for multi-agent orchestration.
    """
    name: str = ""
    default_prompt_file: str = ""

    @abstractmethod
    def build(self, instruction: str = "", **kwargs) -> Any:
        """Builds and returns the concrete ADK Workflow or Agent primitive."""
        pass


class SequentialWorkflowStrategy(WorkflowStrategy):
    """Strategy for multi-stage sequential WorkerAgent pipelines."""
    name = "sequential"
    default_prompt_file = "prompts/sequential_workflow_instructions.md"

    def build(self, instruction: str = "", **kwargs) -> Any:
        return build_sequential_agent(instruction=instruction, **kwargs)


class ParallelWorkflowStrategy(WorkflowStrategy):
    """Strategy for concurrent multi-zone WorkerAgent analytics and scorecard synthesis."""
    name = "parallel"
    default_prompt_file = "prompts/parallel_workflow_instructions.md"

    def build(self, instruction: str = "", **kwargs) -> Any:
        return build_parallel_agent(instruction=instruction, **kwargs)


class LoopWorkflowStrategy(WorkflowStrategy):
    """Strategy for iterative quality calibration WorkerAgent loops."""
    name = "loop"
    default_prompt_file = "prompts/loop_workflow_instructions.md"

    def build(self, instruction: str = "", max_iterations: int = 4, **kwargs) -> Any:
        return build_loop_agent(instruction=instruction, max_iterations=max_iterations, **kwargs)


class CustomWorkflowStrategy(WorkflowStrategy):
    """Strategy for dynamic context-aware WorkerAgent routing based on prompt intent."""
    name = "custom"
    default_prompt_file = "prompts/custom_workflow_instructions.md"

    def build(self, instruction: str = "", **kwargs) -> Any:
        return build_custom_agent(instruction=instruction, **kwargs)


class WorkflowFactory:
    """
    Factory for managing workflow strategies and lazily loading prompt assets
    using uppercase strategy names as environment variable keys (e.g. SEQUENTIAL=prompts/...).
    """

    _strategies: Dict[str, Type[WorkflowStrategy]] = {
        "sequential": SequentialWorkflowStrategy,
        "parallel": ParallelWorkflowStrategy,
        "loop": LoopWorkflowStrategy,
        "custom": CustomWorkflowStrategy,
    }

    prompt_cache: Dict[str, str] = {}

    @classmethod
    def register_strategy(cls, name: str, strategy_cls: Type[WorkflowStrategy]) -> None:
        """Registers a new workflow strategy into the factory registry."""
        cls._strategies[name.lower()] = strategy_cls

    @classmethod
    def get_strategy(cls, workflow_type: str) -> WorkflowStrategy:
        """
        Retrieves an instantiated strategy corresponding to the workflow type.
        Defaults to SequentialWorkflowStrategy if unknown.
        """
        strategy_cls = cls._strategies.get(workflow_type.lower())
        if not strategy_cls:
            strategy_cls = cls._strategies.get("sequential", SequentialWorkflowStrategy)
        return strategy_cls()

    @classmethod
    def get_prompt_path_for_strategy(cls, strategy_name: str) -> str:
        """
        Retrieves the prompt file path for the strategy from the environment variable.
        Uses the uppercase strategy name as the env key (e.g. SEQUENTIAL=prompts/sequential_workflow_instructions.md).
        If the setting or the directory does not exist, terminates execution immediately.
        """
        env_key = strategy_name.upper()
        prompt_setting = os.getenv(env_key)

        # Fallback for backward compatibility if SEQUENTIAL is not yet set in env
        if not prompt_setting and env_key == "SEQUENTIAL":
            prompt_setting = os.getenv("SYSTEM_PROMPT_FILE")

        if not prompt_setting:
            print(f"❌ Configuration Error: Environment setting '{env_key}' is not set.")
            sys.exit(1)

        # Resolve path cleanly without probing candidate locations
        if os.path.isabs(prompt_setting):
            resolved = prompt_setting
        else:
            if os.path.exists(os.path.join(CURRENT_DIR, prompt_setting)):
                resolved = os.path.join(CURRENT_DIR, prompt_setting)
            elif os.path.exists(os.path.join(ADK_ROOT, prompt_setting)):
                resolved = os.path.join(ADK_ROOT, prompt_setting)
            else:
                resolved = os.path.join(CURRENT_DIR, prompt_setting)

        prompt_folder = os.path.dirname(resolved)
        if not os.path.exists(prompt_folder) or not os.path.isdir(prompt_folder):
            print(f"❌ Configuration Error: Prompt folder '{prompt_folder}' does not exist.")
            sys.exit(1)

        if not os.path.exists(resolved):
            print(f"❌ Configuration Error: Prompt file '{resolved}' does not exist.")
            sys.exit(1)

        return os.path.abspath(resolved)

    @classmethod
    def load_prompt(cls, workflow_type: str, force_reload: bool = False) -> str:
        """
        Lazily loads and cryptographically verifies the prompt asset for the selected strategy.
        Cached in memory to eliminate redundant disk I/O and signature verification.
        """
        wtype = workflow_type.lower()
        if not force_reload and wtype in cls.prompt_cache:
            return cls.prompt_cache[wtype]

        prompt_path = cls.get_prompt_path_for_strategy(wtype)

        from security.manifest_verifier import load_and_verify_prompt
        signature_path = prompt_path.replace(".md", ".signed.md")
        status, valid_prompt, quarantined = load_and_verify_prompt(prompt_path, signature_path)

        if status:
            cls.prompt_cache[wtype] = valid_prompt.strip()
            return cls.prompt_cache[wtype]
        else:
            return "🛑 DENY: This instruction is quarantine"

    @classmethod
    def create_workflow(
        cls,
        workflow_type: str,
        instruction: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Factory method returning the concrete workflow primitive instance matching
        the selected strategy. Lazily loads the prompt if not explicitly provided.
        """
        strategy = cls.get_strategy(workflow_type)
        if instruction is None:
            instruction = cls.load_prompt(strategy.name)
        return strategy.build(instruction=instruction, **kwargs)
