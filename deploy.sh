#!/bin/bash

# Exit on error
set -e

APP_NAME="litellm-proxy"
REGION="us-central1"

# Check if PROJECT_ID is provided
if [ -z "$1" ]; then
  echo "Usage: ./deploy.sh <PROJECT_ID> [REGION]"
  echo "Example: ./deploy.sh my-gcp-project us-central1"
  exit 1
fi

PROJECT_ID=$1

if [ -n "$2" ]; then
  REGION=$2
fi

echo "======================================================"
echo "Deploying $APP_NAME to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "======================================================"

# 1. Enable necessary services
echo "Enabling Cloud Run and Artifact Registry APIs..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com --project "$PROJECT_ID"

# 2. Build and Push Container
# We use Cloud Build to build the image directly on GCP (simplest, no local docker needed)
IMAGE_URL="gcr.io/$PROJECT_ID/$APP_NAME:latest"
echo "Building container image: $IMAGE_URL ..."
gcloud builds submit --tag "$IMAGE_URL" --project "$PROJECT_ID"

# 3. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "$APP_NAME" \
  --image "$IMAGE_URL" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --allow-unauthenticated \
  --port 8000 \
  --execution-environment gen2 \
  --memory 1Gi \
  --min 0 \
  --no-cpu-throttling

echo "======================================================"
echo "Deployment Complete!"
echo "Service URL: $(gcloud run services describe $APP_NAME --platform managed --region $REGION --project $PROJECT_ID --format 'value(status.url)')"
echo "======================================================"
