import os
import pymysql
from pymysql import Connection
from pymysql import cursors

#host = os.environ["DATABASE_HOST"]


def get_connection() -> Connection:
    try:
        connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="password",
            database="flatmates",
            cursorclass=pymysql.cursors.Cursor,
            autocommit=True,
        )
        return connection
    except pymysql.err.OperationalError as e:
        print(e)
