# coding=utf-8
from log_helper import LogHelper
import pymysql.cursors

class MySqlHelper:
    
    def __init__(self, host, port, dbName, user, password):
        LogHelper.log("created")
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._dbName = dbName
        self._connection = pymysql.connect(
            host = self._host,
            user = self._user,
            password = self._password,
            db = self._dbName,
            charset = 'utf8mb4',
            cursorclass = pymysql.cursors.DictCursor)

    def close(self):
        self._connection.close()

    def executeOne(self, sql, params):
        with self._connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, params)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        self._connection.commit()

    def queryOne(self, sql, params):
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return row

    def queryMany(self, sql, params, size):
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchmany(size)
            return rows

if __name__ == '__main__':
    try:
        helper = MySqlHelper('localhost', 3306, 'traffic', 'wp', 'wp', )
        sql = "INSERT INTO `node`(`title`, `finger`, `historyPath`, `position`, `region`, `createTime`, `updateTime`, `state`, `errorCount`, `pathOrder`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        helper.executeOne(sql, ('1', 'bbbbb', 'history path', '45.79.95.201', 'US', '2018-05-07 01:00:00', '2018-05-07 01:00:00', 'OK', 0, 'EXIT'))

        sql = 'SELECT title, finger, historyPath, position, region, createTime, updateTime, state, errorCount, pathOrder FROM node WHERE finger = %s'
        doc = helper.queryOne(sql, ('bbbbb'))
        print ('doc={0}'.format(doc))
    finally:
        helper.close()
        