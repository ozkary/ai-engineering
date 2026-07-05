# Deployment, Verification, & Integration Roadmap (Missing Steps)
## Project: Agent for Good - Heart Disease Risk Agent UI

Follow this sequence to set up the environment variables, execute the deployment script, and verify the fully integrated state-graph agent application on Google Cloud.

---

### Step 1: Initialize OAuth Consent Screen (One-Time Console Requirement)
Since the project is using a personal account outside of a Google Workspace Organization, the first-time OAuth Consent Screen setup must be completed in the Cloud Console:
1. Go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** and click **Create**.
3. Fill in required App name (`Heart Disease Risk UI`), support email, and developer contact email, and save.
4. Add your email under **Test Users** and save.

---

### Step 2: Configure IAP Custom OAuth Credentials
Because IAP cannot auto-generate client credentials on non-organization projects, you must link them manually:
1. Go to **APIs & Services** > **Credentials**.
2. Click **+ Create Credentials** > **OAuth client ID** and select **Web application**.
3. Under **Authorized redirect URIs**, add:
   `https://iap.googleapis.com/v1/oauth/clientIds/YOUR_CLIENT_ID:handleRedirect`
4. Copy the generated Client ID and Client Secret.
5. Create a local `iap-oauth.yaml` file:
   ```yaml
   accessSettings:
     oauthSettings:
       clientId: "YOUR_CLIENT_ID"
       clientSecret: "YOUR_CLIENT_SECRET"
   ```
6. Bind the credentials to your service:
   ```bash
   gcloud iap settings set iap-oauth.yaml \
       --project=ozkary-de-101 \
       --resource-type=cloud-run \
       --region=us-east1 \
       --service=heart-disease-risk-ui
   ```

---

### Step 3: Run the Cloud Run Deployment Script
Execute the deployment script to compile React assets and deploy the Node.js container to Cloud Run with native IAP enabled:
```bash
cd app
bash deploy.sh
```

---

### Step 4: Downstream API Deployment & Healthcheck Troubleshooting
When deploying the Python API (`api/` Cloud Function Gen 2), you may encounter the following container healthcheck timeout error:
```
ERROR: (gcloud.functions.deploy) OperationError: code=3, message=Could not create or update Cloud Run service heart-disease-risk-assessment, Container Healthcheck failed. Revision 'heart-disease-risk-assessment-00001-rez' is not ready and cannot serve traffic. The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout.
```

#### Diagnostic & Resolution Path:
* **Root Cause**: The Gen 2 Cloud Function runtime utilizes Google's `functions-framework` internally. By default, the framework expects the designated entry point (`predict_risk_main`) to be a standard Python function (or standard WSGI callable). If the module fails to import due to package version errors, or if the runtime fails to parse `a2wsgi.ASGIMiddleware` directly, the container fails to start and listen on port `8080`.
* **Fix**: Ensure that the functions framework can correctly load and initialize `api/main.py`. Test the module imports locally using:
  ```bash
  cd api
  functions-framework --target=predict_risk_main --port=8080
  ```
  Look for hidden `ImportError` exceptions (e.g. `AttributeError: module 'pkg_resources' has no attribute '_find_adapter'`) and resolve any python package mismatch in `api/requirements.txt` before redeploying.

---

### Step 5: Verification & Integration Tests

#### Test 1: Anonymous Access (Expected: Blocked)
1. Get the URL of your new Cloud Run service from the CLI output.
2. Open an Incognito/Private browser window and navigate to the service URL.
3. **Expected result**: You should be intercepted by a Google Accounts Sign-In screen (IAP Gateway). The app should *never* render.

#### Test 2: Authenticated Assessment Analysis (Expected: Allowed & Functional)
1. Sign in using the authorized account (`ozkary@gmail.com`).
2. Fill out the conversational assessment criteria.
3. Submit the profile on the final screen.
4. **Expected result**: The client proxy triggers the server-side ADK workflow, which queries the private Python ML function, calls the Gemini model, and displays the risk statistics and clinical narrative.

---

> [!NOTE]
> **Developer Feedback Note:** 
> *Antigravity for DevOps has a poor score. It has several incomplete steps.*
