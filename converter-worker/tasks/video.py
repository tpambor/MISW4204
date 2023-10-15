import os
from celery import Celery

BROKER = os.getenv('BROKER') or "redis://127.0.0.1:6379/0"

celery_app = Celery(__name__, broker=BROKER)

@celery_app.task(name="convert_video")
def convert_video(id_video, old_format, new_format):
    print(f"Converting video {id_video} from {old_format} to {new_format}")
