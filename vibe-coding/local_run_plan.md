# Plan: Running Heart Disease Risk Agent Locally

This plan details the steps required to set up and run both the frontend/backend proxy server (`app`) and the downstream classification service (`api` Cloud Function) locally.

---

## 1. Environment Configuration (`.env`)

The Express server loads configurations from system environment variables, falling back to values declared in `app/.env` (via `import "dotenv/config"` at the top of `app/server.ts`).

### Local `.env` Configuration
The following file is created at `app/.env`:
```env
PORT=3001
GCP_PROJECT_ID=ozkary-de-101
SERVICE_ACCOUNT=heart-disease-risk-ui-sa@ozkary-de-101.iam.gserviceaccount.com
INFERENCE_API_URL=http://localhost:8080/sse
GEMINI_MODEL=gemini-2.5-flash
RISK_REVIEW_PROMPT_PATH=./server/prompts/risk-review.md
```

> [!NOTE]
> - **Sensitive Variables**: The `GEMINI_API_KEY` is omitted from the `.env` file because it is loaded directly from your system environment locally (and passed via GCP environment variables in production).
> - **Precedence**: System environment variables (including Cloud Run configuration values) always take precedence over values declared in `.env`. The `INFERENCE_API_URL` set locally will not overwrite the production endpoint when deployed.

### Prompts Directory
The risk assessment system reads the LLM prompt instructions dynamically from the file path specified in `RISK_REVIEW_PROMPT_PATH`. 
- File location: `app/server/prompts/risk-review.md`

---

## 2. Starting the Python API (Cloud Function) Locally

The API is structured as a Starlette app (`app`) converted to a WSGI app (`predict_risk_main` via `a2wsgi`). We can run this ASGI application locally on port `8080` (matching the `INFERENCE_API_URL` above).

### Option A: Using the Makefile (Recommended)
You can start the Python API directly from the `api` folder using `make dev`:
```bash
cd api
make dev
```

### Option B: Using `uvicorn` manually
```bash
cd api
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

### Option C: Using `functions-framework`
```bash
cd api
source .venv/bin/activate
functions-framework --target=predict_risk_main --port=8080
```

---

## 3. Starting the Node.js Server & Frontend Locally

There are two ways to run the web application locally without CORS issues. Both options force Node.js v20 automatically via NVM.

### Option A: Using Vite Dev Server (With Hot-Reload / HMR) - Recommended
Vite is already configured to proxy `/api` requests to the Express backend (running on port `3001`) in [vite.config.ts](file:///home/ozkary/workspace/agy/heart-disease-risk-agent/app/vite.config.ts#L8-L15).

1. Start the Express backend proxy in one terminal:
   ```bash
   cd app
   make dev-server
   ```
2. Start the Vite dev server in a separate terminal:
   ```bash
   cd app
   make dev-app
   ```
3. Open your browser to `http://localhost:5173`. Any call to `/api/evaluate-risk` is automatically proxied to port `3001` under the hood.

### Option B: Build and Run directly from the Express Server (Same Port)
If you prefer not to run a separate dev server, you can compile the React bundle so that the Express server serves both the static files and the API endpoints on the same port:

1. Build the production React files:
   ```bash
   cd app
   make build
   ```
2. Start the server:
   ```bash
   make dev-server
   ```
3. Access the application directly at `http://localhost:3001`. Since everything is served from port `3001`, there is no cross-origin communication.

---

## 4. Verification Check
- The client app makes requests to `/api/evaluate-risk`.
- The Express server (port `3001`) processes the ADK workflow and routes the MCP/SSE transport queries to the Python API running at `http://localhost:8080/sse`.
