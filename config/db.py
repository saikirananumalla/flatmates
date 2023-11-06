import pymysql
from pymysql import Connection

def getConnection() -> Connection :
    try:
        connection = pymysql.connect(host='localhost',
                                    user = 'root',
                                    password='password',
                                    database='roommates',
                                    cursorclass=pymysql.cursors.DictCursor,
                                    autocommit=True)
        cur = connection.cursor()
        return connection
    except pymysql.err.OperationalError as e:
        print('Error: %d: %s' % (e.args[0], e.args[1]))
        