---
name: mta_transit_intelligence
version: "2.1.0"
spec_signature: "HMAC-SHA256"
bounded_context: "nyc_transit_turnstile"
domain_governance:
  cloud_project: "ozkary-de-101"
  dataset: "mta_dev"
  gcs_bucket: "ozkary_data_lake_ozkary-de-101"
  v1_storage_folder: "turnstile"
  v2_storage_folder: "turnstile_v2"
  v1_external_table: "ext_turnstile"
  v2_external_table: "ext_turnstile_v2"
allowed_tools:
  - tools/gcs/read_file_sample
---

# NYC Transit MTA Turnstile Domain Intelligence Skill

## Purpose & Scope
This skill equips the agent with domain intelligence for NYC Transit MTA turnstile telemetry, fare collection feeds, and warehouse governance. It enforces Domain-Driven Design (DDD) by isolating transit domain semantics, detecting schema drift between legacy (v1) feeds and modernized (v2) feeds, enforcing versioning governance, and proposing structured schema contracts for warehouse provisioning.

> [!IMPORTANT]
> **Boundary Rule**: Skills teach domain judgment, rules, and semantic heuristics. This skill NEVER generates or runs raw mutation scripts directly. It strictly validates and emits a structured JSON Schema Proposal Object.

---

## Domain Governance & Storage Rules

- **Cloud Project**: The cloud project for all MTA transit analytical resources is `ozkary-de-101`.
- **Target Dataset**: Use `mta_dev` for ALL tables, views, and stored procedures.
- **Storage Locations**:
  - GCS Bucket: `gs://ozkary_data_lake_ozkary-de-101/`
  - Legacy (v1) feeds land in `turnstile/` with filename pattern `YYMMDD.csv.gz`.
  - Modernized (v2) feeds land in `turnstile_v2/` with filename pattern `YYMMDD.csv.gz`.
- **Table Versioning Governance**:
  - The baseline production external table is **`mta_dev.ext_turnstile`** (v1).
  - **Overwriting Prohibition**: Never overwrite or alter `mta_dev.ext_turnstile` in-place when processing modernized feeds; doing so will break downstream views (`vw_turnstile`) and BI dashboards.
  - **Versioned Naming Rule**: Whenever a modernized feed (`v2`) is detected with breaking schema drift, the proposed external table MUST be versioned as **`ext_turnstile_v2`** (fully qualified: `ozkary-de-101.mta_dev.ext_turnstile_v2`).
- **Wildcard File Pattern Requirement**:
  - External tables MUST point to a wildcard URI pattern, NEVER to an individual file name (e.g. `240915.csv.gz`). Pointing to a single file prevents the table from loading additional files.
  - Baseline v1 URI Pattern: `gs://ozkary_data_lake_ozkary-de-101/turnstile/*.csv.gz`
  - Modernized v2 URI Pattern: `gs://ozkary_data_lake_ozkary-de-101/turnstile_v2/*.csv.gz`

---

## Domain Ubiquitous Language & Entity Semantics

The MTA fare collection network uses standardized transit hardware concepts:

