from flask import url_for
from datetime import datetime, timedelta
from flask_mail import Message
from src.database.database import mysql
from src.utils.email_config import mail
from src.utils.tokens import generar_token

def gestionar_recuperacion_contrasena(email):
    cur = mysql.connection.cursor()
    # Verificar si el usuario existe
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cur.fetchone()
    if not user:
        return False
    user_id = user['idusers']
    token = generar_token(email, secret_key='psychobot')
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(hours=1)

    # Verificar si ya existe un token de recuperación para el usuario
    cur.execute('SELECT idusers FROM password_reset_tokens WHERE idusers = %s', (user_id,))
    existing_token = cur.fetchone()

    if existing_token:
        # Actualizar el token existente
        cur.execute(
            'UPDATE password_reset_tokens SET token=%s, created_at=%s, expires_at=%s, is_active=TRUE WHERE idusers=%s',
            (token, created_at, expires_at, user_id))
    else:
        # Insertar un nuevo token
        cur.execute(
            'INSERT INTO password_reset_tokens (token, idusers, created_at, expires_at) VALUES (%s, %s, %s, %s)',
            (token, user_id, created_at, expires_at))

    # Confirmar los cambios en la base de datos
    mysql.connection.commit()
    # Enviar el correo de recuperación
    reset_url = url_for('password.ResetPassword', token=token, _external=True)
    enviar_correo_recuperacion(email, reset_url)
    return True

def enviar_correo_recuperacion(email, reset_url):
    msg = Message("Recuperación de contraseña", recipients=[email])
    msg.body = (f"Hola,\n\n"
                f"Has solicitado restablecer tu contraseña. Por favor, utiliza el siguiente enlace para hacerlo:\n\n"
                f"{reset_url}\n\n"
                f"Ten en cuenta que este enlace es temporal y expirará en una hora.\n\n"
                f"Si no solicitaste este cambio, ignora este mensaje.\n\n"
                f"Saludos,\n"
                f"El equipo de Psicobot")
    mail.send(msg)
