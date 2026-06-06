import pymysql

def get_db():
    return pymysql.connect(
        host="127.0.0.1",
        user="tecadmin",
        password="tec123",
        database="monitoring_db",
        cursorclass=pymysql.cursors.DictCursor
    )
