# API Solution Blueprint 

## Project: Agent for Good - Heart Disease Risk Agent

### Role & Objective

The objective is to build a secure, lightweight Python (ver 3.12) API that assesses heart disease risk. The service accepts an incoming request containing user metrics, runs them through a pre-built machine learning model (hd_xgboost_model.pkl) and a dictionary vectorizer (hd_dictvectorizer.pkl), and returns a stratified risk category.

### Project Domain
- Request Ingestion: Process arriving HTTP POST payloads containing 16 specific health and lifestyle metrics.
- Identity Verification: Authenticate requests by validating a Firebase Auth token passed via the request header before running the inference pipeline.
- Inference Pipeline: Transform JSON data vectors using the pre-built vectorizer and execute the XGBoost array to score and categorize the patient profile.
  
### Workspace & Directory Layout

```
/heart-disease-risk-workspace
  └── /api
       ├── main.py               # Root Cloud Function Entry Point & Token Gatekeeper
       ├── requirements.txt      # Python Package Dependencies
       ├── deploy.sh             # Build Compilation & Cleanup Shell Pipeline
       └── /predict              # Encapsulated Machine Learning Core Package
            ├── __init__.py      # Module exports and package initializers
            ├── main.py          # Data transformation, vectorization, and scoring logic
            ├── hd_xgboost_model.pkl       # Serialized trained model weights array
            └── hd_dictvectorizer.pkl      # Serialized DictVectorizer data structure
```

### Specification Matrix

- **`specs/specs-risk-evaluation.md`** (ML Engine & Validation): Controls the internal /predict module logic. Governs pickle loading, structural Pydantic validation parameters, data vector transformations, and the probability score classification brackets (none, low, medium, high).

- **`specs/specs-devops.md`** (Automation & Deployment): Outlines the DevOps process. Specifies environmental configurations (FUNCTION_NAME, ENTRY_POINT, REGION), the step-by-step shell build isolation pipeline (/dist purge and compile), and the gcloud Gen2 script layout powered by local shell variables ($FIREBASE_PROJECT_ID).

- **`specs/specs-mcp-server.md`** (MCP Server Integration): Establishes the Model Context Protocol wrapper configuration. Governs Server-Sent Events (SSE) HTTP transport route bindings (`/sse`) and registers our underlying machine learning model execution code as an discoverable tool (`evaluate_heart_risk`) for Google ADK agents.