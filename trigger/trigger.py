import shutil
import os
from models import Task, TaskStatus
import db
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import storage, pubsub_v1
from google.api_core import exceptions
from concurrent import futures
import json

BUCKET = os.getenv('BUCKET')
DATABASE_URL = os.getenv('DATABASE_URL')
NUM_PARALLEL_TASKS = int(os.getenv('NUM_PARALLEL_TASKS') or 100)
NUM_CYCLES = int(os.getenv('NUM_CYCLES') or 10)
OLD_FORMAT = os.getenv('OLD_FORMAT')
NEW_FORMAT = os.getenv('NEW_FORMAT')
DEMO_VIDEO = os.getenv('DEMO_VIDEO')
BUCKET = os.getenv('BUCKET')
PUBSUB_TOPIC = os.getenv('PUBSUB_TOPIC')

publisher = pubsub_v1.PublisherClient()

def create_and_send_task(index, cycle):
    try:
        new_task = Task(
            user=1,
            created=datetime.datetime.utcnow(),
            fileName=DEMO_VIDEO,
            status=TaskStatus.UPLOADED,
            oldFormat=OLD_FORMAT,
            newFormat=NEW_FORMAT,
        )
        new_task_id =  None

        # Guardar tarea de conversión en BD
        with db.session() as session:
            session.add(new_task)
            session.commit()
            db.session.refresh(new_task)
            new_task_id = new_task.id

        # Guardar video a convertir en bucket
        client = storage.Client()
        bucket = client.get_bucket(BUCKET)
        blob = bucket.blob(f'{new_task.id}.{OLD_FORMAT}')
        blob.upload_from_filename(DEMO_VIDEO)
        print(f'Video copiado con éxito como {blob.name}')

        # Mandar tarea de conversión a Cloud Pub/Sub
        pubsub_task = {
            'id_video': new_task.id,
            'old_format': new_task.oldFormat,
            'new_format': new_task.newFormat,
            'task_sent': datetime.datetime.utcnow().isoformat()
        }

        publisher.publish(PUBSUB_TOPIC, json.dumps(pubsub_task).encode('utf-8'))
       
        print(f'Enviada solicitud {index} del ciclo {cycle} a la cola de mensajes con id {new_task_id}.')

    except Exception as e:
        print(f'Error al procesar la tarea: {str(e)}')
        
def publish_tasks():
    with ThreadPoolExecutor() as executor:
        for cycle in range(NUM_CYCLES): 
            futures = {executor.submit(create_and_send_task, index, cycle): index for index in range(1, NUM_PARALLEL_TASKS + 1)}
            for future in as_completed(futures):
                index = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f'Error en la tarea {index}: {str(e)}')

if __name__ == "__main__":
    db.Base.metadata.create_all(db.engine)
    publish_tasks()
    db.session.close()