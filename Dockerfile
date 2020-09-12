FROM python:3.8-slim-buster

COPY . /app/
WORKDIR /app

RUN pip install -U pip && \
    pip install --use-feature=2020-resolver -r requirements.txt

EXPOSE ${PORT}

CMD gunicorn --bind :${PORT} api:app
