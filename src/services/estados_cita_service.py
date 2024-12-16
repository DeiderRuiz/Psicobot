from flask import url_for
from flask_mail import Message
from datetime import time, datetime
from babel.dates import format_date
from src.database.database import mysql
from src.utils.email_config import mail

def cancelar_cita_db(id, idroles, motivo):
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, nombres, apellidos, email, cellphone, fecha, hora FROM citas WHERE id = %s', (id,))
    cita = cur.fetchone()

    if not cita:
        return False

    # Formatear la fecha y la hora
    fecha = format_date(datetime.combine(cita['fecha'], time()), 'd \'de\' MMMM\' de\' Y', locale='es_ES')
    hora_12 = (datetime.min + cita['hora']).time().strftime('%I:%M %p')

    cur.execute('UPDATE citas SET progreso = "cancelada" WHERE id = %s', (id,))
    mysql.connection.commit()

    if idroles == 2:
        solicitud_url = url_for('detalleCita.detalle_cita_view', id=cita['id'], _external=True)
        msg = Message("Cancelación de Cita de Orientación Psicológica",
                      recipients=["deider_ruiz@uajs.edu.co"])
        msg.body = (f"Hola,\n\n"
                    f"Un usuario ha cancelado su cita programada de orientación psicológica.\n\n"
                    f"SOLICITANTE: {cita['nombres']} {cita['apellidos']}\n"
                    f"FECHA Y HORA DE LA CITA: {fecha} a las {hora_12}\n\n"
                    f"Puedes consultar los detalles y el estado de las citas aquí:\n"
                    f"{solicitud_url}\n\n"
                    f"Saludos,\n"
                    f"Psicobot")
        mail.send(msg)
    elif idroles == 1:
        solicitud_url = url_for('solicitud.SolicitarCita', _external=True)
        msg = Message("Cancelación de Cita de Orientación Psicológica",
                      recipients=[cita['email']])
        msg.body = (f"Hola, {cita['nombres']} {cita['apellidos']}\n\n"
                    f"Lamentamos informarte que tu cita de orientación psicológica programada para el día {fecha} a las {hora_12} ha sido cancelada.\n\n"
                    f"Motivo de la cancelación: {motivo}\n\n"
                    f"Si deseas reprogramar tu cita, por favor visita nuestra plataforma en el siguiente enlace:\n"
                    f"{solicitud_url}\n\n"
                    f"Agradecemos tu comprensión y estamos aquí para apoyarte en lo que necesites.\n\n"
                    f"Saludos, Psicobot")
        mail.send(msg)

    return True

def cita_atendida_db(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE citas SET progreso = "atentida" WHERE id = %s', (id,))
    mysql.connection.commit()

    return True

def aceptar_cita_db(id, idroles, mensaje):
    cur = mysql.connection.cursor()
    cur.execute('SELECT id, nombres, apellidos, email, cellphone, fecha, hora FROM citas WHERE id = %s', (id,))
    cita = cur.fetchone()

    if not cita:
        return False

    # Formatear la fecha y la hora
    fecha = format_date(datetime.combine(cita['fecha'], time()), 'd \'de\' MMMM\' de\' Y', locale='es_ES')
    hora_12 = (datetime.min + cita['hora']).time().strftime('%I:%M %p')

    cur.execute('UPDATE citas SET progreso = "aceptada" WHERE id = %s', (id,))
    mysql.connection.commit()

    solicitud_url = url_for('solicitud.SolicitarCita', _external=True)
    msg = Message("Solicitud de Cita de Orientación Psicológica",
                  recipients=[cita['email']])
    msg.body = (f"Hola, {cita['nombres']} {cita['apellidos']}\n\n"
                f"Tu cita de orientación psicológica programada para el día {fecha} a las {hora_12} ha sido aceptada.\n\n"
                f"Motivo de la cancelación: {mensaje}\n\n"
                f"Si por motivos personales necesitas cancelar la cita, puedes solicitar una nueva en el siguiente enlace:\n"
                f"{solicitud_url}\n\n"
                f"Saludos, Psicobot")
    mail.send(msg)

    return True