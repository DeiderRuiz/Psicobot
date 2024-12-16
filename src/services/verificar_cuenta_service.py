from flask import url_for
from datetime import datetime, timedelta
from flask_mail import Message
from src.database.database import mysql
from src.utils.email_config import mail
from src.utils.tokens import generar_token

def token_verificacion(email, codigo):
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
    cur.execute('SELECT idusers FROM verificar_cuenta WHERE idusers = %s', (user_id,))
    existing_token = cur.fetchone()

    if existing_token:
        # Actualizar el token existente
        cur.execute(
            'UPDATE verificar_cuenta SET token=%s, created_at=%s, updated_at=%s, is_active=TRUE WHERE idusers=%s',
            (token, created_at, expires_at, user_id))
    else:
        # Insertar un nuevo token
        cur.execute(
            'INSERT INTO verificar_cuenta (token, idusers, created_at, updated_at) VALUES (%s, %s, %s, %s)',
            (token, user_id, created_at, expires_at))

    # Confirmar los cambios en la base de datos
    mysql.connection.commit()
    # Enviar el correo de recuperación
    verificar_codigo_url = url_for('codigo.VerificarCodigo', token=token, _external=True)
    enviar_correo_validacion(email, verificar_codigo_url, codigo)
    return True, verificar_codigo_url

def enviar_correo_validacion(email, verificar_codigo_url, codigo):
    msg = Message("Validación de cuenta", recipients=[email])
    msg.body = (f"Hola,\n\n"
                f"Gracias por registrarte en Psicobot. Para completar tu registro y validar tu cuenta, por favor el enlace:\n\n"
                f"{verificar_codigo_url}\n\n"
                f"Escribe el siguiente código\n\n"
                f"{codigo}\n\n"
                f"Ten en cuenta que este enlace es temporal y expirará en una hora.\n\n"
                f"Si no solicitaste este cambio, ignora este mensaje.\n\n"
                f"Saludos,\n"
                f"El equipo de Psicobot")
    mail.send(msg)
