#!/bin/bash
set -e

export REGION=us-central
export ZONE=us-central1-c

export PROJECT_ID=$(gcloud config get-value project)
export SERVICE_ACCOUNT="converter@$PROJECT_ID.iam.gserviceaccount.com"

gcloud -q compute firewall-rules delete default-allow-http &
gcloud -q compute instances delete worker --zone=$ZONE &
gcloud -q compute instances delete web --zone=$ZONE &
gcloud -q sql instances delete db1 &
gcloud storage rm -r gs://misw4204-* &
gcloud -q compute instances delete monitoring-worker --zone=$ZONE &

wait < <(jobs -p)

gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/storage.objectAdmin"
gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/iam.serviceAccountTokenCreator"
gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/monitoring.metricWriter"
gcloud -q iam service-accounts delete $SERVICE_ACCOUNT
