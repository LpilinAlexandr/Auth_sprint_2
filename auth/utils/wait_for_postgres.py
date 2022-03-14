import logging
import time

import psycopg2


DELAY = 2
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':

    pg = psycopg2.connect('postgresql://user:password@db/auth_database')

    while True:
        try:
            cur = pg.cursor()
            cur.execute('SELECT 1')
        except psycopg2.OperationalError:
            time.sleep(DELAY)
            logger.warning(f'Postgres is not ready. Wait {DELAY} seconds...')
            continue

        logger.warning('Postgres is ready...')
        break


