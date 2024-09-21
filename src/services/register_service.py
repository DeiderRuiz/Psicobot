from src.database.database import mysql
import bcrypt

def comprobar_usuario(nombre_usuario):
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM users WHERE nombre_usuario = %s', (nombre_usuario,))
        return cur.fetchone()
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al comprobar el usuario: {e}")
        return None
    finally:
        cur.close()

def comprobar_email(email):
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        return cur.fetchone()
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al comprobar el email: {e}")
        return None
    finally:
        cur.close()

def registrar_usuario(nombre_usuario, email, password):
    cur = mysql.connection.cursor()
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute('INSERT INTO users (nombre_usuario, email, password, id_roles) VALUES (%s, %s, %s, "2")', (nombre_usuario, email, hashed_password,))
        mysql.connection.commit()
        return cur.lastrowid
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al registrar el usuario: {e}")
        return None
    finally:
        cur.close()
