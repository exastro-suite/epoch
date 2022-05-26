#   Copyright 2022 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from datetime import datetime as dtlogging
from logging import config, Handler, Formatter, LogRecord, LoggerAdapter, Filter

from flask import has_request_context, request as flrequest


# Filter
class RequireDebugFalse(Filter):

    def filter(self, record):
        """production env log filter setting
        """

        return not LOGGING['DEBUG']


class RequireDebugTrue(Filter):

    def filter(self, record):
        """development env log filter setting
        """

        return LOGGING['DEBUG']


# Format
class ExastroFormatter(Formatter):

    converter = dtlogging.fromtimestamp

    def formatTime(self, record, datefmt=None):
        """log datetime format
        """

        if not datefmt:
            datefmt = '%Y/%m/%d %H:%M:%S.%f'

        ct = self.converter(record.created)
        ct = ct.strftime(datefmt)

        return ct


# LogRecord
class ExastroLogRecord(LogRecord):

    def __init__(self, *args, **kwargs):
        """Add userid
        """

        super().__init__(*args, **kwargs)
        self.userid = '---'


# LogRecordFactory
class ExastroLogRecordFactory():

    def __init__(self, origin_factory, flask_req=None):
        """Add userid
        """

        self.userid         = '-'
        self.origin_factory = origin_factory
        self.flask_req      = flask_req


    def __call__(self, *args, **kwargs):
        """Get keycloak's user id
        """

        record = self.origin_factory(*args, **kwargs)
        record.userid = self.get_keycloak_userid()

        return record


    def get_keycloak_userid(self):
        """Get user id from Flask request
        """

        user_id = '-'

        if  has_request_context() \
        and hasattr(self.flask_req, 'headers') \
        and 'X-REMOTE-USER' in self.flask_req.headers:
            user_id = self.flask_req.headers['X-REMOTE-USER']
            idx = user_id.rfind('@')
            user_id = user_id[:idx]

        return user_id


# Logging settings
LOGGING = {
    'version' : 1,
    'disable_existing_loggers' : False, # or False
    'DEBUG' : False, # or False, For not Django
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
            'format' : '%(asctime)s %(levelname)s (%(userid)s) %(pathname)s(%(lineno)d) %(message)s',
        },
        'backyards' : {
            '()' : ExastroFormatter,
            'format' : '%(asctime)s %(levelname)s (%(process)s) %(pathname)s(%(lineno)d) %(message)s',
        },
    },
    'handlers' : {
        'console' : {
            'level' : 'DEBUG',
            'filters' : ['require_debug_false', ],
            'class' : 'logging.StreamHandler',
            'formatter' : 'verbose',
        },
        #'file_api' : {
        #    'level' : 'INFO',
        #    'filters' : ['require_debug_false', ],
        #    'class' : 'logging.handlers.RotatingFileHandler',
        #    'formatter' : 'verbose',
        #    'filename' : '/app/logs/api.log', # Your Logfile path
        #    'maxBytes' : 100 * 1024 * 1024,
        #    'backupCount' : 10,
        #},
        #'err_file_api' : {
        #    'level' : 'ERROR',
        #    'filters' : ['require_debug_false', ],
        #    'class' : 'logging.handlers.RotatingFileHandler',
        #    'formatter' : 'verbose',
        #    'filename' : '/app/logs/api_error.log', # Your Logfile path
        #    'maxBytes' : 100 * 1024 * 1024,
        #    'backupCount' : 10,
        #},
    },
    'loggers' : {
        'api' : {  # app name
            'handlers' : ['console', ],
            'propagate' : True,
            'level' : 'DEBUG',
        },
        'root' : {
            #'handlers' : ['console', 'file_api', 'err_file_api'],
            'handlers' : ['console', ],
            'propagate' : False,
            'level' : 'DEBUG',
        },
    },
}


