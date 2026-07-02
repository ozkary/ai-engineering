# Deployment, Verification, & Integration Roadmap
## Project: Agent for Good - Heart Disease Risk Agent UI

Follow this sequence to provision resources, containerize, deploy, and integrate the application layers, including the downstream Analyst Agent and final reporting UI.

---

### Step 1: Export Environment Configuration
Open your terminal in the `app/` workspace directory and run the export commands to define the runtime variables:

```bash
export GCP_PROJECT_ID="YOUR_GCP_PROJECT_ID"
export SERVICE_ACCOUNT="heart-disease-risk-ui-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com"
```

---

### Step 2: Run the IAM & IAP Setup Script
Execute the service principal setup script to provision the Cloud Run service identity, enable the IAP APIs, and authorize the default owner:

```bash
./setup-sa.sh
```

**What it does:**
1. Verifies that environment parameters are active.
2. Creates the `heart-disease-risk-ui-sa` service account if it does not exist.
3. Grants `roles/run.invoker` to the service account (allowing the server proxy to execute downstream Python APIs).
4. Enables the Google Identity-Aware Proxy API (`iap.googleapis.com`).
5. Adds `ozkary@gmail.com` to the IAP access list (`roles/iap.httpsResourceAccessor`).

---

### Step 3: Run the Cloud Run Deployment Script
Execute the main deployment script. It compiles the React UI assets, builds the multi-stage Docker container locally, and stages the deployment to Cloud Run:

```bash
./deploy.sh
```

**What it does:**
1. Audits pre-flight environment requirements.
2. Prompts you with a Resource Matrix confirmation prompt (`y/N`).
3. Resets/purges any stale `dist/` folders.
4. Triggers `npm run build` to package static React/Vite assets.
5. Deploys to Cloud Run using the `Dockerfile` with scale-to-zero settings, strict identity configuration, private network access, and the `--iap` direct gateway flag enabled.

---

### Step 4: Verification & Acceptance Tests

#### Test 1: Anonymous Access (Expected: Blocked)
1. Get the URL of your new Cloud Run service from the CLI output.
2. Open an Incognito/Private browser window and navigate to the service URL.
3. **Expected result**: You should be intercepted by a Google Accounts Sign-In screen (or receive an HTTP `401 Unauthorized` / `403 Forbidden` response if not signed in with an authorized email). The raw app should *never* render.

#### Test 2: Authenticated Access (Expected: Allowed)
1. Sign in using the authorized account (`ozkary@gmail.com`).
2. **Expected result**: The conversational Heart Disease Risk UI should load successfully.

---

### Step 5: Full Application Integration & Analyst Agent Setup

To transition from the UI-only layout to the complete multi-agent pipeline:

#### 1. Update UI to Dispatch Actual Risk Request
* Update the React frontend (`src/App.tsx`) to dispatch requests to the proxy server endpoint (`/api/evaluate-risk`) with the populated 16 clinical/lifestyle criteria, replacing any static mock data.

#### 2. Integrate the Proxy Server with the Downstream Cloud Function
* Set the `INFERENCE_API_URL` environment variable inside the Cloud Run environment. This directs the Express proxy (`server.ts`) to request identity tokens matching the downstream Python Function URL and securely forward the payload.

#### 3. Perform Integration Testing
* Run integration tests using your user account to confirm:
  * React UI captures inputs and triggers the proxy API.
  * Express server generates a signed Google IAM OIDC token on behalf of the service account.
  * The Cloud Function accepts the token, processes the lifestyle vector, and returns classification probabilities.

#### 4. Create the Analyst Agent (ADK Agent)
* Build a specialized Python Agent using the **Google Agent Development Kit (ADK)** that:
  * Subscribes to the UI state change hooks or reads the output dataset.
  * Feeds the calculated risk percentages and lifestyle variables to a Large Language Model (LLM).
  * Performs analysis (e.g., identifies risk triggers, drafts custom lifestyle recommendations, and highlights clinical consultation indicators).

#### 5. Build the Analysis Report UI Page & Restart Navigation
* Implement a new reporting interface page in the React app to:
  * Render the structured LLM analysis output (Markdown text, key risk factor lists, advice cards).
  * Provide a clear navigation action button ("Start New Assessment") to reset all state machine inputs and start a new conversational interview process.
