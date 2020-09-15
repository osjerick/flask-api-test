from typing import Dict

import simplejson as json
from flask import Flask
from flask_restful import Api, Resource
from flask_restful.reqparse import RequestParser

import app.utils as utils
from datetime import datetime

backend = Flask(__name__)
api = Api(backend)


class SubmitJob(Resource):
    """
    API Resource to manage job submission.
    """

    parser = RequestParser()
    parser.add_argument('text', required=True, help='Text cannot be omitted!')
    sqs_client = utils.init_sqs_client()
    sqs_queue_url = utils.get_required_sqs_queue()

    # Utils
    def submit_job_to_sqs(self, text: str) -> Dict[str, str]:
        """
        Take string and submit a message to AWS SQS to be processed as a job for the backend process.

        :param text: text string to process
        """

        timestamp = datetime.utcnow().isoformat(' ', 'seconds')
        response = self.sqs_client.send_message(QueueUrl=self.sqs_queue_url,
                                                MessageBody=json.dumps({'text': text,
                                                                        'timestamp': timestamp},
                                                                       ensure_ascii=False, encoding='utf8'))

        return {'sqs_message_id': response.get('MessageId')}

    # Methods
    def post(self):
        args = self.parser.parse_args()
        job_info = self.submit_job_to_sqs(args["text"])

        return {'submitted': True, **job_info}, 201


api.add_resource(SubmitJob, '/submit')


class QueueStatus(Resource):
    """
    API Resource to check AWS Queue status.
    """

    sqs_client = utils.init_sqs_client()
    sqs_queue_url = utils.get_required_sqs_queue()
    sqs_attributes_to_get = {'ApproximateNumberOfMessages': int,
                             'ApproximateNumberOfMessagesNotVisible': int}

    # Utils
    def get_queue_info(self) -> Dict[str, int]:
        response = self.sqs_client.get_queue_attributes(QueueUrl=self.sqs_queue_url,
                                                        AttributeNames=list(self.sqs_attributes_to_get.keys()))
        attributes = response['Attributes']

        for attribute, value in attributes.items():
            attributes[attribute] = self.sqs_attributes_to_get[attribute](value)

        return attributes

    # Methods
    def get(self):
        queue_info = self.get_queue_info()

        if queue_info['ApproximateNumberOfMessages'] == 0 and queue_info['ApproximateNumberOfMessagesNotVisible'] == 0:
            processing = False
        else:
            processing = True

        return {'processing_jobs': processing, 'queue_attributes': queue_info}


api.add_resource(QueueStatus, '/status')


# Use only for testing
class SQSMessage(Resource):
    """
    Get and Delete SQS messages.
    """

    parser = RequestParser()
    parser.add_argument('receiptHandle', required=True, help='Receipt Handle cannot be omitted!', location='cookies')
    sqs_client = utils.init_sqs_client()
    sqs_queue_url = utils.get_required_sqs_queue()

    # Methods
    def get(self):
        response = self.sqs_client.receive_message(QueueUrl=self.sqs_queue_url,
                                                   AttributeNames=['SentTimestamp'],
                                                   MaxNumberOfMessages=1,
                                                   MessageAttributeNames=['All'],
                                                   VisibilityTimeout=0,
                                                   WaitTimeSeconds=0)

        if 'Messages' in response:
            message = response['Messages'][0]
            message_body = json.loads(message['Body'])
            message_id = message['MessageId']
            receipt_handle = message['ReceiptHandle']
            sent_timestamp = message['Attributes']['SentTimestamp']

            return ({'message_received': True,
                     'sent_timestamp': sent_timestamp,
                     'body': message_body,
                     'id': message_id},
                    200,
                    {'Set-Cookie': f'receiptHandle={receipt_handle}; Path=/message; Max-Age=600'})
        else:
            return {'message_received': False}, 204

    def delete(self):
        args = self.parser.parse_args()
        response = self.sqs_client.delete_message(QueueUrl=self.sqs_queue_url,
                                                  ReceiptHandle=args['receiptHandle'])

        return {'message_deleted': True}


api.add_resource(SQSMessage, '/message')
