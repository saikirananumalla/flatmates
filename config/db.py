import os
import pymysql
from pymysql import Connection
from pymysql import cursors

host = os.environ["DATABASE_HOST"]


def get_connection() -> Connection:
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user="root",
            password="admin123",
            database="roommates",
            cursorclass=pymysql.cursors.Cursor,
            autocommit=True,
        )
        return connection
    except pymysql.err.OperationalError as e:
        print(e)
