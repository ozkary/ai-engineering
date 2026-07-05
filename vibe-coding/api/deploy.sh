#!/bin/bash
# Exit immediately if any command fails
set -e

# Strict configuration parameters
FUNCTION_NAME="heart-disease-risk-assessment"
ENTRY_POINT="predict_risk_main"
REGION="us-east1"

# ==========================================
# Phase 1: gcloud User Account Verification
# ==========================================
echo "=== Phase 1: Verify Active User Account ==="
ACTIVE_ACCOUNT=$(gcloud config get-value account 2>/dev/null || echo "")

if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "No active gcloud login account detected."
    read -p "Enter the gcloud account (email) to use: " ACTIVE_ACCOUNT
    if [ -n "$ACTIVE_ACCOUNT" ]; then
        gcloud config set account "$ACTIVE_ACCOUNT"
    else
        echo "ERROR: Active gcloud account email is required to proceed."
        exit 1
    fi
else
    echo "Detected Active Account: $ACTIVE_ACCOUNT"
    read -p "Is '$ACTIVE_ACCOUNT' the correct gcloud account you want to use? (y/N): " confirm_user
    if [[ ! "$confirm_user" =~ ^[Yy]$ ]]; then
        read -p "Enter the gcloud account (email) to use: " ACTIVE_ACCOUNT
        if [ -n "$ACTIVE_ACCOUNT" ]; then
            gcloud config set account "$ACTIVE_ACCOUNT"
        else
            echo "ERROR: Active gcloud account email is required to proceed."
            exit 1
        fi
    fi
fi

# ==========================================
# Phase 2: Project ID Resolution & Verification
# ==========================================
echo ""
echo "=== Phase 2: Verify Target GCP Project ==="
DEFAULT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -z "$GCP_PROJECT_ID" ]; then
    if [ -n "$DEFAULT_PROJECT" ]; then
        GCP_PROJECT_ID="$DEFAULT_PROJECT"
    fi
fi

if [ -n "$GCP_PROJECT_ID" ]; then
    echo "Target Project ID (Resolved): $GCP_PROJECT_ID"
    read -p "Is '$GCP_PROJECT_ID' the correct GCP project ID you want to use? (y/N): " confirm_proj
    if [[ ! "$confirm_proj" =~ ^[Yy]$ ]]; then
        read -p "Enter the GCP project ID to use: " GCP_PROJECT_ID
        if [ -n "$GCP_PROJECT_ID" ]; then
            gcloud config set project "$GCP_PROJECT_ID"
        else
            echo "ERROR: Target GCP project ID is required to proceed."
            exit 1
        fi
    fi
else
    read -p "Enter the GCP project ID to use: " GCP_PROJECT_ID
    if [ -n "$GCP_PROJECT_ID" ]; then
        gcloud config set project "$GCP_PROJECT_ID"
    else
        echo "ERROR: Target GCP project ID is required to proceed."
        exit 1
    fi
fi

export GCP_PROJECT_ID

# Final Confirmation Review
echo ""
echo "=== Final Deployment Context Review ==="
echo "Target Project ID:              $GCP_PROJECT_ID"
echo "Target deployer Account:        $ACTIVE_ACCOUNT"
echo "======================================="
read -p "Proceed with deployment? (y/N): " confirm_final
if [[ ! "$confirm_final" =~ ^[Yy]$ ]]; then
    echo "Deployment aborted by user."
    exit 0
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
cp -r main.py requirements.txt Procfile predict "$DIST_DIR/"

# Change to dist workspace to run the deployment
cd "$DIST_DIR"

echo "=== Deploying to Google Cloud Run ==="
gcloud run deploy "$FUNCTION_NAME" \
    --source=. \
    --project="$GCP_PROJECT_ID" \
    --region="$REGION" \
    --max-instances=1 \
    --concurrency=80 \
    --cpu=1 \
    --memory=512Mi \
    --no-allow-unauthenticated \
    --port=8080 \
    --command="" \
    --args="" \
    --session-affinity





# Grant invoker permissions to the frontend service account on the Cloud Run service
echo "=== Granting Invoker Permissions to Frontend Service Account ==="
UI_SERVICE_ACCOUNT="heart-disease-risk-ui-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com"
gcloud run services add-iam-policy-binding "$FUNCTION_NAME" \
    --region="$REGION" \
    --member="serviceAccount:$UI_SERVICE_ACCOUNT" \
    --role="roles/run.invoker" \
    --project="$GCP_PROJECT_ID" \
    --quiet

echo "=== Deployment Pipeline Successfully Completed ==="
