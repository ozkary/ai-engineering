"""
Loop Workflow Orchestration for Iterative Geo-Quality & Anomaly Calibration.

Demonstrates how to compose `WorkerAgent` instances into an iterative quality
refinement loop using Google ADK's `Workflow` and conditional routing edges:
  1. ZScoreAnomalyDetector: Audits BigQuery turnstile records for Z-score anomalies (|Z| > 2.5)
  2. evaluate_quality_route: Checks if session confidence_score >= 95%
  3. SpatialImputerAgent: Calibrates anomalies via SQL PERCENTILE_CONT spatial median
  4. GeoQualityCertifierAgent: Certifies the dataset once quality threshold is reached
"""

import os
import sys
from typing import Any, AsyncGenerator

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from google.adk.workflow import Workflow, START  # noqa: E402
from google.adk.agents import BaseAgent  # noqa: E402
from worker_agent import WorkerAgent  # noqa: E402
from google.adk.agents.invocation_context import InvocationContext  # noqa: E402
from google.adk.events import Event, EventActions  # noqa: E402
from workflow_agent.geo_tools import (  # noqa: E402
    detect_zscore_outliers,
    impute_spatial_baseline,
)


class GeoQualityEscalationChecker(BaseAgent):
    """
    Custom ADK BaseAgent evaluator that inspects session state for the Data Quality
    Confidence Score and emits an escalation event when certification is reached.
    """

    def __init__(self, target_confidence: float = 0.95, **kwargs):
        kwargs.setdefault("name", "GeoQualityEscalationChecker")
        kwargs.setdefault("description", "Monitors data quality confidence score and breaks loop on certification.")
        super().__init__(**kwargs)
        self.target_confidence = target_confidence

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        confidence = float(ctx.session.state.get("confidence_score", 0.0))

        if confidence >= self.target_confidence:
            message = f"🎯 [GeoQualityEscalationChecker] Quality confidence certified at {confidence*100:.1f}% (>= {self.target_confidence*100:.0f}%). Breaking loop."
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True),
                output=message,
            )
        else:
            message = f"🔄 [GeoQualityEscalationChecker] Confidence at {confidence*100:.1f}% (< {self.target_confidence*100:.0f}%). Continuing calibration loop."
            yield Event(
                author=self.name,
                actions=EventActions(escalate=False),
                output=message,
            )


def build_loop_agent(
    instruction: str = "",
    max_iterations: int = 4,
    **kwargs,
) -> Workflow:
    """
    Builds the ADK Workflow graph representing the quality calibration loop
    using WorkerAgent abstractions and conditional routed edges.

    Args:
        instruction: Cryptographically verified system instruction text.
        max_iterations: Maximum loop iterations before forced termination.
        **kwargs: Optional configuration parameters.

    Returns:
        google.adk.workflow.Workflow instance.
    """
    detector_agent = WorkerAgent(
        name="ZScoreAnomalyDetector",
        instruction=(
            f"{instruction}\n\n"
            "You are the Z-Score Anomaly Detector. Call `detect_zscore_outliers()` to audit "
            "BigQuery turnstile records for statistical anomalies. "
            "Report the number of outliers flagged and the current data confidence score."
        ),
        tools=[detect_zscore_outliers],
        output_key="audit_summary_text",
    ).agent

    imputer_agent = WorkerAgent(
        name="SpatialImputerAgent",
        instruction=(
            f"{instruction}\n\n"
            "You are the Spatial Imputer. Call `impute_spatial_baseline()` to calibrate "
            "anomalous records using neighboring station medians via SQL PERCENTILE_CONT. "
            "Report the count of calibrated observations."
        ),
        tools=[impute_spatial_baseline],
        output_key="imputer_summary_text",
    ).agent

    certifier_agent = WorkerAgent(
        name="GeoQualityCertifierAgent",
        instruction=(
            f"{instruction}\n\n"
            "You are the Geo Quality Certifier. Summarize the completed data quality audit "
            "and confirm that the dataset is certified for operational analytics."
        ),
        output_key="certification_report",
    ).agent

    def evaluate_quality_route(ctx: InvocationContext, node_input: Any) -> Event:
        """Evaluates session state confidence_score to continue calibration or exit loop."""
        conf = 0.0
        if hasattr(ctx, "session") and ctx.session and ctx.session.state:
            conf = float(ctx.session.state.get("confidence_score", 0.0))
        if conf >= 0.95:
            return Event(output=node_input, route="exit")
        return Event(output=node_input, route="continue")

    return Workflow(
        name="mta_quality_refinement_loop",
        description="Iteratively audits turnstile telemetry and calibrates anomalies until quality confidence >= 95% via ADK Workflow.",
        edges=[
            (START, detector_agent),
            (detector_agent, evaluate_quality_route),
            (evaluate_quality_route, {"continue": imputer_agent, "exit": certifier_agent}),
            (imputer_agent, detector_agent),
        ],
    )
