from datetime import datetime
import bcrypt
from src.database.database import mysql

def obtener_usuario(email):
    cur = mysql.connection.cursor()
    cur.execute('SELECT idusers FROM users WHERE email = %s', (email,))
    return cur.fetchone()

def actualizar_password(token, password, idusers):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM password_reset_tokens WHERE token = %s', (token,))
    infoToken = cur.fetchone()
    if infoToken:
        rightNow = datetime.utcnow()
        activo = infoToken['is_active']
        expirado = infoToken['expires_at']
        if activo and expirado > rightNow:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cur.execute('UPDATE users SET password = %s WHERE idusers = %s', (hashed_password, idusers,))
            cur.execute('UPDATE password_reset_tokens SET is_active = False WHERE idusers = %s', (idusers,))
            mysql.connection.commit()
            return True
    return False
