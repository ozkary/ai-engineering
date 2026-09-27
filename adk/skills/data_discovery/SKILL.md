---
name: data_discovery
version: "1.0.0"
spec_signature: "HMAC-SHA256"
allowed_tools:
  - tools/gcs/read_file_sample
  - tools/gcs/list_blobs
---

# Data Discovery & Schema Inference Skill

## Purpose & Scope
This skill equips the agent with domain intelligence for discovering file formats, inspecting raw payloads from storage (Google Cloud Storage), detecting schema anomalies, and inferring target warehouse column types.

> [!IMPORTANT]
> **Boundary Rule**: Skills teach judgment and rules. This skill NEVER generates raw SQL DDL, executable code, or pipeline mutation scripts. It strictly emits a structured JSON Schema Decision Object.

---

## Standard Operating Procedure (SOP)

### 1. Payload & Header Inspection
- Read the first preview chunk (up to 64KB or 20 lines) using `tools/gcs/read_file_sample`.
- Identify the serialization format:
  - **CSV / TSV**: Check for common delimiters (`,`, `\t`, `|`, `;`). Inspect if line 1 contains valid column headers or row values. Determine `skip_leading_rows` (default `1` if header present).
  - **JSON Lines (NDJSON)**: Check for valid line-delimited JSON objects.
  - **Parquet**: Binary magic bytes `PAR1`.

### 2. Type Mapping & Semantic Classification
Evaluate sample values across rows to infer target BigQuery types using standard mapping rules:
- **Timestamp / Temporal**:
  - Unix epoch integer/float values (e.g., `1715000000`, `1715000000.123`) $\rightarrow$ `TIMESTAMP`
  - ISO-8601 strings (`2026-09-15T10:00:00Z`) $\rightarrow$ `TIMESTAMP`
  - Date strings (`YYYY-MM-DD` or `YYYYMMDD`) $\rightarrow$ `DATE`
- **Numeric & Metrics**:
  - Floating point sensor readings, percentages, rates $\rightarrow$ `FLOAT64`
  - Sequential counters, integer counts, amounts in cents $\rightarrow$ `INT64`
- **Identifiers & Codes**:
  - Alphanumeric codes, UUIDs, station IDs, hardware serial numbers $\rightarrow$ `STRING`
- **Boolean**:
  - Values matching `true/false`, `0/1` flags, `yes/no` $\rightarrow$ `BOOL`

### 3. Anomaly & Quality Detection
- Check for ragged rows (varying column counts across lines).
- Check for null values or missing headers.
- Sanitize column names: convert spaces or special characters to snake_case (e.g., `C/A` $\rightarrow$ `c_a`, `Station Name` $\rightarrow$ `station_name`).

---

## Output Contract (Structured Schema Decision Object)

When invoked, this skill must analyze the input file sample and output ONLY a valid JSON object matching the following specification:

```json
{
  "format": "CSV",
  "delimiter": ",",
  "skip_leading_rows": 1,
  "confidence_score": 0.98,
  "columns": [
    {
      "name": "event_id",
      "type": "STRING",
      "mode": "REQUIRED",
      "description": "Unique event identifier"
    },
    {
      "name": "reading_timestamp",
      "type": "TIMESTAMP",
      "mode": "REQUIRED",
      "description": "Epoch timestamp inferred as TIMESTAMP"
    },
    {
      "name": "metric_value",
      "type": "FLOAT64",
      "mode": "NULLABLE",
      "description": "Sensor measurement float"
    }
  ]
}
```
