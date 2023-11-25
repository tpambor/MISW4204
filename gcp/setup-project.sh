#!/bin/bash

export REGION=us-central1
export PROJECT_ID=$(gcloud config get-value project)

# Enable required services
gcloud services enable artifactregistry.googleapis.com

# Create artifact repository for Cloud Run
gcloud artifacts repositories create cloud-converter \
  --location=$REGION \
  --repository-format=docker

# Create service account for GitHub CI
gcloud iam service-accounts create github-ci \
  --display-name="GitHub CI" \
  --description="Service account for GitHub CI"

# Assign role to write container images to Cloud Artifacts from GitHub CI
gcloud artifacts repositories add-iam-policy-binding cloud-converter \
  --location=$REGION \
  --member="serviceAccount:github-ci@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
