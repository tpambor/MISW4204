FROM python:3.11-bookworm

COPY . /app

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD ["gunicorn",  "--bind", "0.0.0.0:8000", "--timeout", "0", "app:create_app()"]
