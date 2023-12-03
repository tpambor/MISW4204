#!/bin/bash

export REGION=us-central1

export PROJECT_ID=$(gcloud config get-value project)
export SERVICE_ACCOUNT="converter@$PROJECT_ID.iam.gserviceaccount.com"

gcloud -q compute instances delete monitoring-worker --zone=$ZONE || true

gcloud -q pubsub subscriptions delete converter-sub || true
gcloud -q run services remove-iam-policy-binding converter-worker --region=$REGION --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/run.invoker" || true
gcloud -q run services delete converter-worker --region=$REGION

gcloud -q run services remove-iam-policy-binding converter-api --region=$REGION --member="allUsers" --role="roles/run.invoker" || true
gcloud -q run services delete converter-api --region=$REGION

gcloud -q pubsub topics remove-iam-policy-binding converter --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/pubsub.publisher" || true
gcloud -q pubsub topics delete converter || true

gcloud -q sql instances delete db1 || true

gcloud storage rm -r gs://misw4204-* || true

gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/storage.admin" || true
gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/iam.serviceAccountTokenCreator" || true
gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/cloudsql.client" || true
gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/cloudsql.instanceUser" || true
gcloud -q iam service-accounts delete $SERVICE_ACCOUNT || true
