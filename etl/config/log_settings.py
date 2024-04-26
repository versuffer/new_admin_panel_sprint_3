import logging
from logging.config import dictConfig

LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(levelname)s] [%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S %Z',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        'root': {
            'level': 'INFO',
            'handlers': ['console'],
        }
    },
}

# Initiate logger config
dictConfig(LOGGER_CONFIG)
logger = logging.getLogger('root')
