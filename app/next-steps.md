# Deployment, Verification, & Integration Roadmap (Missing Steps)
## Project: Agent for Good - Heart Disease Risk Agent UI

Follow this sequence to set up the environment variables, execute the deployment script, and verify the fully integrated state-graph agent application on Google Cloud.

---

### Step 1: Export Required Environment Configuration
Open your terminal in the `app/` workspace directory and run the export commands to define all necessary runtime variables (including the active Gemini credentials and Inference endpoint):

```bash
export GCP_PROJECT_ID="YOUR_GCP_PROJECT_ID"
export SERVICE_ACCOUNT="heart-disease-risk-ui-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com"
export INFERENCE_API_URL="YOUR_DOWNSTREAM_INFERENCE_API_URL"
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

---

### Step 2: Run the Cloud Run Deployment Script
Execute the deployment script. It compiles the production React assets, checks your variables, masks and displays them for confirmation, and deploys the Node.js ADK-based container to Google Cloud Run:

```bash
./deploy.sh
```

**What it verifies on run:**
1. Validates that `GCP_PROJECT_ID`, `SERVICE_ACCOUNT`, `INFERENCE_API_URL`, and `GEMINI_API_KEY` are all set.
2. Masks the `GEMINI_API_KEY` and outputs all configs to the console for review.
3. Prompts for verification confirmation (`y/N`).
4. Compiles React assets, packages dependencies, and deploys the container with scale-to-zero settings, IAP protection, and environment variable configuration.

---

### Step 3: Verification & Integration Tests

#### Test 1: Anonymous Access (Expected: Blocked)
1. Get the URL of your new Cloud Run service from the CLI output.
2. Open an Incognito/Private browser window and navigate to the service URL.
3. **Expected result**: You should be intercepted by a Google Accounts Sign-In screen (IAP Gateway). The app should *never* render.

#### Test 2: Authenticated Assessment Analysis (Expected: Allowed & Functional)
1. Sign in using the authorized account (`ozkary@gmail.com`).
2. Fill out the conversational assessment criteria.
3. Submit the profile on the final screen.
4. **Expected result**: 
   * The client proxy triggers the server-side ADK `HeartRiskWorkflowAgent` state-graph.
   * The backend resolves the OIDC credentials, calls the downstream MCP function tool, and invokes the Gemini model.
   * The UI successfully transitions from the **Processing** loading spinner to render the final **Risk Category**, **Probability Score**, and the custom **Clinical Analyst & Health Coach Review** text.
