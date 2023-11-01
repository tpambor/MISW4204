import os
import time
import subprocess
from celery import Celery
from celery.signals import worker_init, worker_process_init
from sqlalchemy import update
from google.cloud import storage
import db
from models import Task, TaskStatus

BROKER = os.getenv('BROKER') or "redis://127.0.0.1:6379/0"
VIDEO_DIR = os.getenv('VIDEO_DIR', '')
BUCKET = os.getenv('BUCKET', '')

celery_app = Celery(__name__, broker=BROKER)
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

@celery_app.task(name="convert_video")
def convert_video(id_video, old_format, new_format):
    print(f"Converting video {id_video} from {old_format} to {new_format}")

    path_old = os.path.join(VIDEO_DIR, f'{id_video}.{old_format}')
    path_new = os.path.join(VIDEO_DIR, f'{id_video}.{new_format}')

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)
    blob = bucket.blob(f'{id_video}.{old_format}')
    blob.download_to_filename(path_old)

    tstart = time.monotonic()
    result = subprocess.run(['ffmpeg', '-y', '-nostats', '-i', path_old, '-b:v', '2M', path_new], capture_output=True, check=True)
    duration = time.monotonic() - tstart

    blob = bucket.blob(f'{new_task.id}.{new_format}')
    blob.upload_from_filename(path_new)

    with db.session() as session:
        session.execute(
            update(Task).where(Task.id == id_video).values(status=TaskStatus.PROCESSED)
        )
        session.commit()

    print(f"Finished converting video {id_video} in {duration}s")
