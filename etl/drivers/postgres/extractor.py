import os
from contextlib import contextmanager

import backoff
import psycopg2
from config.log_settings import logger
from data.sql_queries import get_all_sql, get_last_modified_sql
from psycopg2.extras import DictCursor


@contextmanager
def postgres_connection(connection_config: dict):
    @backoff.on_exception(
        backoff.expo,
        psycopg2.OperationalError,
        max_tries=5,
        max_time=5,
    )
    def _connect():
        return psycopg2.connect(**connection_config, cursor_factory=DictCursor)

    connection = None
    try:
        connection = _connect()
        yield connection

    except psycopg2.OperationalError as error:
        logger.error(f'Postgres connection error. {error}')
    except psycopg2.Error as error:
        logger.error(f'Unexpected Postgres error. {error}')
        if connection:
            connection.rollback()
    except Exception as error:
        logger.exception(f'Unexpected error. {error}')
    else:
        connection.commit()
    finally:
        if connection:
            connection.close()


class PostgresExtractor:
    def __init__(self):
        self.connection_config = {
            'dbname': os.environ.get('POSTGRES_DB'),
            'user': os.environ.get('POSTGRES_USER'),
            'password': os.environ.get('POSTGRES_PASSWORD'),
            'host': os.environ.get('POSTGRES_HOST'),
            'port': int(os.environ.get('POSTGRES_PORT')),
        }
        self.get_all_sql = get_all_sql
        self.get_last_modified_sql = get_last_modified_sql

    def extract(self, last_sync_time: str | None) -> list[dict]:
        with postgres_connection(self.connection_config) as connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                if last_sync_time:
                    cursor.execute(self.get_last_modified_sql, (last_sync_time, last_sync_time, last_sync_time))
                else:
                    cursor.execute(self.get_all_sql)

                return [dict(entry) for entry in cursor]
