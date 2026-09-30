---
name: bq_governance
version: "2.0.0"
spec_signature: "HMAC-SHA256"
governance_rules:
  external_table_prefix: "ext_"
  physical_table_prefix: "dim_"
  view_prefix: "vw_"
  stored_procedure_prefix: "sp_"
  pipeline_prefix: "dp_"
  column_naming: "snake_case"
  partitioning: "mandatory"
  partition_field: "_PARTITIONDATE"
  expiration_days: 730
  allowed_tools:
    - tools/bq/table_exists
---

# BigQuery Governance & External Table Standards Skill

## Purpose & Scope
This skill equips the agent with enterprise governance policies and architectural standards for deploying BigQuery external tables and lakehouse analytical objects over Google Cloud Storage assets.

> [!IMPORTANT]
> **Boundary Rule**: Skills enforce rules and standards. This skill NEVER generates or runs raw SQL scripts directly. It strictly validates and enriches schema decisions with governance attributes for deterministic command rendering.

---

## Standard Operating Procedure (SOP)

### 1. Architectural Naming Standards
All database identifiers must strictly adhere to lowercase `snake_case` with standardized layer prefixes:
- **External Tables**: MUST use the `ext_` prefix (e.g., `ext_<entity>`, `ext_<entity>_<version>`).
- **Physical Dimension Tables**: MUST use the `dim_` prefix (e.g., `dim_<entity>`).
- **Logical Views**: MUST use the `vw_` prefix for reporting/business logic layers (e.g., `vw_<entity>`).
- **Stored Procedures**: MUST use the `sp_` prefix followed by area and action (e.g., `sp_<area>_<action>`).
- **Data Pipelines**: MUST use the `dp_` prefix followed by area and action (e.g., `dp_<area>_<action>`).
- **Field & Column Naming**: Use lowercase `snake_case` for all column names without special characters.
- Dashes (`-`), uppercase characters, and non-alphanumeric symbols are strictly prohibited.

### 2. Partitioning & Ingestion Strategy
- **Wildcard Storage URIs**: External table URIs MUST ALWAYS use wildcard file patterns (e.g., `gs://bucket/folder/*.csv.gz` or `gs://bucket/folder/*`) instead of pointing to a single specific file. Pointing to a single file prevents the table from ingesting additional incoming and existing partition files.
- **Mandatory Partitioning**: Every external table defined over time-series or telemetry files MUST define date partitioning.
- **Partition Column**: Use pseudo-column `_PARTITIONDATE` or a validated root-level `DATE`/`TIMESTAMP` column.
- **Partition Expiration**: External partitions or staging tables must enforce a maximum retention window of `730` days (2 years) unless exempted by enterprise data tier policies.

### 3. Metadata & Audit Column Injection
Every inferred schema must be augmented with enterprise lineage and audit attributes:
- `_ingested_at`: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP()` populated with current ingestion timestamp.
- `_source_file_uri`: `STRING` referencing the source GCS blob path.
- **Lineage**: Every `CREATE` statement must include a description identifying the source GCS path.

---

## Output Contract (Governance Policy Decision)

When consulted alongside schema inference, this skill outputs governance parameters to be merged into the final Schema Decision Object:

```json
{
  "governance": {
    "table_prefix": "ext_",
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
