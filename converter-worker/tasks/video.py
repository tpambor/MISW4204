import os
import time
from celery import Celery
from celery.signals import worker_init, worker_process_init
from sqlalchemy import update
import db
from models import Task, TaskStatus

BROKER = os.getenv('BROKER') or "redis://127.0.0.1:6379/0"

celery_app = Celery(__name__, broker=BROKER)

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

    time.sleep(15)

    with db.session() as session:
        session.execute(
            update(Task).where(Task.id == id_video).values(status=TaskStatus.PROCESSED)
        )
        session.commit()

    print(f"Finished converting video {id_video}")
