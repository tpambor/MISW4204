#!/bin/bash

export PROJECT_ID=$(gcloud config get-value project)

gcloud services enable networkconnectivity.googleapis.com

gcloud compute addresses create google-managed-services-default \
  --global \
  --purpose=VPC_PEERING \
  --prefix-length=24 \
  --network=projects/$PROJECT_ID/global/networks/default

gcloud services vpc-peerings update \
  --service=servicenetworking.googleapis.com \
  --ranges=google-managed-services-default \
  --network=default \
  --project=$PROJECT_ID \
  --force
