#!/bin/bash
# Exit immediately if any command fails
set -e

# Strict configuration parameters
FUNCTION_NAME="heart-disease-risk-assessment"
REGION="us-east1"

# Ensure environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "ERROR: GCP_PROJECT_ID is not set. Please set it in your environment."
    exit 1
fi

echo "=== Workspace Environment Validation ==="
ACTIVE_ACCOUNT=$(gcloud config get-value account 2>/dev/null || echo "Not Logged In")
ACTIVE_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "None")

echo "Active Account: $ACTIVE_ACCOUNT"
echo "Target Project ID: $GCP_PROJECT_ID"
echo "Active gcloud Project: $ACTIVE_PROJECT"
echo "========================================"

read -p "Are you sure you want to DELETE the Cloud Function '$FUNCTION_NAME' in project '$GCP_PROJECT_ID'? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cleanup aborted by user."
    exit 0
fi

echo "=== Tearing Down Google Cloud Function (Gen2) ==="
if gcloud functions describe "$FUNCTION_NAME" --gen2 --region="$REGION" --project="$GCP_PROJECT_ID" &>/dev/null; then
    gcloud functions delete "$FUNCTION_NAME" \
        --gen2 \
        --region="$REGION" \
        --project="$GCP_PROJECT_ID" \
        --quiet
    echo "Cloud Function '$FUNCTION_NAME' deleted successfully."
else
    echo "Cloud Function '$FUNCTION_NAME' does not exist."
fi

echo "=== API Cleanup Complete ==="
