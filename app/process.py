"""
Process AWS SQS Messages. This script should be executed periodically.
"""

import os
from typing import Dict, Union

import simplejson as json
import spacy
from google.cloud import storage
from google.oauth2 import service_account

import app.utils as utils
from datetime import datetime

import logging
from time import sleep

logger = logging.getLogger('app.process')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s'))
logger.addHandler(handler)
logger.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'ERROR')))


def process_sqs_message(sqs_client,
                        sqs_queue_url: str,
                        gcs_output_bucket: storage.Bucket,
                        gcs_output_prefix: str) -> None:
    """
    Process SQS Message

    :param sqs_client: AWS SQS client
    :param sqs_queue_url: AWS SQS Queue URL
    :param gcs_output_bucket: GCP GCS bucket
    :param gcs_output_prefix: GCP GCS object prefix
    """

    # Receive one message
    response = sqs_client.receive_message(QueueUrl=sqs_queue_url,
                                          MaxNumberOfMessages=1,
                                          VisibilityTimeout=0,
                                          WaitTimeSeconds=0)

    # Process message
    if 'Messages' in response and len(response['Messages']) > 0:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        message_body = json.loads(message['Body'])
        message_id = message['MessageId']
        text = message_body['text']
        timestamp = message_body['timestamp']
        parsed_text = process_text(text)
        logger.info('Message received successfully!')

        # Send result to GCS
        result = {'id': message_id,
                  'timestamp': timestamp,
                  'text': text,
                  'parsed_text': parsed_text}
        result_string = json.dumps(result, ensure_ascii=False, encoding='utf8', indent=2)
        object_key = (f'{gcs_output_prefix.rstrip("/")}'
                      f'/result_{message_id}_{datetime.fromisoformat(timestamp).strftime("%Y%m%dT%H%M%S")}.json')
        blob = gcs_output_bucket.blob(object_key)
        blob.upload_from_string(result_string)
        logger.info(f'Sent result to `{object_key}` in `{gcs_output_bucket.name}`')

        # Delete message
        sqs_client.delete_message(QueueUrl=sqs_queue_url,
                                  ReceiptHandle=receipt_handle)
        logger.info('Message deleted successfully!')
    else:
        logger.info('No messages in queue')


def process_text(text: str, spacy_model_name: str = None) -> Dict[str, Dict[str, Union[str, bool]]]:
    """
    Processes text extracting linguistic features from tokens using spacy model.

    :param text: text string
    :param spacy_model_name: spaCy model name
    :return: dictionary of linguistic features per token
    """

    nlp = spacy.load(spacy_model_name or os.environ['SPACY_MODEL_NAME'])
    doc = nlp(text)
    processed_text = dict()

    for token in doc:
        processed_text[token.text] = dict(lemma=token.lemma_,
                                          pos=token.pos_,
                                          tag=token.tag_,
                                          dep=token.dep_,
                                          shape=token.shape_,
                                          alpha=token.is_alpha,
                                          stop=token.is_stop)

    return processed_text


def main():
    # SQS Client and SQS Queue
    sqs_client = utils.init_sqs_client()
    sqs_queue_url = utils.get_required_sqs_queue()

    # Google Client
    if 'GCP_CREDENTIALS' in os.environ:
        service_account_info = json.loads(os.environ['GCP_CREDENTIALS'])
    elif 'GCP_CREDENTIALS_FILE' in os.environ:
        with open(os.environ['GCP_CREDENTIALS_FILE'], 'r') as f:
            service_account_info = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(
        info=service_account_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    gcs_client = storage.Client(project=credentials.project_id, credentials=credentials)
    gcs_output_bucket = gcs_client.bucket(os.environ['GCS_OUTPUT_BUCKET'])
    gcs_output_prefix = os.environ['GCS_OUTPUT_PREFIX']

    # Process SQS Message
    while True:
        process_sqs_message(sqs_client, sqs_queue_url, gcs_output_bucket, gcs_output_prefix)
        sleep(60)


if __name__ == '__main__':
    main()
