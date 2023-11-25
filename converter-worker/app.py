import base64
import datetime
import json
import os
import subprocess
import time
from flask import Flask, request
import google.auth
from google.cloud import storage
from google.cloud.sql.connector import Connector
from db import db
from modelos import Task, TaskStatus
from sqlalchemy import update

VIDEO_DIR = "/video"
BUCKET = os.getenv('STORAGE_BUCKET')
PROJECT = os.getenv('GCP_PROJECT')

# Initialize Python Cloud SQL Connector object
connector = Connector()

credentials, _ = google.auth.default()
credentials.refresh(request=google.auth.transport.requests.Request())
cloudsql_user = credentials.service_account_email.replace('.gserviceaccount.com', '')
cloudsql_instance = os.getenv('CLOUDSQL_INSTANCE')
cloudsql_db = os.getenv('CLOUDSQL_DB')

# Python Cloud SQL Connector database connection function
def getconn():
    conn = connector.connect(
        cloudsql_instance,
        'pg8000',
        db=cloudsql_db,
        user=cloudsql_user,
        enable_iam_auth=True
    )
    return conn

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "creator": getconn
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def convert(id_video, old_format, new_format):
    path_old = os.path.join(VIDEO_DIR, f'{id_video}.{old_format}')
    path_new = os.path.join(VIDEO_DIR, f'{id_video}.{new_format}')

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)
    blob = bucket.blob(f'{id_video}.{old_format}')
    blob.download_to_filename(path_old)

    subprocess.run(['ffmpeg', '-y', '-nostats', '-i', path_old, '-b:v', '2M', path_new], capture_output=True, check=True)

    blob = bucket.blob(f'{id_video}.{new_format}')
    blob.upload_from_filename(path_new)

    os.remove(path_old)
    os.remove(path_new)

    db.session.execute(
        update(Task).where(Task.id == id_video).values(status=TaskStatus.PROCESSED)
    )
    db.session.commit()

@app.route("/", methods=["POST"])
def index():
    """Receive and parse Pub/Sub messages."""
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}", flush=True)
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}", flush=True)
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    if not isinstance(pubsub_message, dict) or "data" not in pubsub_message or "publish_time" not in pubsub_message or "message_id" not in pubsub_message:
        msg = "no data received"
        print(f"error: {msg}", flush=True)
        return f"Bad Request: {msg}", 400
    
    data = base64.b64decode(pubsub_message["data"]).decode("utf-8")

    try:
        req = json.loads(data)
    except:
        msg = "failed to parse data"
        print(f"error: {msg}", flush=True)
        return f"Bad Request: {msg}", 400

    if not isinstance(req, dict) or "id_video" not in req or "old_format" not in req or "new_format" not in req:
        msg = "invalid request received"
        print(f"error: {msg}", flush=True)
        return f"Bad Request: {msg}", 400  

    id_video = req["id_video"]
    old_format = req["old_format"]
    new_format = req["new_format"]

    print(f"Received request to convert video {id_video} from {old_format} to {new_format}", flush=True)

    tstart = time.monotonic()
    convert(id_video, old_format, new_format)
    duration = time.monotonic() - tstart

    sent = datetime.datetime.fromisoformat(pubsub_message["publish_time"])
    finished = datetime.datetime.now(datetime.timezone.utc)
    time_request = (finished - sent).total_seconds() * 1000

    print(f"Finished converting video {id_video} in {duration}s", flush=True)

    # Build structured log messages as an object.
    global_log_fields = {}

    # Add log correlation to nest all log messages.
    # This is only relevant in HTTP-based contexts, and is ignored elsewhere.
    # (In particular, non-HTTP-based Cloud Functions.)
    request_is_defined = "request" in globals() or "request" in locals()
    if request_is_defined and request:
        trace_header = request.headers.get("X-Cloud-Trace-Context")

        if trace_header and PROJECT:
            trace = trace_header.split("/")
            global_log_fields[
                "logging.googleapis.com/trace"
            ] = f"projects/{PROJECT}/traces/{trace[0]}"

    entry = dict(
        severity="NOTICE",
        message="Video conversion task completed",
        video_id=id_video,
        video_old_format=old_format,
        video_new_format=new_format,
        conversion_time=duration,
        processing_time=time_request,
        publish_time=pubsub_message["publish_time"],
        completion_time=finished.isoformat().replace("+00:00", "Z"),
        task_id=pubsub_message["message_id"],
        **global_log_fields
    )

    print(json.dumps(entry), flush=True)

    return ("", 204)

@app.route("/health-check")
def health_check():
    return ("Happy and alive", 200)
