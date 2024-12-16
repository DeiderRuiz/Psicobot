from src.database.database import mysql
from datetime import datetime, timedelta
import bcrypt
import random
from src.services.verificar_cuenta_service import token_verificacion

def comprobar_email(email):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    return cur.fetchone()

def generar_codigo_verificacion():
    return '{:06d}'.format(random.randint(0, 999999))

def registrar_usuario(nombres, apellidos, email, password, codigo):
    cur = mysql.connection.cursor()
    print(codigo)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_code = bcrypt.hashpw(codigo.encode('utf-8'), bcrypt.gensalt())
    fecha_expiracion = datetime.now() + timedelta(hours=1)
    cur.execute('INSERT INTO users (nombres, apellidos, email, password, codigo_verificacion, fecha_expiracion, verificado, id_roles) VALUES (%s, %s, %s, %s, %s, %s, %s, "2")',
                (nombres, apellidos, email, hashed_password, hashed_code, fecha_expiracion, False, ))
    mysql.connection.commit()
    return cur.lastrowid

