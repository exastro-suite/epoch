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
