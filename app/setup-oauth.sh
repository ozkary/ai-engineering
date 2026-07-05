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

# Set the default project member / test user email
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

# Enable the IAP API if not already enabled
echo "Ensuring Identity-Aware Proxy API is enabled..."
gcloud services enable iap.googleapis.com --project="$GCP_PROJECT_ID"

# Get Cloud Run Service URL to display as Authorized JavaScript origin
SERVICE_NAME="heart-disease-risk-ui"
REGION="us-east1"
echo "Retrieving Cloud Run service URL..."
APP_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$GCP_PROJECT_ID" --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$APP_URL" ]; then
    echo "WARNING: Cloud Run service '$SERVICE_NAME' not found or not deployed yet."
    APP_URL="https://<your-cloud-run-url>"
fi

# ==========================================
# Phase 3: Interactive OAuth Configuration Steps
# ==========================================
echo ""
echo "=== Phase 3: Google Auth Platform Configuration Instructions ==="
echo "Please perform the following actions in the Google Cloud Console:"
echo ""
echo "A. Configure the OAuth Consent Screen (One-Time Setup):"
echo "   1. Navigate to: Google Auth Platform -> OAuth consent screen (or APIs & Services -> OAuth consent screen)"
echo "   2. Choose 'External' as the User Type and click 'Create'."
echo "   3. Fill in the App Name (e.g., 'Heart Disease Risk UI'), support email, and developer contact email."
echo "   4. Save and continue. For Scopes, leave defaults and save/continue."
echo "   5. In the 'Test users' step, or via Google Auth Platform -> Audience:"
echo "      Add your active account email as a test user: $GCP_PROJECT_MEMBER"
echo "   6. Save and complete the consent screen setup."
echo ""
echo "B. Create OAuth Client Credentials:"
echo "   1. Navigate to: Google Auth Platform -> Clients (or APIs & Services -> Credentials)"
echo "   2. Click '+ Create Credentials' and select 'OAuth client ID'."
echo "   3. Choose 'Web application' as the Application type."
echo "   4. Set the name (e.g., 'Heart Disease Risk Agent UI Client')."
echo "   5. Under 'Authorized JavaScript origins', add your app URL:"
echo "      $APP_URL"
echo "   6. Under 'Authorized redirect URIs', add the IAP redirect URI format:"
echo "      https://iap.googleapis.com/v1/oauth/clientIds/<YOUR_CLIENT_ID>:handleRedirect"
echo "      Note: Replace <YOUR_CLIENT_ID> with the actual Client ID that is generated."
echo "   7. Save / Create the OAuth client."
echo "   8. Copy the generated Client ID and Client Secret, and write them to 'iap-oauth.yaml' in the 'app' directory:"
echo "      ---------------------------------------"
echo "      accessSettings:"
echo "        oauthSettings:"
echo "          clientId: \"YOUR_CLIENT_ID\""
echo "          clientSecret: \"YOUR_CLIENT_SECRET\""
echo "      ---------------------------------------"
echo ""

# Wait for User Confirmation
while true; do
    read -p "Have you completed these steps and saved 'app/iap-oauth.yaml'? (y/N): " ready
    if [[ "$ready" =~ ^[Yy]$ ]]; then
        if [ -f "iap-oauth.yaml" ]; then
            echo "Found iap-oauth.yaml!"
            break
        elif [ -f "app/iap-oauth.yaml" ]; then
            echo "Found iap-oauth.yaml in app/ directory!"
            # Move or cd as needed, but in our project structure we are inside /app
            break
        else
            echo "ERROR: 'iap-oauth.yaml' file was not found in the current directory or 'app/' directory."
            echo "Please create the file with your credentials and try again."
        fi
    else
        echo "Please complete the steps and try again."
    fi
done

# ==========================================
# Phase 4: Configure IAP Settings
# ==========================================
echo ""
echo "=== Phase 4: Applying IAP settings ==="

# Detect directory context and run the command
IAP_YAML="iap-oauth.yaml"
if [ ! -f "$IAP_YAML" ] && [ -f "app/iap-oauth.yaml" ]; then
    IAP_YAML="app/iap-oauth.yaml"
fi

gcloud iap settings set "$IAP_YAML" \
    --project="$GCP_PROJECT_ID" \
    --resource-type=cloud-run \
    --region="$REGION" \
    --service="$SERVICE_NAME"

# ==========================================
# Phase 5: Verification & Check
# ==========================================
echo ""
echo "=== Phase 5: Verifying configuration ==="
echo "Retrieving applied settings..."
gcloud iap settings get \
    --project="$GCP_PROJECT_ID" \
    --resource-type=cloud-run \
    --region="$REGION" \
    --service="$SERVICE_NAME" \
    --format="yaml(accessSettings.oauthSettings)"

echo ""
echo "OAuth configuration complete and successfully applied to Identity-Aware Proxy."
