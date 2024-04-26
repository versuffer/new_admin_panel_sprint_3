from datetime import datetime

from config.log_settings import logger
from data.schemas import MovieDataSchema
from drivers.elastic.loader import ElasticsearchLoader
from drivers.postgres.extractor import PostgresExtractor
from management.state import State


class ETLPipeline:
    def __init__(self, state: State) -> None:
        self.state = state
        self.extractor = PostgresExtractor()
        self.loader = ElasticsearchLoader()

    def run(self) -> None:
        last_sync_time = self.state.get_state('last_sync_time')
        logger.info(f'Run ETL pipeline. Last synchronization time: {last_sync_time}')
        try:
            raw_data = self.extractor.extract(last_sync_time)
            validated_data = [MovieDataSchema(**movie).model_dump(mode='json') for movie in raw_data]
            self.loader.load(validated_data)
        except Exception as error:
            logger.exception(f'Error during pipeline execution: {error}')
        else:
            self.state.set_state('last_sync_time', datetime.now().isoformat())
            logger.info(f'Finished ETL pipeline. Objects processed: {len(validated_data)}')
