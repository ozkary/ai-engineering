#!/bin/bash
set -e

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

# Export SERVICE_ACCOUNT dynamically based on the final project context
export SERVICE_ACCOUNT="heart-disease-risk-ui-sa@$GCP_PROJECT_ID.iam.gserviceaccount.com"

# Final Confirmation Review
echo ""
echo "=== final deployment Context Review ==="
echo "Target Project ID:              $GCP_PROJECT_ID"
echo "Target Project Member (IAP):    $GCP_PROJECT_MEMBER"
echo "Target Service Account:         $SERVICE_ACCOUNT"
echo "======================================="
read -p "Proceed with provisioning these settings? (y/N): " confirm_final
if [[ ! "$confirm_final" =~ ^[Yy]$ ]]; then
    echo "Setup aborted by user."
    exit 0
fi

# ==========================================
# Step A: Enable Required Google APIs
# ==========================================
echo "=== Enabling Required Google Cloud APIs ==="
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    iap.googleapis.com \
    cloudfunctions.googleapis.com \
    --project="$GCP_PROJECT_ID"

# Extract SA name from SA Email
SA_NAME=$(echo "$SERVICE_ACCOUNT" | cut -d'@' -f1)

echo "=== Provisioning Service Account: $SA_NAME ==="

# 1. Create the Service Account if it doesn't exist
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project "$GCP_PROJECT_ID" &>/dev/null; then
    echo "Service account $SERVICE_ACCOUNT already exists."
else
    echo "Creating service account $SA_NAME..."
    gcloud iam service-accounts create "$SA_NAME" \
        --description="Service account for Heart Disease Risk UI proxy" \
        --display-name="Heart Disease Risk UI SA" \
        --project "$GCP_PROJECT_ID"
fi

# 2. Add Roles to Service Account
# The UI server needs to generate tokens, access downstream Cloud Run services, and call Vertex AI (Gemini).
echo "Granting roles/run.invoker to service account on project level..."
gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/run.invoker"

echo "Granting roles/aiplatform.user to service account on project level..."
gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/aiplatform.user"

# 3. Grant Storage Object Viewer to default compute Service Account
# (Cloud Build uses the default Compute Engine service account to read stage sources)
echo "Resolving project number for default compute engine service account..."
PROJECT_NUMBER=$(gcloud projects describe "$GCP_PROJECT_ID" --format="value(projectNumber)" 2>/dev/null || echo "")
if [ -n "$PROJECT_NUMBER" ]; then
    COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
    CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

    echo "Granting roles/storage.objectViewer to default Compute SA ($COMPUTE_SA) on project..."
    gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
        --member="serviceAccount:$COMPUTE_SA" \
        --role="roles/storage.objectViewer"

    echo "Granting roles/artifactregistry.writer to default Compute SA ($COMPUTE_SA) on project..."
    gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
        --member="serviceAccount:$COMPUTE_SA" \
        --role="roles/artifactregistry.writer"

    echo "Granting roles/artifactregistry.writer to default Cloud Build SA ($CLOUDBUILD_SA) on project..."
    gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
        --member="serviceAccount:$CLOUDBUILD_SA" \
        --role="roles/artifactregistry.writer"
else
    echo "WARNING: Could not resolve project number. Ensure your default compute and build service accounts have storage/artifactregistry access."
fi