| Field Concept | Legacy v1 Name | Modernized v2 Name | Type | Description |
| :--- | :--- | :--- | :---: | :--- |
| **Control Area** | `C/A` | `booth_id` | `STRING` | Station control area booth identifier (e.g., `A002`, `R101`). |
| **Remote Unit** | `UNIT` | `unit_id` | `STRING` | Remote turnstile controller sub-assembly unit (e.g., `R051`). |
| **Sub-unit Device** | `SCP` | `device_id` | `STRING` | Sub-unit turnstile position counter index (e.g., `02-00-00`). |
| **Station Facility** | `STATION` | `station_name` | `STRING` | Physical station facility name (e.g., `59 ST`, `TIMES SQ-42 ST`). |
| **Transit Lines** | `LINENAME` | `line_routes` | `STRING` | Subway lines accessible at station complex (e.g., `NQR456`). |
| **Division** | `DIVISION` | `division` | `STRING` | Historic transit operating division (`BMT`, `IND`, `IRT`). |
| **Temporal Observation** | `DATE`, `TIME` | `reading_timestamp` | `TIMESTAMP` | **Breaking Drift**: v1 splits into 2 text strings; v2 consolidates to single ISO-8601/epoch. |
| **Audit Status** | `DESC` | `audit_status` | `STRING` | Audit register event flag (`REGULAR`, `RECOVR AUD`). |
| **Fare Payment Method** | *(N/A in v1)* | `fare_method` | `STRING` | Contactless payment gateway method (`OMNY`, `MetroCard`). |
| **Volume Counts** | `ENTRIES`, `EXITS` | `entry_count`, `exit_count` | `INT64` | v1: Cumulative odometer counter; v2: Discrete incremental batch volume. |

---

## Standard Operating Procedure (SOP)

### 1. Payload & Header Inspection
- Read the sample payload using `tools/gcs/read_file_sample`.
- Identify the CSV delimiter (comma `,` or tab `\t`) and inspect header labels.

### 2. Schema Drift & Version Conflict Heuristics
Evaluate whether the input conforms to Baseline v1 or Conflicting v2:
- **Rule 1 (Temporal Consolidation)**: If separate `DATE` and `TIME` columns are present, classify as **Legacy v1**. If a unified `reading_timestamp` or `timestamp` column is present, classify as **Modernized v2** and map to `TIMESTAMP`.
- **Rule 2 (Identifier Normalization)**: Detect if legacy `C/A` has been normalized to `booth_id` or `station_id`.
- **Rule 3 (Dimensional Extension)**: Detect new columns such as `fare_method` (OMNY integration) or `device_status`.
- **Rule 4 (Drift Severity Flag)**: If a v2 feed arrives while the pipeline baseline is v1, set `breaking_drift_detected: true` to require Human-in-the-Loop approval.
- **Rule 5 (Table Target Resolution)**: 
  - For baseline v1 feeds, the target external table is `ext_turnstile`.
  - For modernized v2 feeds with breaking drift, the target external table MUST be **`ext_turnstile_v2`**.

---

## Output Contract (Schema Proposal Object)

When invoked, this skill emits strictly a valid JSON object matching this schema:

```json
{
  "domain": "mta_transit",
  "detected_version": "v2",
  "baseline_version": "v1",
  "target_project": "ozkary-de-101",
  "target_dataset": "mta_dev",
  "target_table": "ext_turnstile_v2",
  "storage_uri_pattern": "gs://ozkary_data_lake_ozkary-de-101/turnstile_v2/*.csv.gz",
  "breaking_drift_detected": true,
  "drift_summary": [
    "Consolidated separate DATE and TIME text columns into unified TIMESTAMP reading_timestamp",
    "Normalized C/A column to booth_id",
    "Introduced new dimensional attribute fare_method for contactless OMNY taps",
    "Transitioned from cumulative register counts to discrete incremental batch volumes"
  ],
  "format": "CSV",
  "delimiter": ",",
  "skip_leading_rows": 1,
  "columns": [
    {"name": "station_id", "type": "STRING", "mode": "REQUIRED", "description": "MTA station complex identifier"},
    {"name": "booth_id", "type": "STRING", "mode": "REQUIRED", "description": "Control area booth ID (formerly C/A)"},
    {"name": "reading_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Unified event timestamp"},
    {"name": "fare_method", "type": "STRING", "mode": "NULLABLE", "description": "Payment type (OMNY or MetroCard)"},
    {"name": "entry_count", "type": "INT64", "mode": "REQUIRED", "description": "Incremental turnstile entry count"},
    {"name": "exit_count", "type": "INT64", "mode": "REQUIRED", "description": "Incremental turnstile exit count"}
  ]
}
```
