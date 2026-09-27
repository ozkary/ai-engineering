---
name: bq_governance
version: "1.0.0"
spec_signature: "HMAC-SHA256"
governance_rules:
  partitioning: "mandatory"
  partition_field: "_PARTITIONDATE"
  expiration_days: 730
  naming_convention: "snake_case"
  allowed_tools:
    - tools/bq/table_exists
---

# BigQuery Governance & External Table Standards Skill

## Purpose & Scope
This skill equips the agent with enterprise governance policies and architectural standards for deploying BigQuery external tables over data lakehouse assets (Google Cloud Storage blobs).

> [!IMPORTANT]
> **Boundary Rule**: Skills enforce rules and standards. This skill NEVER generates or runs raw SQL scripts directly. It strictly validates and enriches schema decisions with governance attributes for deterministic command rendering.

---

## Standard Operating Procedure (SOP)

### 1. Partitioning & Ingestion Strategy
- **Mandatory Partitioning**: Every external table defined over time-series or telemetry files MUST define date partitioning.
- **Partition Column**: Use pseudo-column `_PARTITIONDATE` or a validated root-level `DATE`/`TIMESTAMP` column.
- **Partition Expiration**: External partitions or staging tables must enforce a maximum retention window of `730` days (2 years) unless exempted by enterprise data tier policies.

### 2. Lakehouse Table Naming Standards
- All dataset and table identifiers must strictly adhere to lowercase `snake_case`.
- Table prefix must reflect the pipeline domain and data fidelity layer:
  - Raw Ingestion / Staging: `raw_<domain>_<entity>` (e.g., `raw_mta_turnstiles`, `raw_iot_telemetry`)
  - Curated / Modeled: `stg_<domain>_<entity>` or `fact_<domain>_<entity>`
- Dashes (`-`), uppercase characters, and non-alphanumeric symbols are strictly prohibited.

### 3. Metadata & Audit Column Injection
Every inferred schema must be augmented with enterprise lineage and audit attributes:
- `_ingested_at`: `TIMESTAMP` populated with current load timestamp.
- `_source_file_uri`: `STRING` referencing the source GCS blob path.

---

## Output Contract (Governance Policy Decision)

When consulted alongside schema inference, this skill outputs governance parameters to be merged into the final Schema Decision Object:

```json
{
  "governance": {
    "target_dataset": "lakehouse_raw",
    "table_naming_rule": "raw_mta_<entity>",
    "partition_by": "_PARTITIONDATE",
    "partition_expiration_days": 730,
    "require_partition_filter": false,
    "audit_columns": [
      {
        "name": "_ingested_at",
        "type": "TIMESTAMP",
        "mode": "REQUIRED",
        "description": "Timestamp when this record was ingested into the analytical lakehouse"
      },
      {
        "name": "_source_uri",
        "type": "STRING",
        "mode": "REQUIRED",
        "description": "Origin GCS object URI"
      }
    ]
  }
}
```
