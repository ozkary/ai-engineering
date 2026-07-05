# Specification: Frontend App DevOps & Managed GCP Deployment
## Project: Agent for Good - Private Container Pipeline Automation

### Objective
To outline the serverless compilation lifecycle and automated shell script requirements for containerizing and staging the application on Google Cloud Run. The pipeline compiles assets into a deployment script, injects structural runtime variables, and provides a resource verification gate before execution.

---

### 1. Environment Variable & Script Requirements
The deployment framework must define and reference the following configuration parameters at the top of the script workspace:
* **`SERVICE_NAME`**: Set to `"heart-disease-risk-ui"`
* **`REGION`**: Set to `"us-east1"`
* **`GCP_PROJECT_ID`**: Read dynamically from the local machine's terminal environment (e.g., `$GCP_PROJECT_ID`). It must never be hardcoded.
* **`SERVICE_ACCOUNT`**: Read dynamically from the local machine's terminal environment (e.g., `$SERVICE_ACCOUNT`) to explicitly bind the required runtime identity profile.
* **Directory Bounds**: Execution tracking paths for local distribution boundaries (`DIST_DIR`).

---

### 2. Step-by-Step Shell Pipeline Lifecycle (`app/deploy.sh`)

The script framework must execute the following logical blocks sequentially:

#### Phase 1: Environment Pre-flight Validation
* Intercept runtime execution and assert that the required dynamic terminal environment variables (`GCP_PROJECT_ID` and `SERVICE_ACCOUNT`) are populated.
* If any environment strings are missing, fail-fast with a descriptive error message and terminate the process before running local build tasks.

#### Phase 2: Resource Matrix Review & Confirmation Gate
* Print a standardized text-block readout to the console detailing all target runtime parameters, project scopes, scaling constraints, and access levels.
* Enforce an interactive confirmation prompt (`read`) requiring an explicit affirmative operator key-press (`y/N`) to proceed with compilation or cloud deployment changes.

#### Phase 3: Workspace Target Reset
* Completely purge and remove (`rm`) any existing production distribution folders (`/dist` or `/build`) inside the local directory to guarantee no stale or residual assets remain.

#### Phase 4: Production Compilation Target Bundling
* Trigger the application's native framework production build tool command (e.g., `npm run build`) to generate the optimized, static production web asset layers.

#### Phase 5: Containerized Serverless Deployment Execution
Invoke the formal `gcloud run deploy` workflow targeting the active source directory with the following explicit infrastructure rules:
* Force the deployment code source boundary to look directly at the active path (`--source .`).
* Inject the functional environment configuration parameters (`SERVICE_NAME`, `REGION`, `GCP_PROJECT_ID`).
* **Identity Binding:** Assign the designated identity profile by attaching the `--service-account="$SERVICE_ACCOUNT"` flag at execution time.
* **Access Level Guardrail:** Turn off public internet entry points completely by specifying the strict `--no-allow-unauthenticated` flag.
* **Scale-to-Zero Budget Protection:** Enforce explicit resource boundaries by capping limits precisely (such as setting `--min-instances=0` and `--max-instances=2`) to guarantee true zero-cost idle states and eliminate budget bleed.
