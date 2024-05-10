from contextlib import contextmanager

import backoff
import psycopg2
from config.app_settings import app_settings
from config.log_settings import logger
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
            'dbname': app_settings.POSTGRES_DB,
            'user': app_settings.POSTGRES_USER,
            'password': app_settings.POSTGRES_PASSWORD,
            'host': app_settings.POSTGRES_HOST,
            'port': app_settings.POSTGRES_PORT,
        }

    def extract(self, last_sync_time: str | None, sql_queries_mapping: dict) -> list[dict]:
        with postgres_connection(self.connection_config) as connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                if last_sync_time:
                    cursor.execute(
                        sql_queries_mapping['get_last_modified'].format(last_sync_time=f"'{last_sync_time}'")
                    )
                else:
                    cursor.execute(sql_queries_mapping['get_all'])

                return [dict(entry) for entry in cursor]
