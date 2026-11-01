"""
Parallel Workflow Orchestration for Multi-Zone Commuter Analytics.

Demonstrates how to orchestrate concurrent regional `WorkerAgent` specialists
in parallel using Google ADK's `Workflow` and `JoinNode` fan-in:
  - MidtownZoneAnalyst (Midtown Commercial Core)
  - QueensZoneAnalyst (Long Island City / Queens Corridor)
  - DowntownFinancialZoneAnalyst (Financial District / Wall Street)
Followed by CrossZoneGeoSynthesizer to produce a citywide comparative mobility scorecard.
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from google.adk.workflow import Workflow, START, JoinNode  # noqa: E402
from worker_agent import WorkerAgent  # noqa: E402
from workflow_agent.geo_tools import (  # noqa: E402
    identify_peak_window,
    synthesize_cross_zone_metrics,
)


def build_parallel_agent(
    instruction: str = "",
    **kwargs,
) -> Workflow:
    """
    Builds the ADK Workflow graph representing parallel multi-zone processing
    using WorkerAgent abstractions and JoinNode fan-in.

    Args:
        instruction: Cryptographically verified system instruction text.
        **kwargs: Optional configuration parameters.

    Returns:
        google.adk.workflow.Workflow instance.
    """
    midtown_analyst = WorkerAgent(
        name="MidtownZoneAnalyst",
        instruction=(
            f"{instruction}\n\n"
            "You are the Midtown Zone Analyst in a parallel workflow suite. "
            "Call `identify_peak_window(zone_id='ZONE_MIDTOWN_COMMERCIAL')` to evaluate "
            "Midtown peak windows and Net Directional Ratio in BigQuery. "
            "Report the commuter flow and profile for Midtown exclusively."
        ),
        tools=[identify_peak_window],
        output_key="midtown_metrics_text",
    ).agent

    queens_analyst = WorkerAgent(
        name="QueensZoneAnalyst",
        instruction=(
            f"{instruction}\n\n"
            "You are the Queens Zone Analyst in a parallel workflow suite. "
            "Call `identify_peak_window(zone_id='ZONE_QUEENS_CORRIDOR')` to evaluate "
            "Queens Corridor peak windows and Net Directional Ratio in BigQuery. "
            "Report the commuter flow and profile for Queens exclusively."
        ),
        tools=[identify_peak_window],
        output_key="queens_metrics_text",
    ).agent

    downtown_analyst = WorkerAgent(
        name="DowntownFinancialZoneAnalyst",
        instruction=(
            f"{instruction}\n\n"
            "You are the Downtown Financial Zone Analyst in a parallel workflow suite. "
            "Call `identify_peak_window(zone_id='ZONE_DOWNTOWN_FINANCIAL')` to evaluate "
            "Financial District peak windows and Net Directional Ratio in BigQuery. "
            "Report the commuter flow and profile for Downtown exclusively."
        ),
        tools=[identify_peak_window],
        output_key="financial_metrics_text",
    ).agent

    merger_agent = WorkerAgent(
        name="CrossZoneGeoSynthesizer",
        instruction=(
            f"{instruction}\n\n"
            "You are the Cross-Zone Synthesizer. Call `synthesize_cross_zone_metrics()` "
            "to execute the cross-zone ranking query in BigQuery and combine the parallel "
            "regional findings into a comparative citywide mobility scorecard."
        ),
        tools=[synthesize_cross_zone_metrics],
        output_key="citywide_scorecard_text",
    ).agent

    join_node = JoinNode(name="merge_zones")

    return Workflow(
        name="mta_parallel_workflow_suite",
        description="Coordinates parallel zone analysis followed by cross-zone mobility synthesis via ADK Workflow.",
        edges=[
            (START, (midtown_analyst, queens_analyst, downtown_analyst)),
            ((midtown_analyst, queens_analyst, downtown_analyst), join_node),
            (join_node, merger_agent),
        ],
    )
