FROM python:3.11-bookworm

COPY . /monitor

RUN pip install -r /monitor/requirements.txt

WORKDIR /monitor

CMD python -u /monitor/monitor.py
