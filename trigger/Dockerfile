FROM python:3.11-bookworm

COPY . /trigger

RUN pip install -r /trigger/requirements.txt

WORKDIR /trigger

CMD python /trigger/trigger.py
