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

# logger = logging.getLogger()
# logger.debug('often makes a very good meal of %s', 'visiting tourists')
# logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level=logging.DEBUG)
# logging.log(1, )
