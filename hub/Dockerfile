FROM python:3.9.10-slim

RUN pip install --upgrade pip \
    && pip install flask==2.* gunicorn==20.1.0

COPY ./flask_app /home/flask_app

WORKDIR /home/flask_app

CMD ["gunicorn" ,"--workers", "2", "--threads", "2", "--bind", "0.0.0.0:5000", "app:app"]
