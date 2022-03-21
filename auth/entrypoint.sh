#!/bin/sh

set -e
python3 utils/wait_for_redis.py
python3 utils/wait_for_postgres.py
flask db upgrade
gunicorn wsgi_app:app --bind 0.0.0.0:5000