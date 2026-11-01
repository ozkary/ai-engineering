---
name: geo_fencing
version: "1.0.0"
spec_signature: "HMAC-SHA256"
bounded_context: "nyc_transit_geo_fencing"
domain_governance:
  cloud_project: "ozkary-de-101"
  dataset: "mta_data"
  fact_table: "fact_turnstile"
  dim_station_table: "dim_station"
  dim_booth_table: "dim_booth"
  view_geo_agg: "vw_geo_turnstile_agg"
geo_zones:
  midtown_commercial:
    zone_id: "ZONE_MIDTOWN_COMMERCIAL"
    neighborhood: "Midtown Manhattan"
    role: "Employment & Commercial Destination"
    primary_stations:
      - "59 ST"
      - "34 ST-HERALD SQ"
      - "GRD CNTRL-42 ST"
      - "34 ST-PENN STA"
    expected_peak: "Morning Arrivals (08:00 - 11:00)"
  downtown_financial:
    zone_id: "ZONE_DOWNTOWN_FINANCIAL"
    neighborhood: "Financial District / Wall Street"
    role: "Financial & Corporate Core"
    primary_stations:
      - "FULTON ST"
      - "WALL ST"
      - "WHITEHALL ST"
    expected_peak: "Market Bell Arrivals (08:00 - 10:00)"
  queens_corridor:
    zone_id: "ZONE_QUEENS_CORRIDOR"
    neighborhood: "Long Island City / Queens"
    role: "Mixed Commercial & Residential Feeder"
    primary_stations:
      - "VERNON-JACKSON"
      - "COURT SQ"
    expected_peak: "Morning Departures (07:00 - 10:00)"
  midtown_south_hub:
    zone_id: "ZONE_MIDTOWN_SOUTH_HUB"
    neighborhood: "Union Square / Flatiron"
    role: "Intermodal Transit & Cultural Corridor"
    primary_stations:
      - "14 ST-UNION SQ"
    expected_peak: "Midday & Evening Cross-town Flow (12:00 - 20:00)"
time_slots:
  morning:
    start_hour: 8
    end_hour: 11
    label: "08:00 - 11:00"
    significance: "Morning Commuter Rush (Commercial Inflow / Residential Outflow)"
  afternoon:
    start_hour: 12
    end_hour: 15
    label: "12:00 - 15:00"
    significance: "Midday Business, Dining, and Retail Foot Traffic"
  night:
    start_hour: 16
    end_hour: 20
    label: "16:00 - 20:00"
    significance: "Evening Commuter Departure Rush"
outlier_detection:
  z_score_threshold: 2.5
workflows:
  sequential:
    agent_name: "mta_sequential_geo_pipeline"
    purpose: "4-stage sequential pipeline (Ingestion -> Time Slots -> Peak/NDR -> Executive Bulletin) for single-zone operational resource allocation."
    sample_prompts:
      - "Analyze peak commuter flow for Midtown Manhattan to plan turnstile gate allocation."
      - "Evaluate commuter arrival and departure surges in the Financial District / Wall Street."
      - "Generate an operational resource dispatch brief for the Union Square intermodal hub."
  parallel:
    agent_name: "mta_parallel_workflow_suite"
    purpose: "Concurrent multi-zone analysis across Midtown, Queens, and Financial District followed by a citywide comparative ranking scorecard."
    sample_prompts:
      - "Analyze all NYC transit zones in parallel and rank them by total commuter flow."
      - "Compare morning inbound vs outbound commuter dynamics across Midtown, Financial District, and Queens."
  loop:
    agent_name: "mta_quality_refinement_loop"
    purpose: "Iterative statistical Z-score outlier detection (|Z| > 2.5) and SQL PERCENTILE_CONT spatial median calibration until data confidence >= 95%."
    sample_prompts:
      - "Audit and calibrate turnstile telemetry data for Midtown Manhattan until quality confidence reaches 95%."
      - "Check the Financial District stations for Z-score sensor spikes and impute anomalies."
  custom:
    agent_name: "mta_custom_dynamic_router"
    purpose: "Dynamic context-aware intent router that dispatches queries to individual zone specialists or full workflow suites."
    sample_prompts:
      - "What is the peak arrival window and NDR for Wall Street and Fulton St?"
      - "Compare commuter surges across all New York zones side by side."
