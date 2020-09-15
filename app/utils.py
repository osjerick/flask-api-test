import os

import boto3


def init_sqs_client():
    """
    Returns an AWS SQS Client. AWS credentials should be available from standard system-wide environment variables:
    `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. `region_name` parameter should be passed to the client constructor
    function through the environment variable `SQS_REGION_NAME`.

    :return: AWS SQS Client
    """

    client_kwargs = dict()
    assert 'SQS_REGION_NAME' in os.environ, '`SQS_REGION_NAME` environment variable must be available'
    client_kwargs['region_name'] = os.environ['SQS_REGION_NAME']
    sqs_client = boto3.client('sqs', **client_kwargs)

    return sqs_client


def get_required_sqs_queue():
    """
    Returns an AWS SQS URL available through the system-wide environment variable `SQS_QUEUE_URL`. If the environment
    is not defined, the process fails.

    :return: AWS SQS URL string
    """

    assert 'SQS_QUEUE_URL' in os.environ, '`SQS_QUEUE_URL` environment variable must be available'
    sqs_queue_url = os.environ['SQS_QUEUE_URL']

    return sqs_queue_url
