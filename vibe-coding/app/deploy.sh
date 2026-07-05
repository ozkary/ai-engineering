#!/bin/bash
set -e

# ==========================================
# 1. Environment Variable & Script Requirements
# ==========================================
SERVICE_NAME="heart-disease-risk-ui"
REGION="us-east1"
DIST_DIR="dist"

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

# Set the default project member
export GCP_PROJECT_MEMBER="$ACTIVE_ACCOUNT"

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

# Dynamically compute target dependent variables
if [ -z "$SERVICE_ACCOUNT" ]; then
    SERVICE_ACCOUNT="$SERVICE_NAME-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com"
fi

if [ -z "$INFERENCE_API_URL" ]; then
    # Fetch direct Cloud Run URL for 2nd Gen functions to prevent OIDC audience mismatches
    API_RUN_URL=$(gcloud run services describe heart-disease-risk-assessment --region="$REGION" --project="$GCP_PROJECT_ID" --format="value(status.url)" 2>/dev/null || echo "")
    if [ -n "$API_RUN_URL" ]; then
        INFERENCE_API_URL="${API_RUN_URL}/sse"
    else
        INFERENCE_API_URL="https://$REGION-$GCP_PROJECT_ID.cloudfunctions.net/heart-disease-risk-assessment/sse"
    fi
fi

# ==========================================
# Phase 3: Resource Matrix Review & Confirmation Gate
# ==========================================
echo ""
echo "=== Phase 3: Resource Review ==="
echo "Target Service Name: $SERVICE_NAME"
echo "Target Region:       $REGION"
echo "GCP Project ID:      $GCP_PROJECT_ID"
echo "Service Account:     $SERVICE_ACCOUNT"
echo "Inference API URL:   $INFERENCE_API_URL"
echo "IAP Access Member:   $GCP_PROJECT_MEMBER"
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
make build

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

# Grant invoker permissions to IAP service agent
echo "Resolving project number for IAP service agent..."
PROJECT_NUMBER=$(gcloud projects describe "$GCP_PROJECT_ID" --format="value(projectNumber)" 2>/dev/null || echo "")
if [ -n "$PROJECT_NUMBER" ]; then
    echo "Granting run.invoker to IAP service agent..."
    gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
        --region="$REGION" \
        --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-iap.iam.gserviceaccount.com" \
        --role="roles/run.invoker" \
        --project="$GCP_PROJECT_ID" --quiet 2>/dev/null || echo "WARNING: Failed to bind invoker to IAP service agent. Verify IAP service agent exists."
fi

# Get and display the URL of the deployed application
APP_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$GCP_PROJECT_ID" --format="value(status.url)" 2>/dev/null || echo "Unknown")
echo ""
echo "================================================="
echo "Deployment Successful!"
echo "Public Application URL: $APP_URL"
echo "================================================="

# ==========================================
# Phase 6: Post-Deployment IAP Access Configuration
# ==========================================
echo ""
echo "TIP: To allow specific users to access the IAP-secured Cloud Run app, run:"
echo "  gcloud iap web add-iam-policy-binding \\"
echo "      --resource-type=\"cloud-run\" \\"
echo "      --service=\"$SERVICE_NAME\" \\"
echo "      --region=\"$REGION\" \\"
echo "      --member=\"user:$GCP_PROJECT_MEMBER\" \\"
echo "      --role=\"roles/iap.httpsResourceAccessor\" \\"
echo "      --project=\"$GCP_PROJECT_ID\""
echo "================================================="

echo "=== Phase 6: Post-Deployment IAP Access Configuration ==="
echo "Adding user $GCP_PROJECT_MEMBER to IAP access list..."
gcloud iap web add-iam-policy-binding \
    --resource-type="cloud-run" \
    --service="$SERVICE_NAME" \
    --region="$REGION" \
    --member="user:$GCP_PROJECT_MEMBER" \
    --role="roles/iap.httpsResourceAccessor" \
    --project="$GCP_PROJECT_ID" 2>/dev/null || echo "WARNING: Native IAP binding for '$SERVICE_NAME' failed."

# ==========================================
# Phase 7: Authorized User Configuration Review
# ==========================================
echo ""
echo "=== Phase 7: Authorized IAP Access Members ==="
gcloud iap web get-iam-policy \
    --resource-type="cloud-run" \
    --service="$SERVICE_NAME" \
    --region="$REGION" \
    --project="$GCP_PROJECT_ID" \
    --format="table(bindings.role, bindings.members)" 2>/dev/null || echo "WARNING: Could not retrieve IAP access list. Ensure the service is deployed and native IAP is fully configured."
echo "================================================="

# gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --project=$GCP_PROJECT_ID --limit=30