allowed_tools:
  - commands/bq/geo_aggregate_query
  - tools/bq/execute_sql
---

# NYC Transit MTA Geo-Fencing & Commuter Analytics Domain Skill

## Purpose & Scope
This skill equips agents with domain intelligence for NYC Transit geo-fencing, station geographic clustering, commuter arrival/departure dynamics, and time-slot aggregations. It establishes spatial boundaries around commercial hubs, financial centers, and transit feeder neighborhoods to enable location-based operational decisions, advertising windows, and commuter crowd management.

> [!IMPORTANT]
> **Boundary Rule**: Skills teach domain judgment, spatial definitions, and analytical heuristics. This skill NEVER directly executes raw mutations or unvalidated SQL. It specifies the geo-fencing boundaries, time-slot definitions, and aggregation rules enforced by analytical commands and workflow agents.

---

## Domain Semantics & Directional Flow

Subway turnstile telemetry operates on directional flow:
1. **Exits (`exits`) = Commuter Arrivals**:
   - Represents riders exiting the subway station gates into the surrounding neighborhood or geo-zone.
   - High morning exits characterize an **Employment / Commercial Destination** (e.g. Midtown office towers, Wall Street financial firms).
2. **Entries (`entries`) = Commuter Departures**:
   - Represents riders entering the subway station to travel elsewhere.
   - High morning entries characterize a **Residential Feeder Zone** (e.g. outer-borough residential hubs).
3. **Net Directional Ratio ($NDR$)**:
   $$\text{NDR} = \frac{\text{Morning Arrivals (Exits)}}{\text{Morning Departures (Entries)}}$$
   - $\text{NDR} > 1.5$: Primary Commercial/Employment Hub.
   - $\text{NDR} < 0.7$: Primary Residential Feeder Zone.
   - $0.7 \le \text{NDR} \le 1.5$: Mixed-Use / Intermodal Transfer Hub.

---

## Standard Operating Procedure (SOP)

### 1. Spatial Station Mapping
- Stations must be mapped to their designated Geo-Zone using the `geo_zones` registry.
- Do NOT hardcode arbitrary station names in downstream models; join against `mta_dev.dim_station` using surrogate key `sk_station` or normalized `station_name`.

### 2. Time-Slot Aggregation
Turnstile time-series observations must be bucketed into the three canonical analytical windows:
- **Morning**: `08:00:00 <= TIME < 11:00:00`
- **Afternoon**: `12:00:00 <= TIME < 15:00:00`
- **Night / Evening**: `16:00:00 <= TIME < 20:00:00`

### 3. Statistical Quality & Z-Score Anomaly Detection
Before finalizing peak time identification, compute the Z-score for net entries and exits per station:
$$Z = \frac{x - \mu}{\sigma}$$
- If $|Z| > 2.5$, the observation is flagged as an anomaly (e.g., turnstile counter rollover or sensor hardware glitch).
- Anomalous records must be calibrated via spatial interpolation (using the median flow of adjacent stations in the same geo-zone) before computing zone totals.

### 4. Output Contract
Geo-zone analyses must emit a structured result conforming to:
```json
{
  "zone_id": "ZONE_MIDTOWN_COMMERCIAL",
  "total_arrivals": 45200,
  "total_departures": 18300,
  "net_directional_ratio": 2.47,
  "peak_arrival_window": "08:00 - 11:00",
  "peak_departure_window": "16:00 - 20:00",
  "dominant_profile": "Commercial Destination",
  "quality_confidence_score": 0.98
}
```
