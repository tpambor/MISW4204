#!/bin/bash
export REGION=us-central1
export ZONE=us-central1-c

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
  --location=$REGION \
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
  --network=projects/$PROJECT_ID/global/networks/default \
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

#### Create instance template for API REST / Web

gcloud compute instance-templates create web-template \
  --instance-template-region=$REGION \
  --machine-type=n2-highcpu-2 \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --tags=allow-health-check,allow-load-balancer \
  --service-account=$SERVICE_ACCOUNT \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --metadata=database-url=$DATABASE_URL,broker=redis://$WORKER_IP_PRIVATE:6379/0,bucket=$BUCKET \
  --metadata-from-file startup-script=web.startup-script

echo ""

#### Create firewall rule for health check

gcloud compute firewall-rules create allow-health-check \
  --direction=ingress \
  --network=default \
  --action=allow \
  --source-ranges=130.211.0.0/22,35.191.0.0/16 \
  --target-tags=allow-health-check \
  --rules=tcp:80

echo ""

#### Create firewall rule for load balancer

export LOAD_BALANCER_SUBNET=$(gcloud compute networks subnets describe proxy-only-subnet --region=$REGION --format=json | jq -r '.ipCidrRange')

gcloud compute firewall-rules create allow-load-balancer \
  --direction=ingress \
  --network=default \
  --action=allow \
  --source-ranges=$LOAD_BALANCER_SUBNET \
  --target-tags=allow-load-balancer \
  --rules=tcp:80

echo ""

#### Create managed instance group for API REST / Web

gcloud compute instance-groups managed create web-mig \
  --size=1 \
  --template=https://www.googleapis.com/compute/v1/projects/$PROJECT_ID/regions/$REGION/instanceTemplates/web-template \
  --zone=$ZONE

echo ""

#### Configure named port http (80)

gcloud compute instance-groups set-named-ports web-mig \
  --zone=$ZONE \
  --named-ports=http:80

echo ""

### Configure autoscaling

gcloud compute instance-groups managed set-autoscaling web-mig \
  --zone=$ZONE \
  --max-num-replicas=3 \
  --min-num-replicas=1 \
  --update-stackdriver-metric=agent.googleapis.com/memory/percent_used \
  --stackdriver-metric-filter="metric.labels.state = \"used\"" \
  --stackdriver-metric-utilization-target-type=gauge \
  --stackdriver-metric-utilization-target=55 \
  --cool-down-period=180

echo ""

#### Create health check for API REST / Web

gcloud compute health-checks create http hc-http \
  --region=$REGION \
  --description="HTTP health check" \
  --use-serving-port \
  --request-path='/health-check' \
  --check-interval=60s \
  --timeout=60s \
  --healthy-threshold=1 \
  --unhealthy-threshold=3 \
  --enable-logging

echo ""

#### Create backend service for API REST / Web

gcloud compute backend-services create web-backend-service \
  --region=$REGION \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --protocol=HTTP \
  --port-name=http \
  --health-checks=hc-http \
  --health-checks-region=$REGION \
  --timeout=600s \
  --enable-logging

echo ""

#### Add managed instance group to backend service

gcloud compute backend-services add-backend web-backend-service \
  --region=$REGION \
  --instance-group=web-mig \
  --instance-group-zone=$ZONE \
  --balancing-mode=utilization \
  --max-utilization=0.55

echo ""

#### Create url map

gcloud compute url-maps create web-url-map \
  --region=$REGION \
  --default-service=web-backend-service

echo ""

#### Create http proxy

gcloud compute target-http-proxies create web-proxy \
  --region=$REGION \
  --url-map=web-url-map \
  --url-map-region=$REGION

echo ""

#### Create forwarding rule

gcloud compute forwarding-rules create web-forwarding-rule \
  --region=$REGION \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --network=default \
  --network-tier=standard \
  --ports=80 \
  --target-http-proxy=web-proxy \
  --target-http-proxy-region=$REGION

export WEB_IP=$(gcloud compute forwarding-rules describe web-forwarding-rule --region=$REGION --format=json | jq -r '.IPAddress')

echo ""

#### Configure Trigger / Monitoring

export NUM_PARALLEL_TASKS=5
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
  --metadata=database-url=$DATABASE_URL,broker=redis://$WORKER_IP_PRIVATE:6379/0,num-parallel-taks=$NUM_PARALLEL_TASKS,num-cycles=$NUM_CYCLES,old-format=$OLD_FORMAT,new-format=$NEW_FORMAT,demo-video=$DEMO_VIDEO,bucket=$BUCKET  \
  --metadata-from-file startup-script=monitoring.startup-script

export MONITOR_IP=$(gcloud compute instances describe monitoring-worker --zone $ZONE --format json | jq -r '.networkInterfaces[0].accessConfigs[0].natIP')

echo ""

echo ""
echo "Infrastructure created!"
echo ""
echo "API: http://$WEB_IP/"
