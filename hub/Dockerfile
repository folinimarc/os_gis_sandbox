FROM python:3.9.10-slim

RUN pip install --upgrade pip \
    && pip install flask==2.0.2

COPY ./flask_app /home/flask_app

ENTRYPOINT FLASK_APP=/home/flask_app/app.py flask run --host=0.0.0.0 --port=5000