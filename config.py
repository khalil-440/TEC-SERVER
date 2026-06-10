import os
import pymysql

def get_db():

    return pymysql.connect(
        host="zephyr.proxy.rlwy.net",
        user="root",
        password="lbQeVgmlGdZvcrxOXkkpVEAcmGSsILJR",
        database="railway",
        port=34161,
        cursorclass=pymysql.cursors.DictCursor
    )
