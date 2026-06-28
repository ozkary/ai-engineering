#!/bin/bash
# Exit immediately if any command fails
set -e

# Strict configuration parameters
FUNCTION_NAME="heart-disease-risk-assessment"
ENTRY_POINT="predict_risk_main"
REGION="us-east1"

# Ensure environment variables are set
if [ -z "$FIREBASE_PROJECT_ID" ]; then
    echo "ERROR: FIREBASE_PROJECT_ID is not set. Please set it in your environment."
    exit 1
fi

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "ERROR: GCP_PROJECT_ID is not set. Please set it in your environment."
    exit 1
fi

echo "=== Build & Isolation Pipeline ==="

# Purge existing dist workspace
DIST_DIR="./dist"
if [ -d "$DIST_DIR" ]; then
    echo "Purging old distribution directory..."
    rm -rf "$DIST_DIR"
fi

# Compile / prepare the distribution workspace
echo "Creating isolated distribution workspace..."
mkdir -p "$DIST_DIR"

echo "Copying source files and dependencies..."
cp -r main.py requirements.txt predict "$DIST_DIR/"

# Change to dist workspace to run the deployment
cd "$DIST_DIR"

echo "=== Deploying Google Cloud Function (Gen2) ==="
gcloud functions deploy "$FUNCTION_NAME" \
    --gen2 \
    --region="$REGION" \
    --runtime="python312" \
    --entry-point="$ENTRY_POINT" \
    --source=. \
    --project="$GCP_PROJECT_ID" \
    --set-env-vars FIREBASE_PROJECT_ID="$FIREBASE_PROJECT_ID" \
    --max-instances=2 \
    --trigger-http \
    --allow-unauthenticated

echo "=== Deployment Pipeline Successfully Completed ==="
