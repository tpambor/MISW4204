import os
import time
import subprocess
import json
from concurrent import futures
from sqlalchemy import update
from google.cloud import pubsub_v1
from google.cloud import storage
import db
from models import Task, TaskStatus

VIDEO_DIR = os.getenv('VIDEO_DIR')
BUCKET = os.getenv('BUCKET')
SUBSCRIPTION_NAME = os.getenv('SUBSCRIPTION')

def conversion_callback(message):
    req = json.loads(message.data)

    id_video = req['id_video']
    old_format = req['old_format']
    new_format = req['new_format']

    print(f"Converting video {id_video} from {old_format} to {new_format}", flush=True)
    message.ack()

    path_old = os.path.join(VIDEO_DIR, f'{id_video}.{old_format}')
    path_new = os.path.join(VIDEO_DIR, f'{id_video}.{new_format}')

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)
    blob = bucket.blob(f'{id_video}.{old_format}')
    blob.download_to_filename(path_old)

    tstart = time.monotonic()
    subprocess.run(['ffmpeg', '-y', '-nostats', '-i', path_old, '-b:v', '2M', path_new], capture_output=True, check=True)
    duration = time.monotonic() - tstart

    blob = bucket.blob(f'{id_video}.{new_format}')
    blob.upload_from_filename(path_new)

    os.remove(path_old)
    os.remove(path_new)

    with db.session() as session:
        session.execute(
            update(Task).where(Task.id == id_video).values(status=TaskStatus.PROCESSED)
        )
        session.commit()

    print(f"Finished converting video {id_video} in {duration}s", flush=True)

with pubsub_v1.SubscriberClient() as subscriber:
    executor = futures.ThreadPoolExecutor(max_workers=1)
    scheduler = pubsub_v1.subscriber.scheduler.ThreadScheduler(executor)
    future = subscriber.subscribe(SUBSCRIPTION_NAME, conversion_callback, scheduler=scheduler)

    future.result()
