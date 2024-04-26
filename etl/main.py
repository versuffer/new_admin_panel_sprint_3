from contextlib import contextmanager
from datetime import datetime
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler
from config.app_settings import app_settings
from config.log_settings import logger
from dotenv import load_dotenv
from drivers.storage import JsonFileStorage
from management.state import State
from pipeline import ETLPipeline

load_dotenv()


@contextmanager
def scheduler_context(scheduler: BackgroundScheduler):
    try:
        scheduler.start()
        while True:
            sleep(5)
    except KeyboardInterrupt:
        scheduler.shutdown()


def run_pipeline() -> None:
    storage = JsonFileStorage(app_settings.STATE_FILE_NAME)
    state = State(storage)
    pipeline = ETLPipeline(state)
    pipeline.run()


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_pipeline, 'interval', minutes=1, max_instances=1, misfire_grace_time=5 * 60, next_run_time=datetime.now()
    )

    with scheduler_context(scheduler):
        logger.info('Scheduler started.')
