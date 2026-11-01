"""
Custom Workflow Orchestration for Dynamic Context-Aware Geo-Zone Routing.

Demonstrates how to build a custom `Workflow` or `BaseAgent` orchestrator that
uses an intent-resolving `WorkerAgent` and conditional routing edges to dispatch
requests dynamically to specialized worker agents or sub-workflows.
"""

import os
import sys
from typing import Any

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from google.adk.workflow import Workflow, START  # noqa: E402
from google.adk.agents.invocation_context import InvocationContext  # noqa: E402
from google.adk.events import Event  # noqa: E402
from worker_agent import WorkerAgent  # noqa: E402
from workflow_agent.geo_tools import (  # noqa: E402
    resolve_geo_intent,
    identify_peak_window,
)
from workflow_agent.workflows.sequential import build_sequential_agent  # noqa: E402
from workflow_agent.workflows.parallel import build_parallel_agent  # noqa: E402
from workflow_agent.workflows.loop import build_loop_agent  # noqa: E402


def build_custom_agent(
    instruction: str = "",
    **kwargs,
) -> Workflow:
    """
    Builds a dynamic routing ADK Workflow that analyzes user intent via a router
    WorkerAgent and branches execution to the appropriate specialist or sub-workflow.

    Args:
        instruction: Cryptographically verified system instruction text.
        **kwargs: Optional configuration parameters.

    Returns:
        google.adk.workflow.Workflow instance.
    """
    intent_router = WorkerAgent(
        name="GeoZoneDynamicRouter",
        instruction=(
            f"{instruction}\n\n"
            "You are the Geo-Zone Dynamic Router. Call `resolve_geo_intent(user_prompt=...)` "
            "with the user's request to classify the geographic entity and workflow route."
        ),
        tools=[resolve_geo_intent],
        output_key="resolved_intent",
    ).agent

    midtown_specialist = WorkerAgent(
        name="MidtownZoneSpecialist",
        instruction=(
            f"{instruction}\n\n"
            "You are the Midtown Zone Specialist. Call `identify_peak_window(zone_id='ZONE_MIDTOWN_COMMERCIAL')` "
            "and present the Midtown commuter mobility findings."
        ),
        tools=[identify_peak_window],
        output_key="specialist_output",
    ).agent

    downtown_specialist = WorkerAgent(
        name="DowntownFinancialSpecialist",
        instruction=(
            f"{instruction}\n\n"
            "You are the Downtown Financial Specialist. Call `identify_peak_window(zone_id='ZONE_DOWNTOWN_FINANCIAL')` "
            "and present the Financial District commuter mobility findings."
        ),
        tools=[identify_peak_window],
        output_key="specialist_output",
    ).agent

    queens_specialist = WorkerAgent(
        name="QueensZoneSpecialist",
        instruction=(
            f"{instruction}\n\n"
            "You are the Queens Corridor Specialist. Call `identify_peak_window(zone_id='ZONE_QUEENS_CORRIDOR')` "
            "and present the Queens Corridor commuter mobility findings."
        ),
        tools=[identify_peak_window],
        output_key="specialist_output",
    ).agent

    sequential_workflow = build_sequential_agent(instruction=instruction)
    parallel_workflow = build_parallel_agent(instruction=instruction)
    loop_workflow = build_loop_agent(instruction=instruction)

    def route_by_intent(ctx: InvocationContext, node_input: Any) -> Event:
        """Selects the downstream branch based on the router agent's resolved route."""
        text = str(node_input).lower()
        for route_key in (
            "midtown_specialist",
            "downtown_financial_specialist",
            "queens_specialist",
            "parallel_multi_zone",
            "loop_quality_calibration",
        ):
            if route_key in text:
                return Event(output=node_input, route=route_key)
        return Event(output=node_input, route="sequential_pipeline")

    return Workflow(
        name="mta_custom_dynamic_router",
        description="Dynamically routes commuter queries to target zone specialists or workflow suites via ADK Workflow.",
        edges=[
            (START, intent_router),
            (intent_router, route_by_intent),
            (
                route_by_intent,
                {
                    "midtown_specialist": midtown_specialist,
                    "downtown_financial_specialist": downtown_specialist,
                    "queens_specialist": queens_specialist,
                    "parallel_multi_zone": parallel_workflow,
                    "loop_quality_calibration": loop_workflow,
                    "sequential_pipeline": sequential_workflow,
                },
            ),
        ],
    )
