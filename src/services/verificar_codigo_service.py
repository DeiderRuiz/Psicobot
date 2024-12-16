from datetime import datetime, timedelta
import bcrypt
from src.database.database import mysql

def obtener_usuario(email):
    cur = mysql.connection.cursor()
    cur.execute('SELECT idusers FROM users WHERE email = %s', (email,))
    return cur.fetchone()

def verificar_codigo(token, codigo, idusers):
    print(token, codigo, idusers)
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM verificar_cuenta WHERE token = %s', (token,))
    infoToken = cur.fetchone()
    if infoToken:
        rightNow = datetime.utcnow()
        activo = infoToken['is_active']
        expirado = infoToken['updated_at']
        if activo and expirado > rightNow:
            cur.execute('SELECT * FROM users WHERE idusers = %s', (idusers,))
            codigo_verificado = cur.fetchone()
            if codigo_verificado:
                hashed_code = codigo_verificado['codigo_verificacion']
                if bcrypt.checkpw(codigo.encode('utf-8'), hashed_code.encode('utf-8')):
                    if codigo_verificado['verificado'] == 1:
                        return False, 'La cuenta ya ha sido verificada previamente.'
                    cur.execute('UPDATE verificar_cuenta SET is_active = %s WHERE idusers = %s', (False, idusers, ))
                    cur.execute('UPDATE users SET verificado = %s WHERE idusers = %s', (True, idusers,))
                    mysql.connection.commit()
                    return True, None
                else:
                    return False, 'Código de verificación incorrecto.'
            else:
                return False, 'Usuario no encontrado.'
        else:
            return False, 'Token expirado o inactivo.'
    else:
        return False, 'Token inválido.'

def crear_nuevo_codigo(idusers, nuevoCodigo):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE idusers = %s', (idusers,))
    codigo_verificado = cur.fetchone()
    if codigo_verificado['verificado'] == 1:
        return False, 'La cuenta ya ha sido verificada previamente.'
    new_hashed_code = bcrypt.hashpw(nuevoCodigo.encode('utf-8'), bcrypt.gensalt())
    fecha_expiracion = datetime.now() + timedelta(hours=1)
    cur.execute(
        'UPDATE users SET codigo_verificacion=%s, fecha_expiracion=%s WHERE idusers=%s',
        (new_hashed_code, fecha_expiracion, idusers))
    mysql.connection.commit()
    return True, 'El nuevo código se creó correctamente.'
