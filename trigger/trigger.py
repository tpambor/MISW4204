from celery import Celery
import shutil
import os
from models import Task, TaskStatus
import db
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import storage

VIDEO_DIR = os.getenv('VIDEO_DIR', '')
BUCKET = os.getenv('BUCKET', '')
DATABASE_URL = os.getenv('DATABASE_URL')
NUM_PARALLEL_TASKS = int(os.getenv('NUM_PARALLEL_TASKS') or 100)
NUM_CYCLES = int(os.getenv('NUM_CYCLES') or 10)
OLD_FORMAT = os.getenv('OLD_FORMAT')
NEW_FORMAT = os.getenv('NEW_FORMAT')
DEMO_VIDEO = os.getenv('DEMO_VIDEO')
BUCKET = os.getenv('BUCKET')
celery_app = Celery(__name__, broker=os.getenv('BROKER', 'redis://127.0.0.1:6379/0'))

celery_app.conf.task_send_sent_event = True

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

        with db.session() as session:
            session.add(new_task)
            session.commit()
            db.session.refresh(new_task)
            new_task_id = new_task.id

        client = storage.Client()
        client_str = repr(client)
        print(f'Cliente google: {client_str}')
        bucket = client.get_bucket(BUCKET)
        blob = bucket.blob(f'{new_task.id}.{OLD_FORMAT}')
        blob.upload_from_filename(DEMO_VIDEO)
        print(f'Video copiado con éxito como {blob.name}')
        args = (new_task_id, OLD_FORMAT, NEW_FORMAT)
        celery_app.send_task("convert_video", args)
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