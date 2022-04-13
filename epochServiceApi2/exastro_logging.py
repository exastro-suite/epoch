import datetime
from logging import config, Handler, Formatter, LogRecord, Filter


class RequireDebugFalse(Filter):

    def filter(self, record):

        return not LOGGING['DEBUG']


class RequireDebugTrue(Filter):

    def filter(self, record):

        return LOGGING['DEBUG']


class ExastroFormatter(Formatter):

    converter = datetime.datetime.fromtimestamp

    def format(self, record):

        record.userid = 0
        record.logid  = None

        return super().format(record)


    def formatTime(self, record, datefmt=None):

        if not datefmt:
            datefmt = '%Y/%m/%d %H:%M:%S.%f'

        ct = self.converter(record.created)
        ct = ct.strftime(datefmt)

        return ct


class LogRecordExtension(LogRecord):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.userid = 0
        self.logid  = '-'


LOGGING = {
    'version' : 1,
    'disable_existing_loggers' : False, # or False
    'DEBUG' : True, # or False, For not Django
    'filters' : {
        'require_debug_false' : {
            '()' : 'exastro_logging.RequireDebugFalse',
        },
        'require_debug_true' : {
            '()' : 'exastro_logging.RequireDebugTrue',
        },
    },
    'formatters' : {
        'verbose' : {
            '()' : ExastroFormatter,
            'format' : '%(asctime)s %(levelname)s (%(userid)s) %(filename)s(%(lineno)d) [%(logid)s] %(message)s',
        },
        'backyards' : {
            '()' : ExastroFormatter,
            'format' : '%(asctime)s %(levelname)s (%(process)s) %(filename)s(%(lineno)d) [%(logid)s] %(message)s',
        },
    },
    'handlers' : {
        'console' : {
            'level' : 'DEBUG',
            'filters' : ['require_debug_true', ],
            'class' : 'logging.StreamHandler',
            'formatter' : 'verbose',
        },
        'file_api' : {
            'level' : 'INFO',
            'filters' : ['require_debug_false', ],
            'class' : 'logging.handlers.RotatingFileHandler',
            'formatter' : 'verbose',
            'filename' : '/app/logs/api.log', # Your Logfile path
            'maxBytes' : 100 * 1024 * 1024,
            'backupCount' : 10,
        },
        'err_file_api' : {
            'level' : 'ERROR',
            'filters' : ['require_debug_false', ],
            'class' : 'logging.handlers.RotatingFileHandler',
            'formatter' : 'verbose',
            'filename' : '/app/logs/api_error.log', # Your Logfile path
            'maxBytes' : 100 * 1024 * 1024,
            'backupCount' : 10,
        },
    },
    'loggers' : {
        'api' : {  # app name
            'handlers' : ['console', ],
            'propagate' : True,
            'level' : 'DEBUG',
        },
        'root' : {  # app name
            'handlers' : ['console', ],
            'propagate' : False,
            'level' : 'DEBUG',
        },
    },
}


#config.dictConfig(LOGGING)


