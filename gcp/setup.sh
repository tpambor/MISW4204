#!/bin/bash
export REGION=us-central1
export ZONE=us-central1-c
export ZONE2=us-central1-f

export PROJECT_ID=$(gcloud config get-value project)

#### Enable required services

gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable iamcredentials.googleapis.com

echo ""

#### Create service account

export SERVICE_ACCOUNT="converter@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create converter \
  --display-name="Converter" \
  --description="Service account for converter"

echo ""

# Assign role to create/view/delete objects and buckets in Cloud Storage
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.admin"

echo ""

# Assign role to create links to download from Cloud Storage
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/iam.serviceAccountTokenCreator"

echo ""

# Assign roles to access Cloud SQL instances
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudsql.client"

echo ""

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudsql.instanceUser"

echo ""

#### Configure Cloud Storage

# Bucket name has to be globally unique, therefore add suffix
BUCKET_SUFFIX=$(tr -dc a-z </dev/urandom | head -c 4 ; echo '')
export BUCKET=misw4204-$BUCKET_SUFFIX

gcloud storage buckets create gs://$BUCKET \
  --location=$REGION \
  --uniform-bucket-level-access \
  --public-access-prevention

echo ""

#### Create PubSub topic converter

gcloud pubsub topics create converter

export PUBSUB_TOPIC="projects/$PROJECT_ID/topics/converter"

echo ""

# Assign role for PubSub publisher to service account
gcloud pubsub topics add-iam-policy-binding converter \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/pubsub.publisher"

echo ""

#### Configure Database

gcloud sql instances create db1 \
  --zone=$ZONE \
  --database-version=POSTGRES_14 \
  --cpu=1 \
  --memory=4096MB \
  --database-flags=cloudsql.iam_authentication=on \
  --insights-config-query-insights-enabled \
  --insights-config-record-client-address

echo ""

gcloud sql users create "converter@$PROJECT_ID.iam" \
  --instance=db1 \
  --type=CLOUD_IAM_SERVICE_ACCOUNT

echo ""

gcloud sql databases create converter \
  --instance=db1

echo ""

#### Create Cloud Run service for API REST / Web

cat converter-api.yml | envsubst | gcloud run services replace - \
  --region=$REGION

echo ""

#### Make API REST / Web publicly available
gcloud run services add-iam-policy-binding converter-api \
  --region=$REGION \
  --member="allUsers" \
  --role="roles/run.invoker"

echo ""
