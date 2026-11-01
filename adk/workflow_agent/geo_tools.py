"""
NYC Transit MTA Geo-Fencing & Commuter Analytics SQL Domain Tools.

This module loads domain semantics from `skills/geo_fencing/SKILL.md` and builds
analytical SQL queries executed via the generic BigQuery conduit (`BigQueryGeoAggregateStrategy`).
All calculations (time-slot aggregations, Net Directional Ratio, Z-score anomalies, and
spatial median imputation) are pushed down to SQL.

All functions follow the standardized return contract:
    {
        "status": bool,      # True on successful execution, False on error
        "message": str,      # Human-readable status or diagnostic error message
        "data": Any          # Result payload (dict, list, or None)
    }
"""

import os
import sys
from functools import lru_cache
from typing import Dict, Any, List, Optional
import yaml
from google.adk.tools import ToolContext

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ADK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ADK_ROOT not in sys.path:
    sys.path.insert(0, ADK_ROOT)

from commands.bq.geo_aggregate_query import BigQueryGeoAggregateStrategy  # noqa: E402


# -----------------------------------------------------------------------------
# Domain Skill Loader (Single Source of Truth from skills/geo_fencing/SKILL.md)
# -----------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _load_geo_skill_spec() -> Dict[str, Any]:
    """Loads YAML frontmatter from skills/geo_fencing/SKILL.md."""
    skill_path = os.path.join(ADK_ROOT, "skills", "geo_fencing", "SKILL.md")
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---", 2)
    return yaml.safe_load(parts[1]) if len(parts) >= 3 else {}


def _get_zone_registry() -> Dict[str, Dict[str, Any]]:
    """Maps zone_id to its metadata from the domain skill specification."""
    spec = _load_geo_skill_spec()
    registry: Dict[str, Dict[str, Any]] = {}
    for zone in spec.get("geo_zones", {}).values():
        zid = zone["zone_id"]
        registry[zid] = {
            "name": zone.get("neighborhood", zid),
            "stations": zone.get("primary_stations", []),
            "role": zone.get("role", ""),
            "expected_peak": zone.get("expected_peak", ""),
        }
    return registry


def _get_table_fqn() -> Dict[str, str]:
    """Returns fully qualified table names from the domain skill governance block."""
    gov = _load_geo_skill_spec().get("domain_governance", {})
    proj = gov.get("cloud_project", "ozkary-de-101")
    ds = gov.get("dataset", "mta_dev")
    return {
        "project": proj,
        "fact_turnstile": f"`{proj}.{ds}.{gov.get('fact_table', 'fact_turnstile')}`",
        "dim_station": f"`{proj}.{ds}.{gov.get('dim_station_table', 'dim_station')}`",
    }


def _build_base_cte(stations: List[str], date_filter: Optional[str] = None) -> str:
    """Renders the shared base CTE mapping station observations into canonical time slots."""
    tables = _get_table_fqn()
    slots = _load_geo_skill_spec().get("time_slots", {})
    m_start, m_end = slots.get("morning", {}).get("start_hour", 8), slots.get("morning", {}).get("end_hour", 11)
    a_start, a_end = slots.get("afternoon", {}).get("start_hour", 12), slots.get("afternoon", {}).get("end_hour", 15)
    n_start, n_end = slots.get("night", {}).get("start_hour", 16), slots.get("night", {}).get("end_hour", 20)

    station_list = ", ".join(f"'{s}'" for s in stations)
    station_clause = f"AND s.station_name IN ({station_list})" if stations else ""
    date_clause = f"AND {date_filter}" if date_filter else ""

    return f"""
WITH slotted_telemetry AS (
  SELECT
    s.station_name,
    f.created_dt,
    f.exits AS arrival_count,
    f.entries AS departure_count,
    CASE
      WHEN EXTRACT(HOUR FROM f.created_dt) >= {m_start} AND EXTRACT(HOUR FROM f.created_dt) < {m_end} THEN 'morning_rush'
      WHEN EXTRACT(HOUR FROM f.created_dt) >= {a_start} AND EXTRACT(HOUR FROM f.created_dt) < {a_end} THEN 'afternoon_midday'
      WHEN EXTRACT(HOUR FROM f.created_dt) >= {n_start} AND EXTRACT(HOUR FROM f.created_dt) < {n_end} THEN 'evening_rush'
      ELSE 'off_peak'
    END AS time_slot
  FROM {tables['fact_turnstile']} f
  JOIN {tables['dim_station']} s
    ON f.sk_station = s.sk_station
  WHERE 1=1
    {station_clause}
    {date_clause}
)
""".strip()


