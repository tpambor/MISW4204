FROM python:3.11-bookworm

COPY . /app

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD ["celery", "-A", "tasks", "worker"]
