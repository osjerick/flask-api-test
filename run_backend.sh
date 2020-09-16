#!/usr/bin/env bash

python -m app.process &
gunicorn --bind :"${PORT}" app:flask_app
