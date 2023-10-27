#!/bin/bash
set -e

export REGION=us-central
export ZONE=us-central1-c

gcloud -q compute firewall-rules delete default-allow-http &
gcloud -q compute instances delete worker --zone=$ZONE &
gcloud -q compute instances delete web --zone=$ZONE &
gcloud -q sql instances delete db1 &
gcloud -q compute instances delete fileserver --zone=$ZONE &
gcloud -q compute instances delete monitoring-worker --zone=$ZONE &

wait < <(jobs -p)
