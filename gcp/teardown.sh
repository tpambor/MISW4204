#!/bin/bash

export REGION=us-central1
export ZONE=us-central1-c

export PROJECT_ID=$(gcloud config get-value project)
export SERVICE_ACCOUNT="converter@$PROJECT_ID.iam.gserviceaccount.com"

gcloud -q compute instances delete monitoring-worker --zone=$ZONE || true

gcloud -q compute instances delete worker --zone=$ZONE || true

gcloud -q compute firewall-rules delete allow-health-check || true
gcloud -q compute firewall-rules delete allow-load-balancer || true
gcloud -q compute forwarding-rules delete web-forwarding-rule --region=$REGION || true
gcloud -q compute target-http-proxies delete web-proxy --region=$REGION || true
gcloud -q compute url-maps delete web-url-map --region=$REGION || true
gcloud -q compute backend-services delete web-backend-service --region=$REGION || true
gcloud -q compute health-checks delete hc-http --region=$REGION || true
gcloud -q compute instance-groups managed delete web-mig --zone=$ZONE || true
gcloud -q compute instance-templates delete web-template --region=$REGION || true

gcloud storage rm -r gs://misw4204-* || true

gcloud -q sql instances delete db1 || true

gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/storage.admin" || true
gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/iam.serviceAccountTokenCreator" || true
gcloud -q projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/monitoring.metricWriter" || true
gcloud -q iam service-accounts delete $SERVICE_ACCOUNT || true
