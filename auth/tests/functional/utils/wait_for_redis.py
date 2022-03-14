import logging
import os
import time

from redis import StrictRedis, ConnectionError

DELAY = 2
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':

    r = StrictRedis(
        host=os.getenv('REDIS_HOST', default='redis'),
        port=int(os.getenv('REDIS_PORT', default=6379))
    )

    while True:

        try:
            is_ready = r.ping()
        except ConnectionError:
            is_ready = False

        if not is_ready:
            time.sleep(DELAY)
            logger.warning(f'Redis is not ready. Wait {DELAY} seconds...')
            continue

        logger.warning('Redis is ready...')
        break
