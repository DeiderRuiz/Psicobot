from flask import session
import bcrypt
from src.database.database import mysql

def obtener_usuario(nombre_usuario):
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM users WHERE nombre_usuario = %s OR email = %s', (nombre_usuario, nombre_usuario,))
        return cur.fetchone()
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al obtener el usuario: {e}")
        return None
    finally:
        cur.close()

def comprobar_password(password, hashed_password):
    return bcrypt.checkpw(password, hashed_password.encode('utf-8'))

def crear_sesion(account):
    try:
        session['logged'] = True
        session['id'] = account['idusers']
        session['id_roles'] = account['id_roles']
        session['nombre_usuario'] = account['nombre_usuario']
        session['email'] = account['email']
        session['conversacion'] = []
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al crear la sesión: {e}")
