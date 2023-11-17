import os
import time
import subprocess
import json
from concurrent import futures
from sqlalchemy import update
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber import exceptions as sub_exceptions
from google.cloud import storage
from google.api_core import retry
import db
from models import Task, TaskStatus
import datetime


VIDEO_DIR = os.getenv('VIDEO_DIR')
BUCKET = os.getenv('BUCKET')
SUBSCRIPTION_NAME = os.getenv('SUBSCRIPTION')
PUBSUB_TOPIC_COMPLETION = os.getenv('PUBSUB_TOPIC_COMPLETION')


def convert(id_video, old_format, new_format):
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

    # Envía una señal de finalización al script principal
    publisher = pubsub_v1.PublisherClient()
    signal_message = {'task_id': id_video, 'status': 'completed', 'task_completed': datetime.datetime.utcnow().isoformat()}
    future = publisher.publish(PUBSUB_TOPIC_COMPLETION, json.dumps(signal_message).encode('utf-8'))

    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()


with pubsub_v1.SubscriberClient() as subscriber:
    while True:
    # The subscriber pulls a specific number of messages. The actual
    # number of messages pulled may be smaller than max_messages.
        response = subscriber.pull(
            request={"subscription": SUBSCRIPTION_NAME, "max_messages": 1},
            retry=retry.Retry(deadline=300),
        )

        for received_message in response.received_messages:
            req = json.loads(received_message.message.data)

            id_video = req['id_video']
            old_format = req['old_format']
            new_format = req['new_format']

            print(f"Received request to convert video {id_video} from {old_format} to {new_format}", flush=True)

            try:
                subscriber.acknowledge(
                    request={"subscription": SUBSCRIPTION_NAME, "ack_ids": [received_message.ack_id]}
                )
            except sub_exceptions.RetryError as exc:
                continue

            convert(id_video, old_format, new_format)