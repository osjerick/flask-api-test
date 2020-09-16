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
  -e SPACY_MODEL_NAME=en_core_web_sm \
  -e GCP_CREDENTIALS="${GCP_CREDENTIALS}" \
  -e GCS_OUTPUT_BUCKET="${GCS_OUTPUT_BUCKET}" \
  -e GCS_OUTPUT_PREFIX="${GCS_OUTPUT_PREFIX}" \
  -e LOG_LEVEL="${LOG_LEVEL:-ERROR}" \
  osjerick/api-test:latest
