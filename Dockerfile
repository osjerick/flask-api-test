FROM python:3.8-slim-buster

RUN apt-get update -y && \
    apt-get install -y cron

WORKDIR /srv/

COPY ./requirements.txt ./

RUN pip install -U pip && \
    pip install --use-feature=2020-resolver -r requirements.txt

COPY . ./

EXPOSE ${PORT}

CMD gunicorn --bind :${PORT} app:backend
