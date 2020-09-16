# flask-api-test
Flask API running on AWS

This simple test application allows user to extract linguistic features from a piece of text. The app uses AWS SQS messages to keep a queue of requested jobs; it also sends output reports to GCS in JSON format.

**All of this was done for practicing purposes.**

## Build and Run

### Flask
Useful for debugging. The Flask application is [`app.api.py`](./app/api.py)

```shell script
python -m app.process &
export FLASK_APP=app/api.py
flask run
```

This execution will expose the API through `localhost:5000`.

### Docker
Run the script [`build.sh`](./build.sh) to execute the application using Docker and Gunicorn in production-like environments.

The application expects receiving several environment variables from the Docker environment. **When using [`build.sh`](./build.sh), you can define those variables from the host using the same names.**

### Environment variables
- **`PORT`**: The exposed port from the Docker container and to perform the binding with the host. Already defined in [`build.sh`](./build.sh) as the port `5000` through the host environment variable `PORT`.
- **`AWS_ACCESS_KEY_ID`**: AWS access key for managing the SQS queue.
- **`AWS_SECRET_ACCESS_KEY`**: AWS secret key for managing the SQS queue.
- **`SQS_REGION_NAME`**: SQS needs the `region_name` parameter at construction time of the client ([boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html)).
- **`SQS_QUEUE_URL`**: SQS URL access.
- **`SPACY_MODEL_NAME`**: spaCy model name of the model used to perform the text parsing. Already defined in [`build.sh`](./build.sh) as `en_core_web_sm`, which the only one available from the Docker environment.
- **`GCP_CREDENTIALS`**: GCP service account info (service account credentials JSON file content). Preferred to avoid storing the file in repo when building on the cloud.
- **`GCP_CREDENTIALS_FILE`**: GCP service account JSON file (useful when working in local). Not used in [`build.sh`](./build.sh).
- **`GCS_OUTPUT_BUCKET`**: GCS bucket name for the output report.
- **`GCS_OUTPUT_PREFIX`**:  GCS object prefix for the output report.
- **`LOG_LEVEL`**: Logging level of the [`app.process`](./app/process.py) task. Default is `ERROR` (this default is also hardcoded in [`build.sh`](./build.sh)). 

## Endpoints
- **`/submit`**
    - method: `POST`
        - description: Creates a job to process a piece of text, maximum size is `256 KB`.
        - content-type: `x-www-form-urlencoded` or through query string parameter.
        - data:
            - `text`: Piece of text to process.
                - type: `string`
        - return:
            - type: `JSON`
            - fields:
                - `submitted`: `true` if the job was successfully placed in queue.
                    - type: `boolean`
                - `id`: job ID, which is also the same as the SQS message in queue.
                    - type: `string`
            - status: `201` if success.
                
- **`/status`**
    - method: `GET`
        - description: Checks API status. Doesn't expect parameters.
        - returns:
            - type: `JSON`
            - fields:
                - `processing_jobs`: `true` if there are messages in the queue or in flight.
                    type: `boolean`
                - `queue_attributes`: SQS attributes values now `ApproximateNumberOfMessages` and `ApproximateNumberOfMessagesNotVisible` casted to `number`.
                    type: `object`
            - status: `200` if success.


### Testing endpoints
- **`/message`**:
    - method: `GET`
        - description: Gets a message from the SQS queue.
        - returns:
            - type: `JSON`
            - fields:
                - `message_received`: `true` if message received.
                    - type: `boolean`
                - `sent_timestamp`: time epoch when the SQS message was sent.
                    - type: `string`
                - `body`: SQS message body, includes sent `text` and a `timestamp` taken when starting the submit process.
                    - type: `object`
                - `id`: SQS message ID.
                    - type: `string`
            - cookies:
                - `receiptHandle`: receipt handle ID to delete the message form the queue.
                    - `Path`: `/message`
                    - `Max-Age`: `600`
        - status: `200` if OK, `204` if no messages (response empty).
    - method: `DELETE`
        - description: Deletes a message received from the SQS queue.
        - returns:
            - type: `JSON`
            - fields:
                - `message_deleted`: `true` if message deletion happened successfully.
                    - type: `boolean`
    
## Tests
- [`test_text_processing.py`](./tests/test_text_processing.py) checks if the parsing process is working the same way for the [`parsed_text_sample.json`](./tests/parsed_text_sample.json). This test aims to work as a verification step on a CD workflow using GitHub Actions.
    
## TODO
- Continuous Deployment to AWS ECS using GitHub Actions and AWS CloudFormation.
