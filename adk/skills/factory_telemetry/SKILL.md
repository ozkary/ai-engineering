---
name: factory_telemetry
version: "1.0.0"
spec_signature: "HMAC-SHA256"
bounded_context: "eyepiece_manufacturing_quality"
allowed_tools:
  - tools/gcs/read_file_sample
---

# Factory Telemetry & AR Eyepiece Metrology Skill

## Purpose & Scope
This skill equips the agent with domain intelligence for Augmented Reality (AR) optical eyepiece manufacturing, metrology sensor telemetry, and automated quality control inspection feeds (inspired by optical metrology platforms).

> [!IMPORTANT]
> **Boundary Rule**: Skills teach domain judgment and rules. This skill NEVER generates raw SQL DDL, Python execution scripts, or direct warehouse mutations. It strictly validates and emits a structured JSON Schema Proposal Object.

---

## Domain Ubiquitous Language & Measurement Standards

Each inspection record captures high-precision physical and optical attributes of an AR eyepiece sample:

| Metric / Dimension | Type | Nominal Value | Engineering Description |
| :--- | :---: | :---: | :--- |
| **`Sample_ID`** | `INT64` | `1, 2, 3...` | Sequential workpiece identifier per manufacturing batch. |
| **`Timestamp`** | `TIMESTAMP` | ISO-8601 | Inspection timestamp captured at sensor station exit. |
| **`Focal_Length`** | `FLOAT64` | $50.0 \pm 1.5$ mm | Effective optical focal length of the eyepiece lens. |
| **`Curvature`** | `FLOAT64` | $2.5 \pm 0.15$ mm | Radius of surface curvature measured by laser interferometer. |
| **`Angle`** | `FLOAT64` | $45.0 \pm 0.6^\circ$ | Prismatic optical alignment angle. |
| **`Clarity`** | `FLOAT64` | $9.0$ (Score $0-10$) | Optical transparency and modulation transfer function (MTF) score. |
| **`Distortion`** | `FLOAT64` | $1.0$ (Score $0-10$) | Radial optical aberration distortion index. |
| **`Durability`** | `FLOAT64` | $8.0$ (Score $0-10$) | Scratch-resistance and coating adhesion index. |

---

## Standard Operating Procedure (SOP)

### 1. Header & Measurement Inspection
- Read the sample payload using `tools/gcs/read_file_sample`.
- Verify delimiter (comma `,` or tab `\t`) and ensure header contains optical metrology columns.
- Sanitize header names to canonical snake_case:
  - `Sample_ID` $\rightarrow$ `sample_id`
  - `Timestamp` $\rightarrow$ `reading_timestamp`
  - `Focal_Length` $\rightarrow$ `focal_length`
  - `Curvature` $\rightarrow$ `curvature`
  - `Angle` $\rightarrow$ `alignment_angle`
  - `Clarity` $\rightarrow$ `clarity_score`
  - `Distortion` $\rightarrow$ `distortion_score`
  - `Durability` $\rightarrow$ `durability_score`

### 2. Semantic Type Mapping
- All physical measurements (`Focal_Length`, `Curvature`, `Angle`) and quality scores $\rightarrow$ `FLOAT64` (in BigQuery) or `FLOAT` (in Snowflake).
- `Sample_ID` $\rightarrow$ `INT64` (or `INT`).
- `Timestamp` $\rightarrow$ `TIMESTAMP`.

### 3. Outlier & Anomaly Detection
- Compute bounds against 3-sigma Upper/Lower Control Limits (`UCL` / `LCL`):
  - Flag sample if `Clarity` $< 7.0$ (Critical defect).
  - Flag sample if `Distortion` $> 1.3$ (Optical aberration failure).
  - Flag sample if `Curvature` deviates by $> 0.15$ mm from nominal $2.5$ mm.

---

## Output Contract (Schema Proposal Object)

When invoked on an eyepiece telemetry payload, this skill emits strictly a valid JSON proposal:

```json
{
  "domain": "factory_telemetry",
  "subdomain": "ar_eyepiece_inspection",
  "version": "1.0.0",
  "format": "CSV",
  "delimiter": ",",
  "skip_leading_rows": 1,
  "columns": [
    {"name": "sample_id", "type": "INT64", "mode": "REQUIRED", "description": "Unique workpiece serial identifier"},
    {"name": "reading_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Inspection metrology timestamp"},
    {"name": "focal_length", "type": "FLOAT64", "mode": "REQUIRED", "description": "Lens focal length in mm (nominal 50.0)"},
    {"name": "curvature", "type": "FLOAT64", "mode": "REQUIRED", "description": "Interferometer lens curvature in mm (nominal 2.5)"},
    {"name": "alignment_angle", "type": "FLOAT64", "mode": "REQUIRED", "description": "Prismatic optical alignment angle in degrees"},
    {"name": "clarity_score", "type": "FLOAT64", "mode": "NULLABLE", "description": "Optical clarity score (0-10, nominal >= 8.0)"},
    {"name": "distortion_score", "type": "FLOAT64", "mode": "NULLABLE", "description": "Optical distortion score (0-10, nominal <= 1.3)"},
    {"name": "durability_score", "type": "FLOAT64", "mode": "NULLABLE", "description": "Coating durability score (0-10, nominal >= 7.0)"}
  ]
}
```
