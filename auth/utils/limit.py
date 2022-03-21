import datetime
from http import HTTPStatus

import redis
from flask import request, jsonify

from app_settings.settings import settings


def limit(func):
    """Декоратор на ограничение запросов по времени при помощи Redis."""

    def wrapper(*args, **kwargs):
        redis_conn = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        pipe = redis_conn.pipeline()
        now = datetime.datetime.now()

        ip = request.remote_addr or '127.0.0.1'
        key = f'{ip}:{now.minute}'

        pipe.incr(key, 1)
        pipe.expire(key, 59)

        result = pipe.execute()
        request_number = result[0]

        if request_number > settings.REQUEST_LIMIT_PER_MINUTE:
            return jsonify('Too Many Requests'), HTTPStatus.TOO_MANY_REQUESTS

        return func(*args, **kwargs)
    return wrapper
