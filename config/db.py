import pymysql
from pymysql import Connection
from pymysql import cursors


def get_connection() -> Connection:
    try:
        connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="admin123",
            database="roommates",
            cursorclass=pymysql.cursors.Cursor,
            autocommit=True,
        )
        cur = connection.cursor()
        return connection
    except pymysql.err.OperationalError as e:
        print("Error: %d: %s" % (e.args[0], e.args[1]))
