# DevOps & Deployment Guide: Heart Disease Risk Agent

This document outlines the architecture, deployment sequence, and configuration process to provision and deploy the Heart Disease Risk Agent application to Google Cloud Platform (GCP).

All execution commands are encapsulated within dedicated bash scripts to automate resource setup, security bindings, and deployments.

---

## 1. Environment & Architecture Overview

The system consists of the following components:
*   **Frontend UI & Server Proxy** ([app/](heart-disease-risk-agent/app)): A React frontend served by a Node.js Express proxy. It is protected by Google Identity-Aware Proxy (IAP) to enforce user authentication.
*   **Downstream ML & Inference API** ([api/](heart-disease-risk-agent/api)): A Gen 2 Cloud Function running the XGBoost model and FastMCP services, accessed securely by the frontend service account.

---

## 2. Setup & Deployment Sequence

Follow this sequence of bash scripts to provision and deploy the application.

### Step A: Provision Service Account & Enable APIs
Initialize your target project environment, enable necessary APIs (Cloud Build, Cloud Run, Cloud Functions, and IAP), and configure the service account used by the server proxy to securely communicate with the downstream APIs.
*   **Script to run**: `bash setup-sa.sh` inside the `app/` directory.
*   **Script reference**: [app/setup-sa.sh](heart-disease-risk-agent/app/setup-sa.sh)

### Step B: Configure OAuth Credentials & Identity-Aware Proxy
Establish the OAuth Consent Screen (external testing user configuration) and generate Web application client credentials in the Google Auth Platform. This script prompts you with Console navigation instructions, waits for you to save your Client ID and Client Secret in `app/iap-oauth.yaml`, and automatically applies the IAP settings and verifies the redirect configuration.
*   **Script to run**: `bash setup-oauth.sh` inside the `app/` directory.
*   **Script reference**: [app/setup-oauth.sh](heart-disease-risk-agent/app/setup-oauth.sh)

### Step C: Deploy Downstream ML & MCP Inference API
Deploy the Python XGBoost risk inference engine and FastMCP tool service privately to Cloud Functions.
*   **Script to run**: `bash deploy.sh` inside the `api/` directory.
*   **Script reference**: [api/deploy.sh](heart-disease-risk-agent/api/deploy.sh)

### Step D: Deploy Frontend Web App & Server Proxy
Compile the React build assets and deploy the containerized Node.js application to Cloud Run with Identity-Aware Proxy (IAP) protection enabled. The script automatically sets up the IAM policy bindings for IAP access.
*   **Script to run**: `bash deploy.sh` inside the `app/` directory.
*   **Script reference**: [app/deploy.sh](heart-disease-risk-agent/app/deploy.sh)

---

## 3. Post-Deployment User Access Management

The `app/deploy.sh` script automatically grants the active deploying user access to the IAP-secured application. 

For adding or listing users authorized to access the application after deployment, refer to the comments and helper output generated at the end of the [app/deploy.sh](heart-disease-risk-agent/app/deploy.sh) script run.

---

## 4. Teardown & Resource Cleanup

To remove all deployed resources, custom IAM configurations, and service accounts from your Google Cloud project, run the cleanup scripts in reverse order:

1.  **Downstream API Teardown**: Run `bash cleanup.sh` inside the `api/` directory.
    *   **Script reference**: [api/cleanup.sh](heart-disease-risk-agent/api/cleanup.sh)
2.  **Web App & IAM Teardown**: Run `bash cleanup.sh` inside the `app/` directory.
    *   **Script reference**: [app/cleanup.sh](heart-disease-risk-agent/app/cleanup.sh)
