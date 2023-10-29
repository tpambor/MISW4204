import os
import time
import subprocess
from celery import Celery
from celery.signals import worker_process_init, task_received, task_success, after_task_publish
from sqlalchemy import update
from models import Task, TaskStatus
import db
import datetime

BROKER = os.getenv('BROKER') or "redis://127.0.0.1:6379/0"
VIDEO_DIR = os.getenv('VIDEO_DIR', '')

celery_app = Celery(__name__, broker=BROKER) 
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.task_send_sent_event = True

@worker_process_init.connect
def setup_worker(**kwargs):
    """
        When Celery forks the parent process, the db engine & connection pool is included in that.
        But, the db connections should not be shared across processes, so we tell the engine
        to dispose all existing connections, which will cause new ones to be opened in the child
        processes as needed.
        More info: https://docs.sqlalchemy.org/en/20/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
    """
    db.engine.dispose()

@celery_app.task(bind=True, name="convert_video")
def convert_video(self, id_video, old_format, new_format):
    print(f"Converting video {id_video} from {old_format} to {new_format}")

    path_old = os.path.join(VIDEO_DIR, f'{id_video}.{old_format}')
    path_new = os.path.join(VIDEO_DIR, f'{id_video}.{new_format}')

    tstart = time.monotonic()
    result = subprocess.run(['ffmpeg', '-y', '-nostats', '-i', path_old, '-b:v', '2M', path_new], capture_output=True, check=True)
    duration = time.monotonic() - tstart

    print(f"Finished converting video {id_video} in {duration}s")

    with db.session() as session:
        session.execute(
            update(Task).where(Task.id == id_video).values(status=TaskStatus.PROCESSED)
        )
        session.commit()
        
    # return id_video

# # TODO: ESTA SIGNAL NO FUNCIONA
# @after_task_publish.connect
# def after_task_publish_handler(sender=None, headers=None, body=None, **kwargs):
#     print('after_task_publish for task')

# @task_received.connect
# def task_received_handler(sender=None, request=None, **kwargs):
#     request_body = request.body
#     request_converted = json.loads(request_body.decode('utf-8'))
#     id_video = request_converted[0][0]
#     print('task_received for task with video id {id}'.format(
#         id=id_video,
#     ))

# @task_success.connect
# def task_success_handler(sender=None, result=None, **kwargs):
#     print('task_success for task with video id {id}'.format(
#         id=result,
#     ))