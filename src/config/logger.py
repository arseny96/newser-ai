import logging
from logging.handlers import RotatingFileHandler

app_logger = logging.getLogger('app')
data_logger = logging.getLogger('data')

def setup_loggers(config):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # App Logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(config.APP_LOG_LEVEL)
    app_handler = RotatingFileHandler(
        config.APP_LOG_FILE,
        maxBytes=config.LOG_MAX_SIZE,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    app_handler.setFormatter(formatter)
    app_logger.addHandler(app_handler)

    # Data Logger
    data_logger = logging.getLogger('data')
    data_logger.setLevel(config.DATA_LOG_LEVEL)
    data_logger.propagate = False
    data_handler = RotatingFileHandler(
        config.DATA_LOG_FILE,
        maxBytes=config.LOG_MAX_SIZE,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    data_handler.setFormatter(formatter)
    data_logger.addHandler(data_handler)

    # Third-party libs
    for lib in ['urllib3', 'httpcore']:
        logging.getLogger(lib).setLevel(config.DATA_LOG_LEVEL)
        logging.getLogger(lib).addHandler(data_handler)
