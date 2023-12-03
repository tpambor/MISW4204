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

# Assign roles to view Logging
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/logging.viewer"

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
  --availability-type=regional \
  --zone=$ZONE \
  --secondary-zone=$ZONE2 \
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

export API_URL=$(gcloud run services describe converter-api --region=$REGION --format=json | jq -r '.status.url')

echo ""

#### Make API REST / Web publicly available
gcloud run services add-iam-policy-binding converter-api \
  --region=$REGION \
  --member="allUsers" \
  --role="roles/run.invoker"

echo ""

#### Create Cloud Run service for worker
cat converter-worker.yml | envsubst | gcloud run services replace - \
  --region=$REGION

export WORKER_URL=$(gcloud run services describe converter-worker --region=$REGION --format=json | jq -r '.status.url')

echo ""

#### Make worker available for PubSub
gcloud run services add-iam-policy-binding converter-worker \
  --region=$REGION \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.invoker"

echo ""

#### Create PubSub subscription converter-sub
gcloud pubsub subscriptions create converter-sub \
  --topic=$PUBSUB_TOPIC \
  --push-endpoint=$WORKER_URL \
  --push-auth-service-account=$SERVICE_ACCOUNT \
  --ack-deadline=600  

echo ""

#### Configure Trigger / Monitoring
export CLOUDSQL_INSTANCE=$PROJECT_ID:$REGION:db1
export CLOUDSQL_DB=converter
export NUM_PARALLEL_TASKS=1
export NUM_CYCLES=1
export OLD_FORMAT=mp4
export NEW_FORMAT=webm
export DEMO_VIDEO=salento-720p.mp4

gcloud compute instances create monitoring-worker \
 --zone $ZONE \
 --machine-type=e2-highcpu-2 \
 --image-family debian-12 \
 --image-project debian-cloud \
 --tags ssh-server \
 --service-account=$SERVICE_ACCOUNT \
 --scopes=https://www.googleapis.com/auth/cloud-platform \
 --metadata=database-url=$DATABASE_URL,num-parallel-taks=$NUM_PARALLEL_TASKS,num-cycles=$NUM_CYCLES,old-format=$OLD_FORMAT,new-format=$NEW_FORMAT,demo-video=$DEMO_VIDEO,bucket=$BUCKET,pubsub-topic=$PUBSUB_TOPIC,pubsub-monitor-sub=$PUBSUB_MONITOR_SUBSCRIPTION,pubsub-completion-monitor-sub=$PUBSUB_COMPLETION_MONITOR_SUBSCRIPTION,cloudsql-instance=$CLOUDSQL_INSTANCE,cloudsql-db=$CLOUDSQL_DB  \
 --metadata-from-file startup-script=monitoring.startup-script

export MONITOR_IP=$(gcloud compute instances describe monitoring-worker --zone $ZONE --format json | jq -r '.networkInterfaces[0].accessConfigs[0].natIP')

echo "Setup completed!"
echo ""
echo "API: $API_URL"
echo ""
