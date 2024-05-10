from datetime import datetime

from config.log_settings import logger
from data.schemas import GenreDataSchema, MovieDataSchema, PersonDataSchema
from data.sql_queries.genres_sql import get_all_genres_sql, get_last_modified_genres_sql
from data.sql_queries.movies_sql import get_all_movies_sql, get_last_modified_movies_sql
from data.sql_queries.persons_sql import (
    get_all_persons_sql,
    get_last_modified_persons_sql,
)
from drivers.elastic.loader import ElasticsearchLoader, elastic_manager
from drivers.postgres.extractor import PostgresExtractor
from management.state import State


class ETLPipeline:
    def __init__(self, state: State) -> None:
        self.state = state
        self.extractor = PostgresExtractor()
        self.loader = ElasticsearchLoader()
        self.sql_queries = {
            'movies': {
                'get_last_modified': get_last_modified_movies_sql,
                'get_all': get_all_movies_sql,
            },
            'genres': {
                'get_last_modified': get_last_modified_genres_sql,
                'get_all': get_all_genres_sql,
            },
            'persons': {
                'get_last_modified': get_last_modified_persons_sql,
                'get_all': get_all_persons_sql,
            },
        }
        self.data_schemas = {
            'movies': MovieDataSchema,
            'genres': GenreDataSchema,
            'persons': PersonDataSchema,
        }

    def run(self) -> None:
        with elastic_manager(self.loader.elastic):
            for index_name in ['movies', 'genres', 'persons']:
                state_key = f'{index_name}_last_sync_time'
                last_sync_time = self.state.get_state(state_key)
                logger.info(f'Run ETL pipeline for {index_name}. Last synchronization time: {last_sync_time}')
                try:
                    # Extract
                    raw_data = self.extractor.extract(last_sync_time, self.sql_queries[index_name])

                    # Transform / Validate
                    if raw_data:
                        validated_data = [
                            self.data_schemas[index_name](**entry).model_dump(mode='json') for entry in raw_data
                        ]

                        # Load
                        self.loader.load(index_name, validated_data)

                    else:
                        logger.info(f'Finished ETL pipeline for {index_name}. All objects are up to date.')
                        return

                except Exception as error:
                    logger.exception(f'Error during pipeline execution for {index_name}: {error}')
                else:
                    self.state.set_state(state_key, datetime.now().isoformat())
                    logger.info(f'Finished ETL pipeline for {index_name}. Objects processed: {len(validated_data)}')
