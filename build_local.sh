#!/usr/bin/env bash

export API_PORT=5000
docker container rm --force api
docker image build -t osjerick/api-test:latest .
docker container run --detach --name api -p ${API_PORT}:${API_PORT} \
-e PORT=${API_PORT} \
-e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
-e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
-e SQS_REGION_NAME="${SQS_REGION_NAME}" \
-e SQS_QUEUE_URL="${SQS_QUEUE_URL}" \
osjerick/api-test:latest
