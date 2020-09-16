FROM python:3.8-slim-buster

WORKDIR /srv/

COPY ./requirements.txt ./

RUN pip install -U pip && \
    pip install --use-feature=2020-resolver -r requirements.txt

COPY . ./

EXPOSE ${PORT}

CMD ["./run_backend.sh"]
