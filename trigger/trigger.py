from celery import Celery
import shutil
import os
from models import Task, TaskStatus
import db
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

DATABASE_URL = os.getenv('DATABASE_URL')
NUM_PARALLEL_TASKS = int(os.getenv('NUM_PARALLEL_TASKS') or 100)
NUM_CYCLES = int(os.getenv('NUM_CYCLES') or 10)
VIDEO_DIR = os.getenv('VIDEO_DIR')
OLD_FORMAT = os.getenv('OLD_FORMAT')
NEW_FORMAT = os.getenv('NEW_FORMAT')
DEMO_VIDEO = os.getenv('DEMO_VIDEO')


celery_app = Celery(__name__, broker=os.getenv('BROKER', 'redis://127.0.0.1:6379/0'))


def create_and_send_task(index, cycle):
    try:
        new_task = Task(
            user=1,
            created=datetime.datetime.utcnow(),
            fileName=DEMO_VIDEO,
            status=TaskStatus.UPLOADED,
            oldFormat=OLD_FORMAT,
            newFormat=NEW_FORMAT,
            conversionTime=None,
        )
        new_task_id =  None
        with db.session() as session:
            session.add(new_task)
            session.commit()
            db.session.refresh(new_task)
            new_task_id = new_task.id
        ruta_video_copia = f'{VIDEO_DIR}/{new_task_id}.{OLD_FORMAT}'
        shutil.copy(DEMO_VIDEO, ruta_video_copia)
        print(f'Video copiado con éxito como {ruta_video_copia}')
        args = (new_task_id, OLD_FORMAT, NEW_FORMAT)
        celery_app.send_task("convert_video", args)
        print(f'Enviada solicitud {index} del ciclo {cycle} a la cola de mensajes con id {new_task_id}.')
    except Exception as e:
        print(f'Error al procesar la tarea: {str(e)}')
        
def publish_tasks():
    with ThreadPoolExecutor(max_workers=NUM_PARALLEL_TASKS) as executor:
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