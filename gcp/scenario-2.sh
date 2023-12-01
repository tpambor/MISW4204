#!/bin/bash
export ZONE=us-central1-c

export PROJECT_ID=$(gcloud config get-value project)


#### Modificar variables (Opcional)

NUM_CYCLES=2
NUM_PARALLEL_TASKS=10

gcloud compute ssh --zone $ZONE "monitoring-worker" --project $PROJECT_ID --command "sudo su -c '
sed -i 's/^NUM_CYCLES=.*/NUM_CYCLES=$NUM_CYCLES/' /etc/api.env &&
sed -i 's/^NUM_PARALLEL_TASKS=.*/NUM_PARALLEL_TASKS=$NUM_PARALLEL_TASKS/' /etc/api.env'"

#### Eliminar archivos existentes en las carpetas monitor y trigger (Opcional, recomendado en caso de haber hecho cambios en alguna de esas carpetas)

gcloud compute ssh monitoring-worker --zone $ZONE -- "rm -rf /tmp/monitor"
gcloud compute ssh monitoring-worker --zone $ZONE -- "rm -rf /tmp/trigger"

#### Copia las carpetas monitor y trigger a la VM

gcloud compute scp --recurse ../monitor monitoring-worker:/tmp/monitor --zone $ZONE
gcloud compute scp --recurse ../trigger monitoring-worker:/tmp/trigger --zone $ZONE


#### Correr experimento

gcloud compute ssh --zone $ZONE "monitoring-worker" --project $PROJECT_ID --command "sudo su -c '
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
echo \"El contenedor monitoring-container ha dejado de correr, copiar archivos\" &&
export MONITORING_CONTAINER_ID=\$(docker ps -aqf "name=monitoring-container") &&
docker cp \$MONITORING_CONTAINER_ID:/monitor/output.png /home/$USER &&
docker cp \$MONITORING_CONTAINER_ID:/monitor/output.csv /home/$USER && 
docker cp \$MONITORING_CONTAINER_ID:/monitor/reporte.txt /home/$USER'"


#### Copiar archivos generados por el script a la carpeta destino

export FOLDER_SCENARIO=/home/ldmolinav/MISW4204/escenario2
export FOLDER_ASSIGMENT=cuarta_entrega
export SCENARIO_CASE=caso2
export CASE_ITERATION=iteracion2

mkdir -p "$FOLDER_SCENARIO/$FOLDER_ASSIGMENT/$SCENARIO_CASE/$CASE_ITERATION"

gcloud compute scp monitoring-worker:~/output.png $FOLDER_SCENARIO/$FOLDER_ASSIGMENT/$SCENARIO_CASE/$CASE_ITERATION --zone=$ZONE
gcloud compute scp monitoring-worker:~/output.csv $FOLDER_SCENARIO/$FOLDER_ASSIGMENT/$SCENARIO_CASE/$CASE_ITERATION --zone=$ZONE
gcloud compute scp monitoring-worker:~/reporte.txt $FOLDER_SCENARIO/$FOLDER_ASSIGMENT/$SCENARIO_CASE/$CASE_ITERATION --zone=$ZONE