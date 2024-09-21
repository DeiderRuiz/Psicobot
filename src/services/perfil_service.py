from flask import flash
import bcrypt
from src.database.database import mysql

def actualizar_perfil(idusers, nombre_usuario, email):
    cur = None
    try:
        cur = mysql.connection.cursor()
        # Verificar si el nuevo nombre de usuario ya existe
        cur.execute('SELECT * FROM users WHERE nombre_usuario = %s', (nombre_usuario,))
        existing_user = cur.fetchone()
        if existing_user and existing_user['idusers'] != idusers:
            flash('El nombre de usuario ya existe, intenta con otro diferente', 'error')
        else:
            cur.execute('SELECT * FROM password_reset_tokens WHERE idusers = %s', (idusers,))
            resultado = cur.fetchone()
            if resultado is None:
                cur.execute('UPDATE users SET nombre_usuario = %s, email = %s WHERE idusers = %s',
                            (nombre_usuario, email, idusers))
            else:
                cur.execute('UPDATE users SET nombre_usuario = %s, email = %s WHERE idusers = %s',
                            (nombre_usuario, email, idusers))
                cur.execute('UPDATE password_reset_tokens SET is_active = False WHERE idusers = %s', (idusers,))
            mysql.connection.commit()
            flash('¡Perfil actualizado! Es posible que los cambios tarden en mostrarse.', 'success')
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        flash('Error al actualizar el perfil: {}'.format(e), 'error')
    finally:
        if cur:
            cur.close()

def cambiar_contrasena(idusers, password):
    cur = None
    try:
        password = password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute('UPDATE users SET password = %s WHERE idusers = %s', (hashed_password, idusers))
        mysql.connection.commit()
        flash('Contraseña cambiada con éxito', 'success')
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        flash('Error al cambiar la contraseña: {}'.format(e), 'error')
    finally:
        if cur:
            cur.close()

def borrar_cuenta(idusers):
    cur = None
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM password_reset_tokens WHERE idusers = %s', (idusers,))
        resultado = cur.fetchone()
        if resultado is None:
            cur.execute('DELETE FROM users WHERE idusers = %s', (idusers,))
        else:
            cur.execute('DELETE FROM password_reset_tokens WHERE idusers = %s', (idusers,))
            cur.execute('DELETE FROM users WHERE idusers = %s', (idusers,))
        mysql.connection.commit()
        flash('Cuenta borrada con éxito', 'success')
    except Exception as e:
        if mysql.connection:
            mysql.connection.rollback()
        flash('Error al borrar la cuenta: {}'.format(e), 'error')
    finally:
        if cur:
            cur.close()
