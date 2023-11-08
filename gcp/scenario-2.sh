#!/bin/bash

export ZONE=us-central1-c

# Eliminar archivos existentes en la carpeta de destino
gcloud compute ssh monitoring-worker --zone $ZONE -- "rm -rf /tmp/trigger"


gcloud compute scp --recurse ../monitor monitoring-worker:/tmp/monitor --zone $ZONE
gcloud compute scp --recurse ../trigger monitoring-worker:/tmp/trigger --zone $ZONE

### Correr experimento
gcloud compute ssh --zone "us-central1-c" "monitoring-worker" --project "cloud-conversion-tool-403205" --command "sudo su -c '
echo \"Inicializar monitoring-container\" &&
cd /tmp/monitor &&
if docker inspect monitoring-container &> /dev/null; then
    docker stop monitoring-container
    docker rm monitoring-container
    docker rmi monitoring-image
fi &&
docker build -t monitoring-image . &&
docker run -d --env-file /etc/api.env --name monitoring-container monitoring-image &&
echo \"Inicializar trigger-container\" &&
cd /tmp/trigger &&
if docker inspect trigger-container &> /dev/null; then
    docker stop trigger-container
    docker rm trigger-container
    docker rmi trigger-image
fi &&
docker build -t trigger-image . &&
docker run -d --env-file /etc/api.env --name trigger-container -v /mnt/video:/video trigger-image &&
docker logs -f trigger-container && 
docker logs -f monitoring-container && 
echo \"Esperar que el experimento termine de correr y copiar los archivos\" &&
while [ \"\$(docker inspect -f '{{.State.Running}}' monitoring-container)\" == 'true' ]; do
    sleep 5
done && 
echo \"El contenedor monitoring-container ha dejado de correr, ejecutar comandos adicionales aquí\" &&
export MONITORING_CONTAINER_ID=\$(docker ps -aqf "name=monitoring-container") &&
docker cp \$MONITORING_CONTAINER_ID:/monitor/output.png /home/ldmolinav &&
docker cp \$MONITORING_CONTAINER_ID:/monitor/output.csv /home/ldmolinav && 
docker cp \$MONITORING_CONTAINER_ID:/monitor/reporte.txt /home/ldmolinav
'"

### Inicializar trigger-container
# gcloud compute ssh --zone "us-central1-c" "monitoring-worker" --project "cloud-conversion-tool-403205" --command "sudo su -c '
# cd /tmp/trigger &&
# if docker inspect trigger-container &> /dev/null; then
#     docker stop trigger-container
#     docker rm trigger-container
# fi &&
# docker build -t trigger-image . &&
# docker run -d --env-file /etc/api.env --name trigger-container -v /mnt/video:/video trigger-image'"


### Esperar que el experimento termine de correr y copiar los archivos:
# gcloud compute ssh --zone "us-central1-c" "monitoring-worker" --project "cloud-conversion-tool-403205" --command "sudo su -c '
# while [ \"\$(docker inspect -f '{{.State.Running}}' monitoring-container)\" == 'true' ]; do
#     sleep 5
# done && 
# echo \"El contenedor monitoring-container ha dejado de correr, ejecutar comandos adicionales aquí\" &&
# export MONITORING_CONTAINER_ID=\$(docker ps -aqf "name=monitoring-container") &&
# docker cp \$MONITORING_CONTAINER_ID:/monitor/reporte.png /home/ldmolinav &&
# docker cp \$MONITORING_CONTAINER_ID:/monitor/output.csv /home/ldmolinav'"

