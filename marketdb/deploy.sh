#!/bin/bash
set -e

SERVICE_NAME="marketdb-server"
IMAGE="asia-southeast1-docker.pkg.dev/stagvn/marketdb/$SERVICE_NAME"

docker buildx build --platform linux/amd64 -t $IMAGE  --progress=plain --push .

gcloud run deploy $SERVICE_NAME \
  --project stagvn \
  --service-account stagdev@stagvn.iam.gserviceaccount.com \
  --region asia-southeast1 \
  --image $IMAGE \
  --allow-unauthenticated \
  --port 8000 \
  --add-cloudsql-instances stagvn:asia-southeast1:stagvn-pg \
  --update-secrets=/secrets/marketdb.env=marketdb:latest \
  --network default \
  --subnet default
