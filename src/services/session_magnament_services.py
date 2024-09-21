from flask import session, redirect, url_for
from functools import wraps
from src.database.database import mysql

# Función para restringir acceso a páginas que requieren login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged' not in session:
            return redirect(url_for('login.login_view'))
        return f(*args, **kwargs)
    return decorated_function

def obtener_perfil_usuario(nombre_usuario, id_roles):
    cur = None
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE nombre_usuario = %s AND id_roles = %s', (nombre_usuario, id_roles))
        return cur.fetchone()
    except Exception as e:
        print(f'Error al obtener perfil del usuario: {e}')
    finally:
        if cur:
            cur.close()

def CerrarSesion():
    session.pop('logged', None)
    session.pop('id', None)
    session.pop('id_roles', None)
    session.pop('conversacion', None)
    return redirect(url_for('login.login_view'))
