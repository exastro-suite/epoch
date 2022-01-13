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

import json
import mysql

import globals

class dbconnector:
    """MySQL接続クラス
    """
    def __enter__(self):
        import mysql.connector
        self.connect = mysql.connector.connect(
          host    = globals.config["MYSQL_HOST"],
          port    = globals.config["MYSQL_PORT"],
          database= globals.config['MYSQL_DATABASE'],
          user    = globals.config["MYSQL_USER"],
          password  = globals.config["MYSQL_PASSWORD"]
        )
        self.connect.ping(reconnect=True)
        self.connect.autocommit = False
        return self.connect
    
    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type is None:
            #globals.logger.debug('dbconnector.__exit__.commit')
            self.connect.commit()
        else:
            #globals.logger.debug('dbconnector.__exit__.rollback')
            self.connect.rollback()
        self.connect.close()


class dbcursor:
    """MySQLカーソルクラス
    """
    def __init__(self,db):
        self.db = db

    def __enter__(self):
        self.cursor = self.db.cursor(dictionary=True)
        return self.cursor
    
    def __exit__(self, exception_type, exception_value, traceback):
        #globals.logger.debug('dbcursor.__exit__')
        self.cursor.close()
