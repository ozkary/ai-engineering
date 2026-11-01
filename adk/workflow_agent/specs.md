# Workflow Agents Specification & Implementation Plan

You are working exclusively within the `adk/workflow_agent` directory. This project implements a comprehensive, educational, production-grade demonstration of the four core Google ADK (Agent Development Kit) workflow agent patterns:

1. **Sequential Workflow** (`SequentialAgent`)
2. **Parallel Workflow** (`ParallelAgent`)
3. **Loop Workflow** (`LoopAgent`)
4. **Custom Workflow** (`BaseAgent` subclass with dynamic algorithmic routing)

---

## 1. Grounding Domain Concepts (Ozkary MTA Turnstile Transit Intelligence)

The workflows are grounded directly in the concepts and architecture from the book and reference repository:
👉 [https://github.com/ozkary/data-engineering-mta-turnstile](https://github.com/ozkary/data-engineering-mta-turnstile)

### Key Analytical Principles
- **No File Ingestion Needed**: We do not parse raw CSV files. The data is stored in BigQuery (`mta_dev.fact_turnstile`, `mta_dev.dim_station`, `mta_dev.dim_booth`). Agents query BigQuery directly using the native ADK BigQuery toolset (`execute_sql`).
- **Station as Geo-Anchor**: `station_name` provides the spatial reference point linked to `dim_station`.
- **Geo-Fencing & Geo-Zoning**: Stations are grouped into geographic zones / geo-fences (e.g. `Zone 1: Midtown Commercial`, `Zone 2: Downtown Financial`, `Zone 3: Queens / Vernon-Jackson`, `Zone 4: Transit Hubs`) to analyze localized commuter volume.
- **Commuter Flow Semantics**:
  - `exits` = **Arrivals** (passengers exiting the station into the local geo-zone / neighborhood).
  - `entries` = **Departures** (passengers entering the transit network from the geo-zone).
- **Standard Time Slots**:
  - Morning Rush: `08:00 – 11:00` (peak arrivals in commercial hubs).
  - Midday / Afternoon: `12:00 – 15:00` (lunch and retail traffic).
  - Night / Evening Rush: `16:00 – 20:00` (peak departures from commercial hubs).
- **Statistical Outlier Detection (Z-Score)**:
  - $Z = \frac{x - \mu}{\sigma}$ calculated per station/zone to detect abnormal surges or sensor glitches.
- **Target Business / Operational Goal**:
  - Identify peak commuter foot-traffic windows tied to geographic location to optimize operations, staffing, and location-based promotions.

---

## 2. Architecture & Inheritance Model

```
                    BaseAgent (core/base_agent.py)
                     │                      │
         ┌───────────┴───────────┐          │
         ▼                       ▼          ▼
    BasicAgent               WorkerAgent (worker_agent/agent.py)
         │                   (Abstracts LLM model, encapsulates subagent
         ▼                    name, instructions, tools, output_key)
    ToolAgent
         │
         ▼
    SecuredToolAgent (enforces HMAC-SHA256 signatures)
         │
         ▼
    WorkflowAgent (orchestrates subagents created via WorkerAgent)
```

### The `WorkerAgent` Abstraction (`worker_agent/agent.py`)
To prevent coupling workflow sub-agents directly to framework primitives (`google.adk.Agent`), all workflow workers derive from `WorkerAgent`:
- **Model Abstraction**: Callers do NOT pass `model=...`. The model is resolved centrally by `BaseAgent` from environment variables (`LLM_MODEL`).
- **Clean Configuration**: Instantiated cleanly with `name`, `instruction` (or `instructions`), `tools`, and `output_key`.
- **Exposes `.agent`**: Provides the compiled concrete framework primitive ready for composition in `SequentialAgent`, `ParallelAgent`, or `LoopAgent`.

### Why Inherit from `SecuredToolAgent`?

- **Cryptographic Prompt Protection**: Every system instruction file (`.md`) is paired with an HMAC/SHA-256 signature file (`.signed.md`). `SecuredToolAgent.load_prompt_asset()` automatically verifies authenticity and integrity at startup.
- **Integrated Toolsets**: Inherits native BigQuery query execution tools without boilerplate.
- **Session Continuity**: Integrates seamlessly with `AgentRunner` and the persistent SQLite database.

---

## 3. Code & Function Design Standards

To ensure software engineering rigor and maintainability:

1. **Modular Concepts**: Each workflow pattern is isolated in its own dedicated module under `workflow_agent/workflows/`.
2. **Atomic Action Functions**: Every analytical action or task is encapsulated in its own discrete Python function (e.g., `query_zone_commuter_data`, `calculate_peak_time_slots`, `detect_zscore_outliers`, `impute_spatial_baseline`).
3. **Comprehensive Docstrings**: Every module, class, and function includes clear Google/NumPy-style docstrings describing parameters, return values, and exceptions.
4. **Standardized Return Contract**: Every function and tool returns a structured dictionary:
   ```python
   {
       "status": True,             # Boolean flag: True on success, False on error
       "message": "Description",   # Human-readable status or diagnostic message
       "data": { ... }             # Optional payload dictionary
   }
   ```
5. **Agent Control Flow & Error Handling**:
   - The agent instructions explicitly command: **"Continue when status is True. Stop immediately and report the error when status is False or when an exception occurs."**
   - All tools implement structured `try...except` blocks that catch exceptions and return `{"status": False, "message": str(e), "data": None}`.
6. **Dedicated Prompt per Workflow**: Each workflow has its own dedicated system instruction prompt asset:
   - `prompts/sequential_workflow_instructions.md` & `.signed.md`
   - `prompts/parallel_workflow_instructions.md` & `.signed.md`
   - `prompts/loop_workflow_instructions.md` & `.signed.md`
   - `prompts/custom_workflow_instructions.md` & `.signed.md`
   Each prompt details:
   - The available tools.
   - The step execution sequence.
   - Strict error handling instructions.

---

## 4. The 4 Workflow Specifications

### A. Sequential Workflow (`SequentialAgent`)
- **Focus**: End-to-End Geo-Zone Commuter Peak Detection Pipeline.
- **Step Sequence**:
  1. `QueryZoneDataTask`: Queries BigQuery (`mta_dev.fact_turnstile` joined with `dim_station`) for target geo-zone stations across date ranges.
  2. `ComputeTimeSlotMetricsTask`: Aggregates arrivals (`exits`) and departures (`entries`) into the standard time slots (`08:00–11:00`, `12:00–15:00`, `16:00–20:00`).
  3. `IdentifyPeakWindowTask`: Determines the peak arrival hour (morning) and departure hour (evening) and computes the zone's Net Directional Ratio ($Arrivals / Departures$).
  4. `GenerateGeoZoneBriefTask`: Emits an executive operational summary.
- **Stop/Continue Rule**: If any query or aggregation fails (`status == False`), pipeline execution stops immediately.

### B. Parallel Workflow (`ParallelAgent`)
- **Focus**: Concurrent Multi-Zone Foot-Traffic Analysis.
- **Step Sequence**:
  - Spawns concurrent regional analysts:
    - `MidtownZoneAnalyst`: Queries & analyzes Midtown Commercial Zone (`59 ST`, `34 ST-HERALD SQ`).
    - `QueensZoneAnalyst`: Queries & analyzes Queens Commercial-Residential Corridor (`VERNON-JACKSON`).
    - `DowntownFinancialZoneAnalyst`: Queries & analyzes Financial District (`FULTON ST`).
  - `CrossZoneGeoSynthesizer`: Receives all parallel worker outputs, ranks geo-zones by foot traffic density, and identifies contrasting peak dynamics across neighborhoods.

### C. Loop Workflow (`LoopAgent`)
- **Focus**: Iterative Z-Score Statistical Outlier Detection & Spatial Calibration.
- **Step Sequence**:
  1. `ZScoreAuditTask`: Queries station metrics and computes Z-scores: $Z = \frac{x - \mu}{\sigma}$. Flags records with $|Z| > 2.5$.
  2. `SpatialImputationTask`: Calibrates outlier records using the median rate of neighboring stations within the same geo-zone.
  3. `GeoQualityEscalationChecker`: Custom `BaseAgent` evaluating Data Confidence Score. If confidence $\ge 95\%$ (or 0 critical outliers remain), emits `Event(actions=EventActions(escalate=True))` to break out of the loop and certify the dataset.
- **Safeguard**: Bound by `max_iterations=4`.

### D. Custom Workflow (Dynamic Router `BaseAgent`)
- **Focus**: Context-Aware Geo-Zone Query & Granularity Router.
- **Step Sequence**:
  - Custom `BaseAgent` subclass implementing `_run_async_impl(ctx)`:
    - Parses user intent from the prompt.
    - If user asks for a *specific zone* $\rightarrow$ routes to that Zone Analyst.
    - If user asks for *multi-zone comparison* $\rightarrow$ executes `ParallelAgent`.
    - If user asks for *full pipeline* $\rightarrow$ executes `SequentialAgent`.
    - If user asks for *sensor calibration / outlier cleanup* $\rightarrow$ executes `LoopAgent`.

---

## 5. File Layout (`adk/workflow_agent/`)

```
adk/workflow_agent/
├── specs.md                             # This document
├── README.md                            # Comprehensive pedagogical guide
├── .env                                 # Environment configuration
├── __init__.py                          # Package exports
├── agent.py                             # WorkflowAgent class inheriting from SecuredToolAgent
├── geo_tools.py                         # Atomic data operation functions with structured return
├── demo.py                              # Interactive CLI runner
├── prompts/
│   ├── sequential_workflow_instructions.md        # Sequential pipeline prompt
│   ├── sequential_workflow_instructions.signed.md # SHA-256 / HMAC signature
│   ├── parallel_workflow_instructions.md          # Parallel multi-zone prompt
│   ├── parallel_workflow_instructions.signed.md   # SHA-256 / HMAC signature
│   ├── loop_workflow_instructions.md              # Loop quality calibration prompt
│   ├── loop_workflow_instructions.signed.md       # SHA-256 / HMAC signature
│   ├── custom_workflow_instructions.md            # Custom dynamic router prompt
│   └── custom_workflow_instructions.signed.md     # SHA-256 / HMAC signature
└── workflows/
    ├── __init__.py                      # Package exports
    ├── sequential.py                    # SequentialAgent builder & functions
    ├── parallel.py                      # ParallelAgent builder & functions
    ├── loop.py                          # LoopAgent builder with EscalationChecker
    └── custom.py                        # Custom dynamic router BaseAgent
```

---

## 6. Deterministic Workflow Execution Guide

This architecture provides **three distinct tiers of deterministic execution**:
1. **CLI Flag Runner (`demo.py`)**: Dedicated command-line execution for testing and verifying each pattern in isolation or all together.
2. **ADK CLI Execution (`uv run adk run`)**: Official ADK agentic runtime execution selecting specific workflow graphs via `WORKFLOW_TYPE`.
3. **Programmatic Python API (`execute_*_pipeline`)**: Direct code execution for backend services and automated unit test pipelines with zero LLM drift.

---

### Tier 1: CLI Deterministic Execution (`demo.py`)

Execute individual workflows or the complete suite with full step-by-step trajectory logging:

```bash
# 1. Run all 4 workflows sequentially in one pass
python demo.py --workflow all

# 2. Run ONLY the Sequential Pipeline (Ingestion -> Slots -> Peak -> Bulletin)
python demo.py --workflow sequential

# 3. Run ONLY the Parallel Multi-Zone Analytics Suite (Midtown + Queens + Financial)
python demo.py --workflow parallel

# 4. Run ONLY the Iterative Z-Score Quality Loop (Audit -> Impute -> Certify)
python demo.py --workflow loop

# 5. Run ONLY the Custom Intent Dynamic Router
python demo.py --workflow custom
```

#### What Each Command Does Deterministically:
- **`--workflow sequential`**: Calls `execute_sequential_pipeline()`. Executes Step 1 ➔ Step 2 ➔ Step 3 ➔ Step 4. Asserts each step returns `status: true`. If any step fails, halts immediately. Outputs the formatted NYC Transit Geo-Zone Commuter Mobility Bulletin.
- **`--workflow parallel`**: Calls `execute_parallel_pipeline()`. Concurrently analyzes Midtown, Queens, and Financial District. Asserts worker success count $\ge 2$. Calls `synthesize_cross_zone_metrics()` and displays the ranked citywide scorecard.
- **`--workflow loop`**: Calls `execute_loop_calibration()`. Runs iterative audit and imputation cycles until Data Quality Confidence reaches $\ge 95\%$ or terminates at `max_iterations = 4`.
- **`--workflow custom`**: Calls `execute_custom_routing()` across three test prompts, evaluating `resolve_geo_intent()` and verifying deterministic dispatch.

---

### Tier 2: ADK CLI Deterministic Execution (`uv run adk run`)

In Google ADK, `agent.py` exports `root_agent`. The environment variable `WORKFLOW_TYPE` deterministically configures which `Workflow` graph is compiled and executed:

| Workflow Pattern | CLI Command | Step-by-Step Deterministic Sequence |
|---|---|---|
| **Sequential** | `WORKFLOW_TYPE=sequential uv run adk run . "Analyze peak commuter flow for Midtown Manhattan"` | 1. `IngestionAgent` queries observations & writes to `state["telemetry_data"]`<br/>2. `TimeSlotAggregatorAgent` reads telemetry & writes to `state["slotted_data"]`<br/>3. `PeakWindowAnalyzerAgent` computes peak windows & writes to `state["metrics_data"]`<br/>4. `GeoBriefingReporterAgent` formats & presents mobility bulletin |
| **Parallel** | `WORKFLOW_TYPE=parallel uv run adk run . "Analyze all zones in parallel"` | 1. Fan-out concurrently to `MidtownZoneAnalyst`, `QueensZoneAnalyst`, and `DowntownFinancialZoneAnalyst`<br/>2. Each worker calls `run_zone_analysis(zone_id)`<br/>3. `JoinNode("merge_zones")` synchronizes worker completions<br/>4. `CrossZoneGeoSynthesizer` ranks zones by flow volume |
| **Loop** | `WORKFLOW_TYPE=loop uv run adk run . "Calibrate turnstile telemetry data"` | 1. `ZScoreAnomalyDetector` runs `detect_zscore_outliers()`<br/>2. `evaluate_quality_route` checks `confidence >= 0.95`<br/>3. If `< 0.95` (`continue`), `SpatialImputerAgent` imputes medians & loops back<br/>4. If $\ge 0.95$ (`exit`), `GeoQualityCertifierAgent` issues certification |
| **Custom Router** | `WORKFLOW_TYPE=custom uv run adk run . "Compare commuter surges across all New York zones in parallel"` | 1. `GeoZoneDynamicRouter` calls `resolve_geo_intent(prompt)`<br/>2. Resolves route (`midtown_specialist`, `parallel_multi_zone`, `loop_quality_calibration`, etc.)<br/>3. Deterministically dispatches to target engine |

---

### Tier 3: Programmatic Python API

For deterministic backend execution without LLM non-determinism:

#### 1. Sequential Pipeline
```python
from workflow_agent.workflows.sequential import execute_sequential_pipeline

result = execute_sequential_pipeline(zone_id="ZONE_MIDTOWN_COMMERCIAL")
if result["status"]:
    print("Status:", result["message"])
    print("Report:\n", result["data"]["report"])
    for step in result["trajectory"]:
        print(f"  Step {step['step']} ({step['task']}): {'PASS' if step['status'] else 'FAIL'}")
else:
    print("Pipeline Halted:", result["message"])
```

#### 2. Parallel Multi-Zone Analytics
```python
from workflow_agent.workflows.parallel import execute_parallel_pipeline

result = execute_parallel_pipeline(zone_ids=["ZONE_MIDTOWN_COMMERCIAL", "ZONE_DOWNTOWN_FINANCIAL", "ZONE_QUEENS_CORRIDOR"])
if result["status"]:
    print("Busiest Zone:", result["data"]["scorecard"]["citywide_busiest_zone"])
    for z in result["data"]["scorecard"]["ranked_zones"]:
        print(f"  {z['zone_name']}: {z['total_flow']:,} commuters (Peak: {z['peak_arrival_window']})")
```

#### 3. Iterative Loop Calibration
```python
from workflow_agent.workflows.loop import execute_loop_calibration

result = execute_loop_calibration(zone_id="ZONE_MIDTOWN_COMMERCIAL", max_iterations=4, target_confidence=0.95)
if result["status"]:
    print(f"Certified: {result['data']['certified']} in {result['data']['total_iterations']} iteration(s)")
    print("Final Confidence Score:", f"{result['data']['final_confidence_score']*100:.1f}%")
```

#### 4. Custom Intent Routing
```python
from workflow_agent.workflows.custom import execute_custom_routing

result = execute_custom_routing(user_prompt="Sensor telemetry in Zone 1 is noisy, run calibration loop")
if result["status"]:
    print("Dispatched Engine:", result["data"]["dispatched_engine"])
    print("Sub-Result:", result["data"]["result"]["message"])
```

---

### Strict Error Handling & Flow Control Contract

Every task function and step adheres to this deterministic contract:
1. **Return Shape**: Always returns a dictionary `{"status": bool, "message": str, "data": Any}`.
2. **Continue Condition**: Downstream tasks only proceed if `step_result.get("status") is True`.
3. **Halt Condition**: If any step encounters an error or returns `status: False`, the workflow halts immediately, captures diagnostic context in `message`, and does not invoke subsequent steps.

---

## 7. Interactive Web Playground (`uv run adk web`)

Launch the visual graph and state inspector:
```bash
# Launch via Makefile
make run-workflow

# Or launch directly with uv
uv run adk web workflow_agent/
```
Open `http://localhost:8000` to inspect node execution, session state deltas, and live event emissions.

---

## 8. Verification Plan

1. **Cryptographic Integrity**: Verify all 4 prompt files validate through `SecuredToolAgent.load_prompt_asset()` with 0 security quarantines.
2. **Sequential Run**: Verify `python demo.py --workflow sequential` queries BQ, computes time slots, and generates geo-brief.
3. **Parallel Run**: Verify `python demo.py --workflow parallel` concurrently runs Midtown, Queens, and Financial analysts and merges results.
4. **Loop Run**: Verify `python demo.py --workflow loop` detects Z-score outliers, calibrates values, and escalates out of loop.
5. **Custom Run**: Verify `python demo.py --workflow custom` dynamically routes based on input query intent.
6. **All Workflows Run**: Verify `python demo.py --workflow all` runs complete suite end-to-end.
7. **ADK CLI Run**: Verify `uv run adk run workflow_agent/ "Analyze commuter peak times in Midtown"` executes cleanly.

