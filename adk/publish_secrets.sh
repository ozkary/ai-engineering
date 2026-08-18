#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Default values
PROJECT_ID=""
SECRET_NAME=""
SECRET_VALUE=""

# Helper function to print usage
usage() {
  echo "Usage: $0 -n <secret_name> -v <secret_value_or_file_path> [-p <project_id>]"
  echo "  -n, --name      Name of the secret to create/update in Secret Manager"
  echo "  -v, --value     Secret value (can be a plain-text string, or a path to a file if prefixed with @)"
  echo "  -p, --project   GCP Project ID (optional, defaults to GOOGLE_CLOUD_PROJECT env var or 'ozkary-de-101')"
  exit 1
}

# Parse command-line options
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -n|--name) SECRET_NAME="$2"; shift ;;
    -v|--value) SECRET_VALUE="$2"; shift ;;
    -p|--project) PROJECT_ID="$2"; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown parameter passed: $1"; usage ;;
  esac
  shift
done

# Validate required parameters
if [ -z "$SECRET_NAME" ] || [ -z "$SECRET_VALUE" ]; then
  echo "❌ Error: Secret name and value are required."
  usage
fi

# Resolve Project ID
if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-ozkary-de-101}"
fi

echo "🚀 Publishing secret to GCP Secret Manager..."
echo "Project ID:  $PROJECT_ID"
echo "Secret Name: $SECRET_NAME"

# Check if the secret already exists
if gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" &>/dev/null; then
  echo "ℹ️ Secret '$SECRET_NAME' already exists. Adding a new version..."
else
  echo "🆕 Creating new secret '$SECRET_NAME'..."
  gcloud secrets create "$SECRET_NAME" \
    --project="$PROJECT_ID" \
    --replication-policy="automatic"
fi

# Handle file inputs (if value is prefixed with @, e.g., @path/to/key.json)
if [[ "$SECRET_VALUE" == @* ]]; then
  FILE_PATH="${SECRET_VALUE#@}"
  if [ ! -f "$FILE_PATH" ]; then
    echo "❌ Error: File not found at $FILE_PATH"
    exit 1
  fi
  echo "🔑 Uploading secret value from file: $FILE_PATH"
  gcloud secrets versions add "$SECRET_NAME" \
    --project="$PROJECT_ID" \
    --data-file="$FILE_PATH"
else
  echo "🔑 Uploading secret value from text input"
  echo -n "$SECRET_VALUE" | gcloud secrets versions add "$SECRET_NAME" \
    --project="$PROJECT_ID" \
    --data-file=-
fi

echo "✅ Secret successfully published to GCP Secret Manager!"