def _save_state(tool_context: Optional[ToolContext], **kwargs) -> None:
    """Safely updates ADK session state when tool_context is provided."""
    if tool_context and hasattr(tool_context, "state"):
        tool_context.state.update(kwargs)


# -----------------------------------------------------------------------------
# Domain SQL Tools
# -----------------------------------------------------------------------------
def query_zone_commuters(
    zone_id: str = "ZONE_MIDTOWN_COMMERCIAL",
    stations: Optional[List[str]] = None,
    date_filter: Optional[str] = None,
    bq_strategy: Optional[BigQueryGeoAggregateStrategy] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Executes a SQL query to retrieve station-level turnstile observations for a target geo-zone.
    """
    try:
        registry = _get_zone_registry()
        target_stations = stations or registry.get(zone_id, {}).get("stations", [])
        base_cte = _build_base_cte(target_stations, date_filter)

        sql = f"""
{base_cte}
SELECT
  station_name,
  time_slot,
  SUM(arrival_count) AS arrival_count,
  SUM(departure_count) AS departure_count
FROM slotted_telemetry
WHERE time_slot != 'off_peak'
GROUP BY station_name, time_slot
ORDER BY station_name, time_slot;
""".strip()

        conduit = bq_strategy or BigQueryGeoAggregateStrategy()
        result = conduit.execute_query(query=sql)
        if not result.get("status"):
            return result

        _save_state(tool_context, telemetry_data=result["data"], zone_id=zone_id)
        return {
            "status": True,
            "message": f"Retrieved BigQuery records for zone '{zone_id}'.",
            "data": result["data"],
        }
    except Exception as e:
        return {"status": False, "message": f"Error in query_zone_commuters: {e}", "data": None}


def calculate_time_slots(
    zone_id: str = "ZONE_MIDTOWN_COMMERCIAL",
    date_filter: Optional[str] = None,
    bq_strategy: Optional[BigQueryGeoAggregateStrategy] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Executes a SQL aggregation grouping turnstile observations into canonical time slots.
    """
    try:
        if tool_context and hasattr(tool_context, "state"):
            zone_id = tool_context.state.get("zone_id", zone_id)

        stations = _get_zone_registry().get(zone_id, {}).get("stations", [])
        base_cte = _build_base_cte(stations, date_filter)

        sql = f"""
{base_cte}
SELECT
  time_slot,
  SUM(arrival_count) AS arrivals,
  SUM(departure_count) AS departures,
  COUNT(1) AS count
FROM slotted_telemetry
WHERE time_slot != 'off_peak'
GROUP BY time_slot
ORDER BY time_slot;
""".strip()

        conduit = bq_strategy or BigQueryGeoAggregateStrategy()
        result = conduit.execute_query(query=sql)
        if not result.get("status"):
            return result

        _save_state(tool_context, slotted_data=result["data"])
        return {
            "status": True,
            "message": f"Time slots aggregated via SQL for zone '{zone_id}'.",
            "data": result["data"],
        }
    except Exception as e:
        return {"status": False, "message": f"Error in calculate_time_slots: {e}", "data": None}


def identify_peak_window(
    zone_id: str = "ZONE_MIDTOWN_COMMERCIAL",
    date_filter: Optional[str] = None,
    bq_strategy: Optional[BigQueryGeoAggregateStrategy] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Executes a SQL analytical query to identify peak arrival/departure windows,
    compute the Net Directional Ratio (NDR), and classify the zone mobility profile.
    """
    try:
        if tool_context and hasattr(tool_context, "state"):
            zone_id = tool_context.state.get("zone_id", zone_id)

        stations = _get_zone_registry().get(zone_id, {}).get("stations", [])
        base_cte = _build_base_cte(stations, date_filter)

        sql = f"""
{base_cte},
slot_totals AS (
  SELECT
    time_slot,
    SUM(arrival_count) AS arrivals,
    SUM(departure_count) AS departures
  FROM slotted_telemetry
  WHERE time_slot != 'off_peak'
  GROUP BY time_slot
),
ranked_slots AS (
  SELECT
    FIRST_VALUE(time_slot) OVER (ORDER BY arrivals DESC) AS peak_arrival_window,
    MAX(arrivals) OVER () AS peak_arrival_volume,
    FIRST_VALUE(time_slot) OVER (ORDER BY departures DESC) AS peak_departure_window,
    MAX(departures) OVER () AS peak_departure_volume,
    ROUND(
      SAFE_DIVIDE(
        SUM(CASE WHEN time_slot = 'morning_rush' THEN arrivals ELSE 0 END) OVER (),
        NULLIF(SUM(CASE WHEN time_slot = 'morning_rush' THEN departures ELSE 0 END) OVER (), 0)
      ), 2
    ) AS morning_net_directional_ratio
  FROM slot_totals
  LIMIT 1
)
SELECT
  *,
  CASE
    WHEN morning_net_directional_ratio > 1.5 THEN 'Commercial / Employment Destination (Inflow Heavy)'
    WHEN morning_net_directional_ratio < 0.7 THEN 'Residential Feeder Corridor (Outflow Heavy)'
    ELSE 'Balanced Mixed-Use / Intermodal Transfer Hub'
  END AS zone_mobility_profile
FROM ranked_slots;
""".strip()

        conduit = bq_strategy or BigQueryGeoAggregateStrategy()
        result = conduit.execute_query(query=sql)
        if not result.get("status"):
            return result

        data = result["data"][0] if isinstance(result["data"], list) and result["data"] else result["data"]
        _save_state(tool_context, metrics_data=data, peak_metrics=data)
        return {
            "status": True,
            "message": f"Peak window and NDR computed via SQL for zone '{zone_id}'.",
            "data": data,
        }
    except Exception as e:
        return {"status": False, "message": f"Error in identify_peak_window: {e}", "data": None}


def generate_geo_brief(
    analysis_metrics: Optional[Dict[str, Any]] = None,
    zone_id: Optional[str] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Renders the executive transit operations bulletin using the generic report container
    in `BigQueryGeoAggregateStrategy.render_report`.
    """
    try:
        if not analysis_metrics and tool_context and hasattr(tool_context, "state"):
            analysis_metrics = tool_context.state.get("metrics_data") or tool_context.state.get("peak_metrics")
        if not zone_id and tool_context and hasattr(tool_context, "state"):
            zone_id = tool_context.state.get("zone_id")

        zone_id = zone_id or "ZONE_MIDTOWN_COMMERCIAL"
        if not analysis_metrics or not isinstance(analysis_metrics, dict):
            return {
                "status": False,
                "message": "analysis_metrics is required to render the report.",
                "data": None,
            }

        zone_meta = _get_zone_registry().get(zone_id, {"name": zone_id, "stations": []})
        peak_arr = str(analysis_metrics.get("peak_arrival_window", "N/A"))
        peak_dep = str(analysis_metrics.get("peak_departure_window", "N/A"))

        report = BigQueryGeoAggregateStrategy.render_report(
            title="NYC TRANSIT GEO-ZONE COMMUTER MOBILITY BULLETIN",
            metadata={
                "Target Zone": f"{zone_meta['name']} ({zone_id})",
                "Monitored Stations": ", ".join(zone_meta["stations"]),
                "Spatial Profile": analysis_metrics.get("zone_mobility_profile", "N/A"),
                "Net Direction Ratio": f"{analysis_metrics.get('morning_net_directional_ratio', 1.0)} (Morning Inbound / Outbound)",
            },
            sections={
                "Peak Mobility Windows": [
                    f"Peak Arrival Influx:    {peak_arr.replace('_', ' ').title()} ({analysis_metrics.get('peak_arrival_volume', 0):,} passengers)",
                    f"Peak Departure Outflow: {peak_dep.replace('_', ' ').title()} ({analysis_metrics.get('peak_departure_volume', 0):,} passengers)",
                ],
                "Operational Dispatch Directive": [
                    f"Allocate maximum turnstile entry-gate throughput during '{peak_dep.replace('_', ' ')}'.",
                    f"Schedule location-based dynamic messaging near station exits during '{peak_arr.replace('_', ' ')}'.",
                ],
            },
        )

        _save_state(tool_context, final_report=report)
        return {
            "status": True,
            "message": "Executive geo-zone briefing generated.",
            "data": {"report": report},
        }
    except Exception as e:
        return {"status": False, "message": f"Error in generate_geo_brief: {e}", "data": None}


def synthesize_cross_zone_metrics(
    zone_ids: Optional[List[str]] = None,
    date_filter: Optional[str] = None,
    bq_strategy: Optional[BigQueryGeoAggregateStrategy] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Executes a multi-zone SQL rollup ranking geographic zones by total commuter flow.
    """
    try:
        registry = _get_zone_registry()
        target_zones = zone_ids or [
            "ZONE_MIDTOWN_COMMERCIAL",
            "ZONE_DOWNTOWN_FINANCIAL",
            "ZONE_QUEENS_CORRIDOR",
        ]

        # Build SQL mapping stations to their zone_id
        when_clauses = []
        all_stations = []
        for zid in target_zones:
            z_stations = registry.get(zid, {}).get("stations", [])
            if z_stations:
                all_stations.extend(z_stations)
                st_in = ", ".join(f"'{s}'" for s in z_stations)
                when_clauses.append(f"WHEN station_name IN ({st_in}) THEN '{zid}'")

        base_cte = _build_base_cte(all_stations, date_filter)
        case_zone = "\n      ".join(when_clauses)

        sql = f"""
{base_cte},
zone_tagged AS (
  SELECT
    CASE
      {case_zone}
      ELSE 'OTHER'
    END AS zone_id,
    time_slot,
    arrival_count,
    departure_count
  FROM slotted_telemetry
  WHERE time_slot != 'off_peak'
),
zone_aggregates AS (
  SELECT
    zone_id,
    SUM(arrival_count + departure_count) AS total_flow,
    ARRAY_AGG(time_slot ORDER BY arrival_count DESC LIMIT 1)[OFFSET(0)] AS peak_arrival_window,
    ROUND(
      SAFE_DIVIDE(
        SUM(CASE WHEN time_slot = 'morning_rush' THEN arrival_count ELSE 0 END),
        NULLIF(SUM(CASE WHEN time_slot = 'morning_rush' THEN departure_count ELSE 0 END), 0)
      ), 2
    ) AS ndr
  FROM zone_tagged
  GROUP BY zone_id
)
SELECT
  zone_id,
  total_flow,
  peak_arrival_window,
  ndr,
  CASE
    WHEN ndr > 1.5 THEN 'Commercial / Employment Destination (Inflow Heavy)'
    WHEN ndr < 0.7 THEN 'Residential Feeder Corridor (Outflow Heavy)'
    ELSE 'Balanced Mixed-Use / Intermodal Transfer Hub'
  END AS profile
FROM zone_aggregates
ORDER BY total_flow DESC;
""".strip()

        conduit = bq_strategy or BigQueryGeoAggregateStrategy()
        result = conduit.execute_query(query=sql)
        if not result.get("status"):
            return result

        rows = result["data"] if isinstance(result["data"], list) else []
        for r in rows:
            zid = r.get("zone_id", "")
            r["zone_name"] = registry.get(zid, {}).get("name", zid)

        return {
            "status": True,
            "message": f"Synthesized comparative SQL metrics across {len(rows)} geographic zones.",
            "data": {
                "ranked_zones": rows,
                "citywide_busiest_zone": rows[0]["zone_name"] if rows else "N/A",
            },
        }
    except Exception as e:
        return {"status": False, "message": f"Error in synthesize_cross_zone_metrics: {e}", "data": None}


def detect_zscore_outliers(
    zone_id: str = "ZONE_MIDTOWN_COMMERCIAL",
    z_threshold: Optional[float] = None,
    date_filter: Optional[str] = None,
    bq_strategy: Optional[BigQueryGeoAggregateStrategy] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Executes a SQL statistical window query computing Z-scores (Z = (x - mean) / std)
    to flag turnstile counter anomalies and calculate data quality confidence.
    """
    try:
        spec = _load_geo_skill_spec()
        threshold = z_threshold or float(spec.get("outlier_detection", {}).get("z_score_threshold", 2.5))
        stations = _get_zone_registry().get(zone_id, {}).get("stations", [])
        base_cte = _build_base_cte(stations, date_filter)

        sql = f"""
{base_cte},
scored_records AS (
  SELECT
    station_name,
    time_slot,
    arrival_count,
    departure_count,
    ROUND(
      SAFE_DIVIDE(
        arrival_count - AVG(arrival_count) OVER (PARTITION BY time_slot),
        NULLIF(STDDEV(arrival_count) OVER (PARTITION BY time_slot), 0)
      ), 2
    ) AS z_score
  FROM slotted_telemetry
  WHERE time_slot != 'off_peak'
)
SELECT
  *,
  CASE
    WHEN ABS(z_score) > {threshold} OR arrival_count > 50000 OR arrival_count < 0 THEN TRUE
    ELSE FALSE
  END AS is_outlier
FROM scored_records;
""".strip()

        conduit = bq_strategy or BigQueryGeoAggregateStrategy()
        result = conduit.execute_query(query=sql)
        if not result.get("status"):
            return result

        records = result["data"] if isinstance(result["data"], list) else []
        outliers = [r for r in records if r.get("is_outlier")]
        clean_records = [r for r in records if not r.get("is_outlier")]
        total = max(len(records), 1)
        confidence_score = round(1.0 - (len(outliers) / total), 2)

        _save_state(tool_context, outliers=outliers, confidence_score=confidence_score)
        return {
            "status": True,
            "message": f"SQL Z-Score scan complete. Flagged {len(outliers)} outliers across {len(records)} records.",
            "data": {
                "outlier_count": len(outliers),
                "total_records": len(records),
                "confidence_score": confidence_score,
                "outliers": outliers,
                "clean_records": clean_records,
            },
        }
    except Exception as e:
        return {"status": False, "message": f"Error in detect_zscore_outliers: {e}", "data": None}


def impute_spatial_baseline(
    zone_id: str = "ZONE_MIDTOWN_COMMERCIAL",
    z_threshold: Optional[float] = None,
    date_filter: Optional[str] = None,
    bq_strategy: Optional[BigQueryGeoAggregateStrategy] = None,
    tool_context: Optional[ToolContext] = None,
) -> Dict[str, Any]:
    """
    Executes a SQL window query using PERCENTILE_CONT(0.5) to impute anomalous station counts
    with the spatial median of neighboring stations in the same geo-zone and time slot.
    """
    try:
        spec = _load_geo_skill_spec()
        threshold = z_threshold or float(spec.get("outlier_detection", {}).get("z_score_threshold", 2.5))
        stations = _get_zone_registry().get(zone_id, {}).get("stations", [])
        base_cte = _build_base_cte(stations, date_filter)

        sql = f"""
{base_cte},
scored_records AS (
  SELECT
    station_name,
    time_slot,
    arrival_count,
    departure_count,
    SAFE_DIVIDE(
      arrival_count - AVG(arrival_count) OVER (PARTITION BY time_slot),
      NULLIF(STDDEV(arrival_count) OVER (PARTITION BY time_slot), 0)
    ) AS z_score,
    PERCENTILE_CONT(arrival_count, 0.5) OVER (PARTITION BY time_slot) AS spatial_median_arrival
  FROM slotted_telemetry
  WHERE time_slot != 'off_peak'
)
SELECT
  station_name,
  time_slot,
  CASE
    WHEN ABS(z_score) > {threshold} OR arrival_count > 50000 OR arrival_count < 0
      THEN CAST(ROUND(spatial_median_arrival) AS INT64)
    ELSE arrival_count
  END AS arrival_count,
  departure_count,
  CASE
    WHEN ABS(z_score) > {threshold} OR arrival_count > 50000 OR arrival_count < 0 THEN TRUE
    ELSE FALSE
  END AS calibrated
FROM scored_records;
""".strip()

        conduit = bq_strategy or BigQueryGeoAggregateStrategy()
        result = conduit.execute_query(query=sql)
        if not result.get("status"):
            return result

        calibrated = result["data"] if isinstance(result["data"], list) else []
        imputed_count = sum(1 for r in calibrated if r.get("calibrated"))
        _save_state(tool_context, telemetry_data=calibrated)

        return {
            "status": True,
            "message": f"Calibrated {imputed_count} records via SQL PERCENTILE_CONT spatial median.",
            "data": {
                "calibrated_records": calibrated,
                "imputed_count": imputed_count,
            },
        }
    except Exception as e:
        return {"status": False, "message": f"Error in impute_spatial_baseline: {e}", "data": None}


def resolve_geo_intent(user_prompt: str) -> Dict[str, Any]:
    """
    Maps natural language query intent to the corresponding geo-zone and workflow pattern
    using the station and neighborhood definitions in `skills/geo_fencing/SKILL.md`.
    """
    try:
        prompt_lower = user_prompt.lower()
        if any(k in prompt_lower for k in ("compare", "all zones", "cross zone", "parallel")):
            return {
                "status": True,
                "message": "Resolved route: parallel_multi_zone",
                "data": {"target_route": "parallel_multi_zone", "zone_id": None},
            }
        if any(k in prompt_lower for k in ("clean", "outlier", "calibrate", "loop")):
            return {
                "status": True,
                "message": "Resolved route: loop_quality_calibration",
                "data": {"target_route": "loop_quality_calibration", "zone_id": "ZONE_MIDTOWN_COMMERCIAL"},
            }

        route_map = {
            "ZONE_MIDTOWN_COMMERCIAL": "midtown_specialist",
            "ZONE_DOWNTOWN_FINANCIAL": "downtown_financial_specialist",
            "ZONE_QUEENS_CORRIDOR": "queens_specialist",
        }
        for zid, meta in _get_zone_registry().items():
            tokens = [meta["name"].lower()] + [s.lower() for s in meta["stations"]]
            if any(t in prompt_lower for t in tokens) or zid.lower() in prompt_lower:
                route = route_map.get(zid, "sequential_pipeline")
                return {
                    "status": True,
                    "message": f"Resolved route: {route}",
                    "data": {"target_route": route, "zone_id": zid},
                }

        return {
            "status": True,
            "message": "Resolved route: sequential_pipeline",
            "data": {"target_route": "sequential_pipeline", "zone_id": "ZONE_MIDTOWN_COMMERCIAL"},
        }
    except Exception as e:
        return {"status": False, "message": f"Error in resolve_geo_intent: {e}", "data": None}
