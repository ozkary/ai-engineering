"""
Sequential Workflow Orchestration for Geo-Zone Commuter Analytics.

Demonstrates how to compose specialized `WorkerAgent` instances into a strict serial
pipeline using Google ADK's `Workflow` graph:
  1. IngestionAgent: Queries BigQuery for station-level turnstile observations
  2. TimeSlotAggregatorAgent: Aggregates observations into morning/afternoon/evening slots
  3. PeakWindowAnalyzerAgent: Computes peak windows, Net Directional Ratio (NDR), and profile
  4. GeoBriefingReporterAgent: Renders the executive operational mobility bulletin
"""

import os
import sys
from google.adk.workflow import Workflow, START
from worker_agent import WorkerAgent
from workflow_agent.geo_tools import (
    query_zone_commuters,
    calculate_time_slots,
    identify_peak_window,
    generate_geo_brief,
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)


def build_sequential_agent(
    instruction: str = "",
    **kwargs,
) -> Workflow:
    """
    Builds the ADK Workflow graph representing the sequential pipeline
    using WorkerAgent abstractions.

    Args:
        instruction: Cryptographically verified system instruction text.
        **kwargs: Optional configuration parameters.

    Returns:
        google.adk.workflow.Workflow instance.
    """
    ingestion_agent = WorkerAgent(
        name="IngestionAgent",
        instruction=(
            f"{instruction}\n\n"
            "## YOUR EXCLUSIVE ROLE: STEP 1 ONLY (IngestionAgent)\n"
            "You ONLY execute Step 1. Your ONLY available tool is `query_zone_commuters`.\n"
            "Identify the target geographic zone from the user request (e.g. 'ZONE_MIDTOWN_COMMERCIAL', "
            "'ZONE_DOWNTOWN_FINANCIAL', 'ZONE_QUEENS_CORRIDOR', 'ZONE_MIDTOWN_SOUTH_HUB') and call "
            "`query_zone_commuters(zone_id=...)` once. "
            "After calling `query_zone_commuters`, summarize the stations and records retrieved and finish your turn. "
            "Do NOT attempt to call `calculate_time_slots`, `identify_peak_window`, or `generate_geo_brief`—downstream agents will execute Steps 2, 3, and 4."
        ),
        tools=[query_zone_commuters],
        output_key="raw_telemetry",
    ).agent

    aggregation_agent = WorkerAgent(
        name="TimeSlotAggregatorAgent",
        instruction=(
            f"{instruction}\n\n"
            "## YOUR EXCLUSIVE ROLE: STEP 2 ONLY (TimeSlotAggregatorAgent)\n"
            "You ONLY execute Step 2. Your ONLY available tool is `calculate_time_slots`.\n"
            "Call `calculate_time_slots()` once to aggregate the zone's commuter observations into canonical time slots in BigQuery. "
            "After calling `calculate_time_slots`, summarize the arrival and departure counts across morning, afternoon, and evening slots and finish your turn. "
            "Do NOT attempt to call `identify_peak_window` or `generate_geo_brief`."
        ),
        tools=[calculate_time_slots],
        output_key="slotted_telemetry",
    ).agent

    peak_agent = WorkerAgent(
        name="PeakWindowAnalyzerAgent",
        instruction=(
            f"{instruction}\n\n"
            "## YOUR EXCLUSIVE ROLE: STEP 3 ONLY (PeakWindowAnalyzerAgent)\n"
            "You ONLY execute Step 3. Your ONLY available tool is `identify_peak_window`.\n"
            "Call `identify_peak_window()` once to compute peak arrival/departure windows and the Net Directional Ratio (NDR) in BigQuery. "
            "After calling `identify_peak_window`, interpret the NDR, state the zone's mobility profile, and finish your turn. "
            "Do NOT attempt to call `generate_geo_brief`."
        ),
        tools=[identify_peak_window],
        output_key="peak_summary_text",
    ).agent

    reporter_agent = WorkerAgent(
        name="GeoBriefingReporterAgent",
        instruction=(
            f"{instruction}\n\n"
            "## YOUR EXCLUSIVE ROLE: STEP 4 ONLY (GeoBriefingReporterAgent)\n"
            "You ONLY execute Step 4. Your ONLY available tool is `generate_geo_brief`.\n"
            "Call `generate_geo_brief()` once to render the executive operational mobility bulletin from the session metrics, "
            "and present the complete bulletin along with your operational insights."
        ),
        tools=[generate_geo_brief],
        output_key="final_bulletin",
    ).agent

    return Workflow(
        name="mta_sequential_geo_pipeline",
        description="Executes serial data operations from BigQuery turnstile telemetry to executive geo-zone mobility reports via ADK Workflow.",
        edges=[
            (START, ingestion_agent),
            (ingestion_agent, aggregation_agent),
            (aggregation_agent, peak_agent),
            (peak_agent, reporter_agent),
        ],
    )
