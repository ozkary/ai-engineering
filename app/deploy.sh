#!/bin/bash
set -e

# ==========================================
# 1. Environment Variable & Script Requirements
# ==========================================
SERVICE_NAME="heart-disease-risk-ui"
REGION="us-east1"
DIST_DIR="dist"

# ==========================================
# Phase 1: Environment Pre-flight Validation
# ==========================================
echo "=== Phase 1: Pre-flight Validation ==="
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "ERROR: GCP_PROJECT_ID environment variable is not set."
    exit 1
fi

if [ -z "$SERVICE_ACCOUNT" ]; then
    echo "ERROR: SERVICE_ACCOUNT environment variable is not set."
    exit 1
fi

if [ -z "$INFERENCE_API_URL" ]; then
    echo "ERROR: INFERENCE_API_URL environment variable is not set."
    exit 1
fi

# ==========================================
# Phase 2: Resource Matrix Review & Confirmation Gate
# ==========================================
echo "=== Phase 2: Resource Review ==="
echo "Target Service Name: $SERVICE_NAME"
echo "Target Region:       $REGION"
echo "GCP Project ID:      $GCP_PROJECT_ID"
echo "Service Account:     $SERVICE_ACCOUNT"
echo "Inference API URL:   $INFERENCE_API_URL"
echo "Min/Max Instances:   0 / 2 (Scale-to-Zero Enabled)"
echo "Access Policy:       Private (--no-allow-unauthenticated)"
echo "================================="
read -p "Do you want to proceed with the build and deployment? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Deployment aborted by user."
    exit 0
fi

# ==========================================
# Phase 3: Workspace Target Reset
# ==========================================
echo "=== Phase 3: Workspace Target Reset ==="
if [ -d "$DIST_DIR" ]; then
    echo "Purging old production distribution folder: /$DIST_DIR"
    rm -rf "$DIST_DIR"
fi

# ==========================================
# Phase 4: Production Compilation Target Bundling
# ==========================================
echo "=== Phase 4: Production Compilation ==="
npm run build

# ==========================================
# Phase 5: Containerized Serverless Deployment Execution
# ==========================================
echo "=== Phase 5: Google Cloud Run Deployment ==="
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --project "$GCP_PROJECT_ID" \
  --region "$REGION" \
  --service-account "$SERVICE_ACCOUNT" \
  --no-allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars INFERENCE_API_URL="$INFERENCE_API_URL",GCP_PROJECT_ID="$GCP_PROJECT_ID",GCP_LOCATION="$REGION" \
  --iap