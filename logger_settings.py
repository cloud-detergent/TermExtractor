import logging
from logging.config import dictConfig


def setup():
    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', filename='data/journal.log', level=logging.DEBUG)
    logger = logging.getLogger()
    logger.info("Настройка модуля логирования произведена")
    return None
    logging_config = dict(
        version=1,
        formatters={
            'f': {'format':
                  '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
            },
        handlers={
            'h': {'class': 'logging.StreamHandler',
                  'formatter': 'f',
                  'level': logging.DEBUG}
            },
        root={
            'handlers': ['h'],
            'level': logging.DEBUG,
            },
        filename="data/journal.log"
    )

    dictConfig(logging_config)
    logger = logging.getLogger()
    logger.info("Настройка модуля логирования произведена")


def get_logger(
        LOG_FORMAT     = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        LOG_NAME       = '',
        LOG_FILE_INFO  = 'data/journal.log',
        LOG_FILE_ERROR = 'data/journal.err'):

    log = logging.getLogger(LOG_NAME)
    log_formatter = logging.Formatter(LOG_FORMAT)

    # comment this to suppress console output
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    log.addHandler(stream_handler)

    file_handler_info = logging.FileHandler(LOG_FILE_INFO, mode='w')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.INFO)
    log.addHandler(file_handler_info)

    file_handler_error = logging.FileHandler(LOG_FILE_ERROR, mode='w')
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.ERROR)
    log.addHandler(file_handler_error)

    log.setLevel(logging.INFO)

    return log

# logger = logging.getLogger()
# logger.debug('often makes a very good meal of %s', 'visiting tourists')
# logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level=logging.DEBUG)
# logging.log(1, )
