from flask import flash
import bcrypt
from src.database.database import mysql

def actualizar_perfil(idusers, nombres, apellidos, email):
    cur = mysql.connection.cursor()
    # Verificar si el nuevo nombre de usuario ya existe
    cur.execute('SELECT * FROM users WHERE idusers = %s', (idusers,))
    existing_user = cur.fetchone()
    if existing_user and existing_user['idusers'] != idusers:
        flash('El nombre de usuario ya existe. Intenta con uno diferente.', 'error')
    else:
        cur.execute('SELECT * FROM password_reset_tokens WHERE idusers = %s', (idusers,))
        resultado = cur.fetchone()
        if resultado is None:
            cur.execute('UPDATE users SET nombres = %s, apellidos = %s, email = %s WHERE idusers = %s',
                        (nombres, apellidos, email, idusers))
        else:
            cur.execute('UPDATE users SET nombres = %s, apellidos = %s, email = %s WHERE idusers = %s',
                        (nombres, apellidos, email, idusers))
            cur.execute('UPDATE password_reset_tokens SET is_active = False WHERE idusers = %s', (idusers,))
        mysql.connection.commit()
        flash('¡Perfil actualizado! Es posible que los cambios tarden en reflejarse', 'success')

def cambiar_contrasena(idusers, password):
    password = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    cur = mysql.connection.cursor()
    cur.execute('UPDATE users SET password = %s WHERE idusers = %s', (hashed_password, idusers))
    mysql.connection.commit()
    flash('Contraseña cambiada con éxito.', 'success')

def borrar_cuenta(idusers):
    cur = mysql.connection.cursor()
    cur.execute('''
            UPDATE citas
            SET numero_id = %s,
                nombres = %s,
                apellidos = %s,
                email = %s,
                cellphone = %s
            WHERE idusers = %s
        ''', ('0000000000', 'ANÓNIMO', 'ANÓNIMO', 'anonimo@ejemplo.com', '0000000000', idusers))
    cur.execute('DELETE FROM users WHERE idusers = %s', (idusers,))
    mysql.connection.commit()
    flash('Cuenta borrada con éxito.', 'success')
