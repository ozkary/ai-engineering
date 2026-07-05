#!/bin/bash
set -e

# ==========================================
# 1. Environment Variable & Script Requirements
# ==========================================
SERVICE_NAME="heart-disease-risk-ui"
REGION="us-east1"

# Ensure environment variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "ERROR: GCP_PROJECT_ID environment variable is not set."
    exit 1
fi

if [ -z "$SERVICE_ACCOUNT" ]; then
    SERVICE_ACCOUNT="heart-disease-risk-ui-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com"
fi

ACTIVE_ACCOUNT=$(gcloud config get-value account 2>/dev/null || echo "")
if [ -z "$GCP_PROJECT_MEMBER" ]; then
    if [ -n "$ACTIVE_ACCOUNT" ]; then
        GCP_PROJECT_MEMBER="$ACTIVE_ACCOUNT"
    else
        echo "ERROR: GCP_PROJECT_MEMBER environment variable is not set, and unable to detect active gcloud account."
        exit 1
    fi
fi

# ==========================================
# Phase 2: Resource Review & Confirmation Gate
# ==========================================
echo "=== Workspace Environment Validation ==="
echo "Target Service Name: $SERVICE_NAME"
echo "Target Region:       $REGION"
echo "GCP Project ID:      $GCP_PROJECT_ID"
echo "Service Account:     $SERVICE_ACCOUNT"
echo "IAP Access Member:   $GCP_PROJECT_MEMBER"
echo "========================================"

read -p "Are you sure you want to TEAR DOWN the Cloud Run application and Service Account? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Tear down aborted by user."
    exit 0
fi

# ==========================================
# Step A: Delete Cloud Run Service
# ==========================================
echo "=== Deleting Google Cloud Run Service: $SERVICE_NAME ==="
if gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$GCP_PROJECT_ID" &>/dev/null; then
    gcloud run services delete "$SERVICE_NAME" \
        --region="$REGION" \
        --project="$GCP_PROJECT_ID" \
        --quiet
    echo "Cloud Run service '$SERVICE_NAME' deleted successfully."
else
    echo "Cloud Run service '$SERVICE_NAME' does not exist."
fi

# ==========================================
# Step B: Remove IAM Policy Binding for IAP
# ==========================================
echo "=== Removing IAP Policy Access for $GCP_PROJECT_MEMBER ==="
gcloud iap web remove-iam-policy-binding \
    --resource-type="cloud-run" \
    --service="$SERVICE_NAME" \
    --region="$REGION" \
    --member="user:$GCP_PROJECT_MEMBER" \
    --role="roles/iap.httpsResourceAccessor" \
    --project="$GCP_PROJECT_ID" || echo "IAP policy binding removal skipped or not found."

# ==========================================
# Step C: Delete Service Account & Role Bindings
# ==========================================
echo "=== Tearing Down Service Account: $SERVICE_ACCOUNT ==="
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project "$GCP_PROJECT_ID" &>/dev/null; then
    # Remove project level role bindings
    echo "Removing roles/run.invoker policy binding..."
    gcloud projects remove-iam-policy-binding "$GCP_PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/run.invoker" || true

    echo "Removing roles/aiplatform.user policy binding..."
    gcloud projects remove-iam-policy-binding "$GCP_PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/aiplatform.user" || true

    # Remove storage object viewer, artifact registry writer, and IAP service agent policy bindings
    PROJECT_NUMBER=$(gcloud projects describe "$GCP_PROJECT_ID" --format="value(projectNumber)" 2>/dev/null || echo "")
    if [ -n "$PROJECT_NUMBER" ]; then
        COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
        CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

        echo "Removing roles/storage.objectViewer from default Compute SA ($COMPUTE_SA)..."
        gcloud projects remove-iam-policy-binding "$GCP_PROJECT_ID" \
            --member="serviceAccount:$COMPUTE_SA" \
            --role="roles/storage.objectViewer" || true

        echo "Removing roles/artifactregistry.writer from default Compute SA ($COMPUTE_SA)..."
        gcloud projects remove-iam-policy-binding "$GCP_PROJECT_ID" \
            --member="serviceAccount:$COMPUTE_SA" \
            --role="roles/artifactregistry.writer" || true

        echo "Removing roles/artifactregistry.writer from default Cloud Build SA ($CLOUDBUILD_SA)..."
        gcloud projects remove-iam-policy-binding "$GCP_PROJECT_ID" \
            --member="serviceAccount:$CLOUDBUILD_SA" \
            --role="roles/artifactregistry.writer" || true

        echo "Removing run.invoker from IAP service agent on service '$SERVICE_NAME'..."
        gcloud run services remove-iam-policy-binding "$SERVICE_NAME" \
            --region="$REGION" \
            --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-iap.iam.gserviceaccount.com" \
            --role="roles/run.invoker" \
            --project="$GCP_PROJECT_ID" --quiet 2>/dev/null || true
    fi

    echo "Deleting service account..."
    gcloud iam service-accounts delete "$SERVICE_ACCOUNT" \
        --project "$GCP_PROJECT_ID" \
        --quiet
    echo "Service Account deleted successfully."
else
    echo "Service Account '$SERVICE_ACCOUNT' does not exist."
fi

echo "=== App/UI Cleanup Complete ==="
