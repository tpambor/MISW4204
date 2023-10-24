#!/bin/bash
export REGION=us-central
export ZONE=us-central1-c

#### Configure File Server

gcloud compute instances create fileserver \
  --zone $ZONE \
  --machine-type=e2-micro \
  --image-family debian-12 \
  --image-project debian-cloud \
  --metadata-from-file startup-script=fileserver.startup-script

export FILESERVER_IP_PRIVATE=$(gcloud compute instances describe fileserver --zone $ZONE --format json | jq -r '.networkInterfaces[0].networkIP')

echo ""

#### Configure Database

gcloud sql instances create db1 \
  --zone=$ZONE \
  --database-version=POSTGRES_15 \
  --cpu=1 \
  --memory=4096MB \
  --insights-config-query-insights-enabled \
  --insights-config-record-client-address

export DB_IP=$(gcloud sql instances describe db1 --format=json | jq -r '.ipAddresses[] | select(.type=="PRIMARY").ipAddress')

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
  --machine-type=e2-highcpu-2 \
  --image-family cos-stable \
  --image-project cos-cloud \
  --metadata=database-url=$DATABASE_URL,fileserver-ip=$FILESERVER_IP_PRIVATE,google-monitoring-enabled=true \
  --metadata-from-file user-data=worker.cloud-init

export WORKER_IP=$(gcloud compute instances describe worker --zone $ZONE --format json | jq -r '.networkInterfaces[0].accessConfigs[0].natIP')
export WORKER_IP_PRIVATE=$(gcloud compute instances describe worker --zone $ZONE --format json | jq -r '.networkInterfaces[0].networkIP')

echo ""

gcloud -q sql instances patch db1 \
  --authorized-networks=$WORKER_IP/32

echo ""

#### Configure API REST / Web

gcloud compute instances create web \
  --zone $ZONE \
  --machine-type=e2-highcpu-2 \
  --image-family cos-stable \
  --image-project cos-cloud \
  --tags http-server \
  --metadata=database-url=$DATABASE_URL,broker=redis://$WORKER_IP_PRIVATE:6379/0,fileserver-ip=$FILESERVER_IP_PRIVATE,google-monitoring-enabled=true \
  --metadata-from-file user-data=web.cloud-init

export WEB_IP=$(gcloud compute instances describe web --zone $ZONE --format json | jq -r '.networkInterfaces[0].accessConfigs[0].natIP')

echo ""

gcloud -q sql instances patch db1 \
  --authorized-networks=$WORKER_IP/32,$WEB_IP/32

echo ""

echo ""
echo "Infrastructure created!"
echo ""
echo "API: http://$WEB_IP/"
