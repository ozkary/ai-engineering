### Environment Variable Requirements
The deployment automation system must define and reference the following strict configuration parameters:
* **`FUNCTION_NAME`**: Set to `"heart-disease-risk-assessment"`
* **`ENTRY_POINT`**: Set to `"predict_risk_main"`
* **`REGION`**: Set to `"us-east1"`
* **GCP_PROJECT_ID:** Read dynamically from your machine's environment (e.g., $GCP_PROJECT_ID) to designate the targeted cloud deployment infrastructure canvas.
* **`FIREBASE_PROJECT_ID`**: Must be read dynamically from the local machine's shell execution environment (e.g., `$FIREBASE_PROJECT_ID`). It is never hardcoded in the deployment scripts.

---

#### 4. Google Cloud Functions Gen2 Deployment Execution
Invoke the formal `gcloud functions deploy` workflow targeting the compiled distribution workspace with the following explicit runtime rules:
* Execute under the **Gen2** cloud architecture layer.
* Force the deployment code source boundary to look directly at the active path (`--source=.`).
* Inject the functional environment configuration parameters (`FUNCTION_NAME`, `ENTRY_POINT`, `REGION`).
* Explicit Project Isolation: Pass the target GCP project ID by attaching the `--project="$GCP_PROJECT_ID"` flag at runtime execution. This ensures deployment goes to the correct cloud canvas regardless of the active gcloud CLI profile state.
* Pass the dynamically resolved shell variable directly into the runtime environment configuration table using the `--set-env-vars FIREBASE_PROJECT_ID="$FIREBASE_PROJECT_ID"` flag. This exposes the correct project identification string safely to the Python code layer during token verification.
* Implement serverless boundary safety limits (such as capping `--max-instances=2`) to control processing overhead and compute costs.