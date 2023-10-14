import os
from celery import Celery

BROKER = os.getenv('BROKER') or "redis://127.0.0.1:6379/0"

celery_app = Celery(__name__, broker=BROKER)

@celery_app.task(name="convertir_video")
def convertir_video(id_video):
    print("Convertiendo video")
