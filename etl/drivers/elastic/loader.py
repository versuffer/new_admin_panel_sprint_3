from contextlib import contextmanager

import backoff
import elastic_transport
from config.app_settings import app_settings
from config.log_settings import logger
from data.elastic_indexes.genres_index import genres_index
from data.elastic_indexes.movies_index import movies_index
from data.elastic_indexes.persons_index import persons_index
from elasticsearch import Elasticsearch, helpers


@contextmanager
def elastic_manager(elastic: Elasticsearch):
    try:
        yield
    except (elastic_transport.ConnectionError, elastic_transport.ConnectionTimeout) as error:
        logger.error(f'Unexpected Elasticsearch error. {error}')
        raise error
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
        self.elastic_indexes = {
            'movies': movies_index,
            'genres': genres_index,
            'persons': persons_index,
        }

    @backoff.on_exception(
        backoff.expo,
        (elastic_transport.ConnectionError, elastic_transport.ConnectionTimeout),
        max_tries=5,
        max_time=5,
    )
    def _create_index(self, index_name: str) -> None:
        if not self.elastic.indices.exists(index=index_name):
            self.elastic.indices.create(index=index_name, body=self.elastic_indexes[index_name])

    @backoff.on_exception(
        backoff.expo,
        (elastic_transport.ConnectionError, elastic_transport.ConnectionTimeout),
        max_tries=5,
        max_time=5,
    )
    def _load_bulk(self, index_name: str, data: list[dict]) -> None:
        data_bulk = [
            {'_op_type': 'index', '_index': index_name, '_id': entry["id"], '_source': entry} for entry in data
        ]
        helpers.bulk(self.elastic, data_bulk)

    def load(self, index_name: str, data: list[dict]) -> None:
        self._create_index(index_name)
        self._load_bulk(index_name, data)
