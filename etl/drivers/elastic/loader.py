from contextlib import contextmanager

import backoff
import elastic_transport
from config.app_settings import app_settings
from config.log_settings import logger
from data.elastic_index import index
from elasticsearch import Elasticsearch, helpers


@contextmanager
def elastic_manager(elastic: Elasticsearch):
    try:
        yield
    except (elastic_transport.ConnectionError, elastic_transport.ConnectionTimeout) as error:
        logger.error(f'Unexpected Elasticsearch error. {error}')
    finally:
        if elastic:
            elastic.close()


class ElasticsearchLoader:
    def __init__(self):
        self.elastic = Elasticsearch(
            hosts=[
                {
                    'scheme': app_settings.ELASTIC_SCHEMA,
                    'host': app_settings.ELASTIC_HOST,
                    'port': app_settings.ELASTIC_PORT,
                }
            ],
            timeout=5,
        )
        self.elastic_index_name = "movies"
        self.elastic_index_config = index

    @backoff.on_exception(
        backoff.expo,
        (elastic_transport.ConnectionError, elastic_transport.ConnectionTimeout),
        max_tries=5,
        max_time=5,
    )
    def _create_index(self) -> None:
        if not self.elastic.indices.exists(index=self.elastic_index_name):
            self.elastic.indices.create(index=self.elastic_index_name, body=self.elastic_index_config)

    @backoff.on_exception(
        backoff.expo,
        (elastic_transport.ConnectionError, elastic_transport.ConnectionTimeout),
        max_tries=5,
        max_time=5,
    )
    def _load_bulk(self, data: list[dict]) -> None:
        data_bulk = [
            {'_op_type': 'index', '_index': self.elastic_index_name, '_id': movie["id"], '_source': movie}
            for movie in data
        ]
        helpers.bulk(self.elastic, data_bulk)

    def load(self, data: list[dict]) -> None:
        with elastic_manager(self.elastic):
            self._create_index()
            self._load_bulk(data)
