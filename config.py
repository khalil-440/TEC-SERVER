import pymysql

def get_db():
    return pymysql.connect(
        host="100.76.221.96",
        user="tecadmin",
        password="tec123",
        database="monitoring_db",
        cursorclass=pymysql.cursors.DictCursor
    )
