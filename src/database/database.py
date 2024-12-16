from flask_mysqldb import MySQL
import logging

mysql = MySQL()

def init_app(app):
    try:
        mysql.init_app(app)
        mysql.host = app.config['MYSQL_HOST']
        mysql.user = app.config['MYSQL_USER']
        mysql.password = app.config['MYSQL_PASSWORD']
        mysql.db = app.config['MYSQL_DB']
        mysql.cursorclass = app.config['MYSQL_CURSORCLASS']
        logging.info("Conexión a la base de datos establecida con éxito")
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos: {e}")
