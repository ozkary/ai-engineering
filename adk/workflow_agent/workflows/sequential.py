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
            "You are the Ingestion Agent in a multi-stage sequential pipeline. "
            "Identify the target geographic zone from the user request (defaulting to 'ZONE_MIDTOWN_COMMERCIAL') "
            "and call `query_zone_commuters(zone_id=...)` to retrieve BigQuery turnstile observations. "
            "Summarize the stations and records retrieved."
        ),
        tools=[query_zone_commuters],
        output_key="raw_telemetry",
    ).agent

    aggregation_agent = WorkerAgent(
        name="TimeSlotAggregatorAgent",
        instruction=(
            f"{instruction}\n\n"
            "You are the Time Slot Aggregator. Call `calculate_time_slots()` to aggregate "
            "the zone's commuter observations into canonical time slots in BigQuery. "
            "Summarize the arrival and departure counts across morning, afternoon, and evening slots."
        ),
        tools=[calculate_time_slots],
        output_key="slotted_telemetry",
    ).agent

    peak_agent = WorkerAgent(
        name="PeakWindowAnalyzerAgent",
        instruction=(
            f"{instruction}\n\n"
            "You are the Peak Window Analyzer. Call `identify_peak_window()` to compute "
            "peak arrival/departure windows and the Net Directional Ratio (NDR) in BigQuery. "
            "Interpret the NDR and state the zone's mobility profile."
        ),
        tools=[identify_peak_window],
        output_key="peak_summary_text",
    ).agent

    reporter_agent = WorkerAgent(
        name="GeoBriefingReporterAgent",
        instruction=(
            f"{instruction}\n\n"
            "You are the Geo Briefing Reporter. Call `generate_geo_brief()` to render "
            "the executive operational mobility bulletin from the session metrics, and present "
            "the complete bulletin along with your operational insights."
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
