from flask import url_for
from flask_mail import Message
from datetime import datetime
from src.database.database import mysql
from src.utils.email_config import mail

def verificar_disponibilidad(form):
    fecha = form.fecha.data
    hora = form.hora.data
    cur = mysql.connection.cursor()
    cur.execute('SELECT fecha, hora FROM citas WHERE fecha = %s AND hora = %s', (fecha, hora))
    return cur.fetchone()

def procesar_solicitud_cita(form, idusers):
    numero_id = form.numero_id.data
    nombres = form.nombres.data
    apellidos = form.apellidos.data
    email = form.email.data
    cellphone = form.cellphone.data
    publico = form.publico.data
    programa = form.programa.data
    semestre = form.semestre.data
    fecha = form.fecha.data
    hora = form.hora.data
    asunto = form.asunto.data

    cur = mysql.connection.cursor()
    cur.execute(
        'INSERT INTO citas (numero_id, nombres, apellidos, email, cellphone, publico, programa, semestre, fecha, hora, asunto, estado, progreso, idusers) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "no leido", "pendiente", %s)',
        (numero_id, nombres, apellidos, email, cellphone, publico, programa, semestre, fecha, hora, asunto, idusers))
    mysql.connection.commit()
    # Obtener el ID de la cita recién creada
    id_cita = cur.lastrowid

    hora_str = hora.strftime('%H:%M:%S')
    hora_24 = datetime.strptime(hora_str, '%H:%M:%S')
    hora_12 = hora_24.strftime('%I:%M %p')

    solicitud_url = url_for('detalleCita.detalle_cita_view', id=id_cita, _external=True)
    msg = Message("Nueva Solicitud de Cita de Orientación Psicológica",
                  recipients=["deider_ruiz@uajs.edu.co"])
    msg.body = (f"Hola,\n\n"
                f"Se ha recibido una nueva solicitud de cita de orientación psicológica. A continuación, se detallan los datos de la solicitud:\n\n"
                f"SOLICITANTE: {nombres} {apellidos}\n"
                f"CORREO ELECTRÓNICO: {email}\n"
                f"NÚMERO DE TELÉFONO: {cellphone}\n"
                f"FECHA Y HORA DE LA CITA {fecha} a las {hora_12}\n"
                f"ASUNTO: {asunto}\n\n"
                f"Por favor, revise esta solicitud lo antes posible:\n"
                f"{solicitud_url}\n\n"
                f"Saludos,\n"
                f"El equipo de Psicobot")
    mail.send(msg)
