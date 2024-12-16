from flask import session
import bcrypt
from src.database.database import mysql

def obtener_usuario(email):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    usuario = cur.fetchone()
    if not usuario:
        return usuario, None
    if usuario['verificado'] == 1:
        return usuario, True
    else:
        return usuario, False

def comprobar_password(password, hashed_password):
    return bcrypt.checkpw(password, hashed_password.encode('utf-8'))

def crear_sesion(account):
    session['logged'] = True
    session['id'] = account['idusers']
    session['id_roles'] = account['id_roles']
    session['nombres'] = account['nombres']
    session['apellidos'] = account['apellidos']
    session['email'] = account['email']
    session['conversacion'] = []
