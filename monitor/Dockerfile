FROM python:3.11-bookworm

RUN apt -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update && \
  apt install --no-install-recommends --yes \
    gnuplot \
  && apt clean && \
  rm -rf /var/lib/apt/lists/*

COPY . /monitor

RUN pip install -r /monitor/requirements.txt

WORKDIR /monitor

CMD python -u /monitor/monitor.py
