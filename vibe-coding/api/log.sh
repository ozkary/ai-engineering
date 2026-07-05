#!/bin/bash
PROJECT_ID="ozkary-de-101"
SERVICE_NAME="heart-disease-risk-assessment"

echo "Retrieving logs for ${SERVICE_NAME}..."
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --limit=50 \
    --format="table(timestamp, httpRequest.status, textPayload)" > log.md
echo "Logs saved to log.md"
