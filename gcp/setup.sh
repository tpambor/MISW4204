#!/bin/bash
export REGION=europe-west1
export ZONE=europe-west1-d

# https://cloud.google.com/sdk/gcloud/reference/sql/instances/create
# https://cloud.google.com/sql/docs/postgres/create-instance?hl=es
gcloud sql instances create db1 \
  --zone=$ZONE \
  --database-version=POSTGRES_15 \
  --cpu=2 \
  --memory=8192MB \
  --insights-config-query-insights-enabled \
  --insights-config-record-client-address

# Database IP
export DB_IP=$(gcloud sql instances describe db1 --format=json | jq -r '.ipAddresses[] | select(.type=="PRIMARY").ipAddress')
export DATABASE_URL="postgresql://postgres:postgres@$DB_IP/converter"

echo ""

gcloud compute instances create worker \
  --zone $ZONE \
  --machine-type=e2-micro \
  --image-family cos-stable \
  --image-project cos-cloud \
  --metadata=database-url=$DATABASE_URL \
  --metadata-from-file user-data=worker.cloud-init

export WORKER_IP=$(gcloud compute instances describe worker --zone $ZONE --format json | jq -r '.networkInterfaces[0].accessConfigs[0].natIP')

echo ""

gcloud -q sql instances patch db1 \
  --authorized-networks=$WORKER_IP/32

echo ""
echo "Infrastructure created"

# gcloud compute instances delete worker --zone=$ZONE
# gcloud sql instances delete db1
