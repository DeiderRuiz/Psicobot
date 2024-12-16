from flask import session, redirect, url_for, make_response
from functools import wraps
from src.database.database import mysql
from src.services.panel_usuario_service import limpiar_historial

# Función para restringir acceso a páginas que requieren login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged' not in session:
            return redirect(url_for('login.login_view'))
        return f(*args, **kwargs)
    return decorated_function

def obtener_perfil_usuario(idusers, id_roles):
    cur = None
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE idusers = %s AND id_roles = %s', (idusers, id_roles))
        return cur.fetchone()
    except Exception as e:
        print(f'Error al obtener perfil del usuario: {e}')
    finally:
        if cur:
            cur.close()

def verificar_permiso(idroles, idpermisos):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM rol_has_permiso WHERE idroles = %s AND idpermisos = %s", (idroles, idpermisos))
    resultado = cur.fetchone()
    return resultado is not None

def CerrarSesion():
    session.pop('logged', None)
    session.pop('id', None)
    session.pop('id_roles', None)
    session.pop('conversacion', None)
    session.clear()
    # Limpia el historial de conversación del chatbot, es para que la memoria no se mantenga entre sesiones
    limpiar_historial()
    response = make_response(redirect(url_for('login.login_view')))
    response.set_cookie('session', '', expires=0)
    return response
