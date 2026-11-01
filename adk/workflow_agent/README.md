# Google ADK Workflow Agents: NYC Transit Geo-Zone Intelligence

Welcome to the **Workflow Agent Suite** for Google ADK (Agent Development Kit). This guide explains how to build specialized [`WorkerAgent`](../worker_agent/agent.py) sub-agents and orchestrate them using Google ADK's `Workflow` graph across four core multi-agent orchestration patterns:

1. **Sequential Workflow** (`workflows/sequential.py`)
2. **Parallel Workflow** (`workflows/parallel.py`)
3. **Loop Workflow** (`workflows/loop.py`)
4. **Custom Dynamic Router Workflow** (`workflows/custom.py`)

This implementation is grounded in the NYC Transit turnstile architecture and concepts from the book:
👉 **[data-engineering-mta-turnstile](https://github.com/ozkary/data-engineering-mta-turnstile)**

---

## 🧭 Architectural Blueprint: Inheritance, Security & SQL-First Design

The workflow suite separates **Orchestration (`WorkflowAgent` & `WorkerAgent`)**, **Semantic Domain Rules (`SKILL.md`)**, **Domain SQL Tools (`geo_tools.py`)**, and **Warehouse Execution (`commands/bq/`)**:

```
                     BaseAgent (core/base_agent.py)
                      │                      │
          ┌───────────┴───────────┐          │
          ▼                       ▼          ▼
     BasicAgent               WorkerAgent (worker_agent/agent.py)
          │                   (Abstracts LLM model, encapsulates sub-agent
          ▼                    name, instructions, SQL tools, output_key)
     ToolAgent
          │
          ▼
     SecuredToolAgent (enforces HMAC-SHA256 prompt signatures)
          │
          ▼
     WorkflowAgent (resolves strategy via WorkflowFactory & builds ADK Workflow graph)
```

### 1. The `WorkerAgent` Abstraction (`worker_agent/agent.py`)
Instead of coupling workflow definitions directly to low-level framework primitives (`google.adk.Agent`), every sub-agent in a workflow is instantiated via `WorkerAgent`:
- **Central Model Resolution**: Callers do not hardcode `model=...`; the model is inherited from `BaseAgent` via the `LLM_MODEL` environment variable.
- **Declarative Configuration**: Each worker is defined with `name`, `instruction`, `tools`, and `output_key`:
  ```python
  from worker_agent import WorkerAgent

  ingestion_agent = WorkerAgent(
      name="IngestionAgent",
      instruction="Identify the target zone and call query_zone_commuters.",
      tools=[query_zone_commuters],
      output_key="raw_telemetry",
  ).agent
  ```
- **Graph Composition**: Calling `.agent` returns the compiled ADK agent primitive ready to be wired into `Workflow(edges=[...])`.

### 2. Three-Tier SQL-First Separation of Concerns (The "Looker" Pattern)

```
┌───────────────────────────────────────────┐
│ 1. Domain Skill (skills/geo_fencing/)     │  Semantic layer: Geo-zone station mappings,
│    SKILL.md                               │  time-slot boundaries, NDR & Z-score rules.
└─────────────────────┬─────────────────────┘
                      ▼
┌───────────────────────────────────────────┐
│ 2. Domain SQL Tools (geo_tools.py)        │  Builds parameterized analytical SQL queries
│    query_zone_commuters,                  │  (GROUP BY, FIRST_VALUE, STDDEV OVER,
│    identify_peak_window, etc.             │  PERCENTILE_CONT) from Skill metadata.
└─────────────────────┬─────────────────────┘
                      ▼
┌───────────────────────────────────────────┐
│ 3. BigQuery Conduit (commands/bq/)        │  Domain-agnostic WarehouseQueryStrategy:
│    BigQueryGeoAggregateStrategy           │  Executes SQL via BigQueryToolset and
│                                           │  renders structured report containers.
└───────────────────────────────────────────┘
```

---

## 🏙️ NYC Transit Geo-Fencing Domain Semantics

Defined in [`skills/geo_fencing/SKILL.md`](../skills/geo_fencing/SKILL.md):

1. **Directional Flow Semantics**:
   - `exits` = **Arrivals** into the geo-zone / neighborhood.
   - `entries` = **Departures** from the geo-zone into the transit network.
2. **Canonical Time Slots**:
   - `morning_rush`: `08:00 – 11:00` (peak arrivals in commercial hubs).
   - `afternoon_midday`: `12:00 – 15:00` (midday business & retail traffic).
   - `evening_rush`: `16:00 – 20:00` (peak departures from commercial hubs).
3. **Net Directional Ratio ($NDR$)**:
   $$\text{NDR} = \frac{\text{Morning Arrivals (Exits)}}{\text{Morning Departures (Entries)}}$$
   - $\text{NDR} > 1.5$: Commercial / Employment Destination (Inflow Heavy).
   - $\text{NDR} < 0.7$: Residential Feeder Corridor (Outflow Heavy).
   - $0.7 \le \text{NDR} \le 1.5$: Balanced Mixed-Use / Intermodal Transfer Hub.

---

## 🔄 Guide to the 4 Workflow Orchestration Patterns

### 1. Sequential Workflow (`workflows/sequential.py`)
* **When to use**: Multi-stage pipelines where each `WorkerAgent` builds on the session state produced by the previous agent.
* **Graph Topology (`mta_sequential_geo_pipeline`)**:
  ```
  START ──> IngestionAgent ──> TimeSlotAggregatorAgent ──> PeakWindowAnalyzerAgent ──> GeoBriefingReporterAgent
  ```
* **Workers & Tools**:
  1. `IngestionAgent` $\rightarrow$ `query_zone_commuters`: Queries station-level observations in BigQuery and saves `telemetry_data` & `zone_id` to session state.
  2. `TimeSlotAggregatorAgent` $\rightarrow$ `calculate_time_slots`: Runs SQL `GROUP BY time_slot` aggregation and saves `slotted_data` to state.
  3. `PeakWindowAnalyzerAgent` $\rightarrow$ `identify_peak_window`: Runs SQL window functions (`FIRST_VALUE`, `SAFE_DIVIDE`) to compute peak windows, NDR, and mobility profile.
  4. `GeoBriefingReporterAgent` $\rightarrow$ `generate_geo_brief`: Renders the executive operational mobility bulletin via `BigQueryGeoAggregateStrategy.render_report`.

### 2. Parallel Workflow (`workflows/parallel.py`)
* **When to use**: Independent regional or domain analyses that can run concurrently without blocking each other, followed by a fan-in synthesis step.
* **Graph Topology (`mta_parallel_workflow_suite`)**:
  ```
          ┌──> MidtownZoneAnalyst ───────────┐
  START ──┼──> QueensZoneAnalyst ────────────┼──> JoinNode("merge_zones") ──> CrossZoneGeoSynthesizer
          └──> DowntownFinancialZoneAnalyst ─┘
  ```
* **Workers & Tools**:
  - `MidtownZoneAnalyst`, `QueensZoneAnalyst`, and `DowntownFinancialZoneAnalyst` concurrently call `identify_peak_window` for their respective geo-zones.
  - `JoinNode(name="merge_zones")` synchronizes completion of all parallel branches.
  - `CrossZoneGeoSynthesizer` calls `synthesize_cross_zone_metrics` to rank all zones by total commuter flow in BigQuery.

### 3. Loop Workflow (`workflows/loop.py`)
* **When to use**: Iterative data quality auditing and calibration cycles that repeat until a statistical confidence threshold is met.
* **Graph Topology (`mta_quality_refinement_loop`)**:
  ```
  START ──> ZScoreAnomalyDetector ──> evaluate_quality_route ──(exit: confidence >= 0.95)──> GeoQualityCertifierAgent
                     ▲                          │
                     └─── SpatialImputerAgent <─┴──(continue: confidence < 0.95)
  ```
* **Workers & Tools**:
  1. `ZScoreAnomalyDetector` $\rightarrow$ `detect_zscore_outliers`: Computes SQL window Z-scores (`AVG() OVER`, `STDDEV() OVER`) to flag anomalies ($|Z| > 2.5$) and updates `confidence_score` in session state.
  2. `evaluate_quality_route`: Inspects `ctx.session.state["confidence_score"]`. Routes to `"exit"` when $\ge 0.95$, or `"continue"` otherwise.
  3. `SpatialImputerAgent` $\rightarrow$ `impute_spatial_baseline`: Imputes anomalous counts in SQL using `PERCENTILE_CONT(arrival_count, 0.5) OVER (PARTITION BY time_slot)` and loops back to the detector.
  4. `GeoQualityCertifierAgent`: Issues the final data quality certification summary.

### 4. Custom Dynamic Router Workflow (`workflows/custom.py`)
* **When to use**: Context-aware orchestration where an initial router agent classifies user intent and dynamically branches to either a single specialist agent or an entire sub-workflow (`sequential`, `parallel`, or `loop`).
* **Graph Topology (`mta_custom_dynamic_router`)**:
  ```
                                                      ┌──> MidtownZoneSpecialist
                                                      ├──> DowntownFinancialSpecialist
  START ──> GeoZoneDynamicRouter ──> route_by_intent ─┼──> QueensZoneSpecialist
                                                      ├──> mta_parallel_workflow_suite
                                                      ├──> mta_quality_refinement_loop
                                                      └──> mta_sequential_geo_pipeline
  ```

---

## ⚙️ Configuration & Environment Setup

The `WorkflowFactory` (`factory.py`) resolves the active workflow strategy from `WORKFLOW_TYPE` (`sequential`, `parallel`, `loop`, `custom`) and loads the corresponding cryptographically signed prompt file via uppercase environment variable keys:

```ini
# workflow_agent/.env
GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
GOOGLE_CLOUD_PROJECT="ozkary-de-101"
GOOGLE_GENAI_USE_VERTEXAI="1"
GOOGLE_CLOUD_LOCATION="us-east1"
LLM_MODEL="gemini-2.5-flash"
AGENT_NAME="workflow_agent"

# Strategy Prompt Mappings (each paired with a .signed.md HMAC signature)
SEQUENTIAL="prompts/sequential_workflow_instructions.md"
PARALLEL="prompts/parallel_workflow_instructions.md"
LOOP="prompts/loop_workflow_instructions.md"
CUSTOM="prompts/custom_workflow_instructions.md"
```

---

## 🚀 How to Run and Use the Workflow Agents

### 1. Run via Google ADK CLI (`uv run adk run`)

By default, `WORKFLOW_TYPE` defaults to `sequential`. Set `WORKFLOW_TYPE` to switch between the four orchestration graphs:

```bash
# 1. Sequential Pipeline (Default)
uv run adk run workflow_agent "Analyze peak commuter flow for Midtown Manhattan"

# 2. Parallel Regional Analytics Suite
WORKFLOW_TYPE=parallel uv run adk run workflow_agent "Analyze all zones in parallel"

# 3. Iterative Z-Score Calibration Loop
WORKFLOW_TYPE=loop uv run adk run workflow_agent "Calibrate turnstile telemetry data for Midtown"

# 4. Custom Dynamic Router
WORKFLOW_TYPE=custom uv run adk run workflow_agent "Compare commuter surges across all New York zones"
```

### 2. Inspect Visually in the ADK Web Playground (`uv run adk web`)

Launch the interactive ADK web UI to inspect the `Workflow` graph nodes, `WorkerAgent` tool calls, and session state transitions in real time:

```bash
# Launch with default workflow (sequential) or specify WORKFLOW_TYPE
WORKFLOW_TYPE=sequential uv run adk web workflow_agent/
```
Open `http://localhost:8000` in your browser to interact with the workflow graph.

### 3. Instantiate Programmatically in Python

You can instantiate any workflow graph via `WorkflowAgent` or `WorkflowFactory`:

```python
from workflow_agent import WorkflowAgent, WorkflowFactory

# Option A: Via WorkflowAgent (verifies prompt signature & compiles active_workflow)
agent_wrapper = WorkflowAgent(workflow_type="parallel")
workflow_graph = agent_wrapper.active_workflow

# Option B: Directly via WorkflowFactory
loop_graph = WorkflowFactory.create_workflow("loop")
```
