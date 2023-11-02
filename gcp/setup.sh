#!/bin/bash
export REGION=us-central
export ZONE=us-central1-c
export BUCKET_LOCATION=us-central1

export PROJECT_ID=$(gcloud config get-value project)

#### Enable required services

gcloud services enable compute.googleapis.com
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

# Assign role to create/view/delete objects in Cloud Storage
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"

echo ""

# Assign role to create links to download from Cloud Storage
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/iam.serviceAccountTokenCreator"

echo ""

# Assign role for Cloud Monitoring
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/monitoring.metricWriter"

echo ""

#### Configure Cloud Storage
# Bucket name has to be globally unique, therefore add suffix
BUCKET_SUFFIX=$(tr -dc a-z </dev/urandom | head -c 4 ; echo '')
export BUCKET=misw4204-$BUCKET_SUFFIX

gcloud storage buckets create gs://$BUCKET \
  --location=$BUCKET_LOCATION \
  --uniform-bucket-level-access \
  --public-access-prevention

echo ""

#### Configure Database

gcloud sql instances create db1 \
  --zone=$ZONE \
  --database-version=POSTGRES_15 \
  --cpu=1 \
  --memory=4096MB \
  --no-assign-ip \
  --network=projects/misw4204-e3/global/networks/default \
  --insights-config-query-insights-enabled \
  --insights-config-record-client-address

export DB_IP=$(gcloud sql instances describe db1 --format=json | jq -r '.ipAddresses[] | select(.type=="PRIVATE").ipAddress')

echo ""

gcloud sql databases create converter \
  --instance=db1

echo ""

export POSTGRES_PASSWORD=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 16 ; echo '')

gcloud sql users set-password postgres \
  --instance=db1 \
  --password=$POSTGRES_PASSWORD

export DATABASE_URL="postgresql://postgres:$POSTGRES_PASSWORD@$DB_IP/converter"

echo ""

#### Configure Worker

gcloud compute instances create worker \
  --zone $ZONE \
  --machine-type=t2d-standard-4 \
  --image-family debian-12 \
  --image-project debian-cloud \
  --service-account=$SERVICE_ACCOUNT \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --metadata=database-url=$DATABASE_URL,bucket=$BUCKET \
  --metadata-from-file startup-script=worker.startup-script

export WORKER_IP=$(gcloud compute instances describe worker --zone $ZONE --format json | jq -r '.networkInterfaces[0].accessConfigs[0].natIP')
export WORKER_IP_PRIVATE=$(gcloud compute instances describe worker --zone $ZONE --format json | jq -r '.networkInterfaces[0].networkIP')

echo ""

#### Configure API REST / Web

gcloud compute instances create web \
  --zone $ZONE \
  --machine-type=e2-highcpu-2 \
  --image-family debian-12 \
  --image-project debian-cloud \
  --tags http-server \
  --service-account=$SERVICE_ACCOUNT \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --metadata=database-url=$DATABASE_URL,broker=redis://$WORKER_IP_PRIVATE:6379/0,bucket=$BUCKET \
  --metadata-from-file startup-script=web.startup-script

export WEB_IP=$(gcloud compute instances describe web --zone $ZONE --format json | jq -r '.networkInterfaces[0].accessConfigs[0].natIP')

echo ""

#### Configure Trigger / Monitoring

#export NUM_PARALLEL_TASKS=20
#export NUM_CYCLES=2
#export OLD_FORMAT=mp4
#export NEW_FORMAT=webm
#export DEMO_VIDEO=salento-720p.mp4

#gcloud compute instances create monitoring-worker \
# --zone $ZONE \
# --machine-type=e2-highcpu-2 \
# --image-family debian-12 \
# --image-project debian-cloud \
# --tags ssh-server \
# --metadata=database-url=$DATABASE_URL,broker=redis://$WORKER_IP_PRIVATE:6379/0,fileserver-ip=$FILESERVER_IP_PRIVATE,num-parallel-taks=$NUM_PARALLEL_TASKS,num-cycles=$NUM_CYCLES,old-format=$OLD_FORMAT,new-format=$NEW_FORMAT,demo-video=$DEMO_VIDEO  \
# --metadata-from-file startup-script=monitoring.startup-script


#export MONITOR_IP=$(gcloud compute instances describe monitoring-worker --zone $ZONE --format json | jq -r '.networkInterfaces[0].accessConfigs[0].natIP')

#echo ""

#### Configure Firewall

gcloud compute firewall-rules create default-allow-http \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server

echo ""
echo "Infrastructure created!"
echo ""
echo "API: http://$WEB_IP/"

### Correr esto en el shell cuando todo lo demás haya terminado

# export ZONE=us-central1-c
# gcloud compute scp --recurse ../monitor monitoring-worker:/tmp/monitor --zone $ZONE
# gcloud compute scp --recurse ../trigger monitoring-worker:/tmp/trigger --zone $ZONE
