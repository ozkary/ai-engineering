#!/bin/bash
set -e

# ==========================================
# Pre-flight Validation
# ==========================================
if [ -z "$GCP_PROJECT_ID" ] || [ -z "$SERVICE_ACCOUNT" ]; then
    echo "ERROR: Required environment variables are not set."
    echo ""
    echo "Usage instructions:"
    echo "  export GCP_PROJECT_ID=\"YOUR_GCP_PROJECT_ID\""
    echo "  export SERVICE_ACCOUNT=\"heart-disease-risk-ui-sa@\$GCP_PROJECT_ID.iam.gserviceaccount.com\""
    echo "  ./setup-sa.sh"
    exit 1
fi

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
# The UI server needs to generate tokens and access downstream Cloud Run services.
# Let's grant roles/run.invoker at the project level to simplify downstream proxy connectivity.
echo "Granting roles/run.invoker to service account on project level..."
gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/run.invoker"

# 3. Enable Identity-Aware Proxy API
echo "Enabling Identity-Aware Proxy (IAP) API..."
gcloud services enable iap.googleapis.com --project "$GCP_PROJECT_ID"

echo "=== Service Account Provisioning Complete ==="
echo ""
echo "TIP: To allow specific users to access the IAP-secured Cloud Run app, run:"
echo "  gcloud iap web add-iam-policy-binding \\"
echo "      --resource-type=\"backend-services\" \\"
echo "      --service=\"heart-disease-risk-ui\" \\"
echo "      --member=\"user:USER_EMAIL@example.com\" \\"
echo "      --role=\"roles/iap.httpsResourceAccessor\" \\"
echo "      --project=\"$GCP_PROJECT_ID\""
echo "================================================="

echo "Adding default user ozkary@gmail.com to IAP access list..."
gcloud iap web add-iam-policy-binding \
    --resource-type="backend-services" \
    --service="heart-disease-risk-ui" \
    --member="user:ozkary@gmail.com" \
    --role="roles/iap.httpsResourceAccessor" \
    --project="$GCP_PROJECT_ID"

