#!/usr/bin/env bash

export API_PORT=5000
docker container rm --force api
docker image build -t osjerick/api-test:latest .
docker container run --detach --name api -p ${API_PORT}:${API_PORT} -e PORT=${API_PORT} osjerick/api-test:latest
