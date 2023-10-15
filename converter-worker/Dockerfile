FROM python:3.11-bookworm

RUN apt update && \
  apt install --no-install-recommends --yes \
    ffmpeg \
  && apt clean && \
  rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD ["celery", "-A", "tasks", "worker"]
