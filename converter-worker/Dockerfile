FROM python:3.11-bookworm

# Workaround https://github.com/microsoft/WSL/issues/4114
RUN apt -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update && \
  apt install --no-install-recommends --yes \
    ffmpeg \
  && apt clean && \
  rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD ["celery", "-A", "tasks", "worker"]
