from flask import url_for
from flask_mail import Message
from datetime import datetime
from src.database.database import mysql
from src.utils.email_config import mail

def obtener_horarios_formateados():
    cur = None
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM horarios ORDER BY FIELD(dia, "Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"), hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm')
        horarios = cur.fetchall()

        for horario in horarios:
            if horario['hora_inicio_am'] is not None:
                horario['hora_inicio_am'] = datetime.strptime(':'.join(str(horario['hora_inicio_am']).split(':')[:2]),
                                                              '%H:%M').strftime('%I:%M %p')
            if horario['hora_fin_am'] is not None:
                horario['hora_fin_am'] = datetime.strptime(':'.join(str(horario['hora_fin_am']).split(':')[:2]),
                                                           '%H:%M').strftime('%I:%M %p')
            if horario['hora_inicio_pm'] is not None:
                horario['hora_inicio_pm'] = datetime.strptime(':'.join(str(horario['hora_inicio_pm']).split(':')[:2]),
                                                              '%H:%M').strftime('%I:%M %p')
            if horario['hora_fin_pm'] is not None:
                horario['hora_fin_pm'] = datetime.strptime(':'.join(str(horario['hora_fin_pm']).split(':')[:2]),
                                                           '%H:%M').strftime('%I:%M %p')

        return horarios
    except Exception as e:
        print(f'Error al obtener horarios formateados: {e}')
    finally:
        if cur:
            cur.close()

def procesar_solicitud_cita(form):
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

    cur = None
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO citas (numero_id, nombres, apellidos, email, cellphone, publico, programa, semestre, fecha, hora, asunto, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "no leido")',
            (numero_id, nombres, apellidos, email, cellphone, publico, programa, semestre, fecha, hora, asunto))
        mysql.connection.commit()

        hora_str = hora.strftime('%H:%M:%S')
        hora_24 = datetime.strptime(hora_str, '%H:%M:%S')
        hora_12 = hora_24.strftime('%I:%M %p')

        solicitud_url = url_for('citas.Solicitudes', _external=True)
        msg = Message("Solicitud de Cita de Orientación Psicológica",
                      recipients=["deider_ruiz@uajs.edu.co"])
        msg.body = (f"Se ha recibido una nueva solicitud de cita de orientación psicológica.\n\n"
                    f"Detalles de la solicitud:\n\n"
                    f"Solicitante: {nombres} {apellidos}\n"
                    f"Correo electrónico: {email}\n"
                    f"Número de Telefono: {cellphone}\n"
                    f"Fecha y hora de la solicitud: {fecha} a las {hora_12}\n"
                    f"Asunto: {asunto}\n\n"
                    f"Por favor, revise esta solicitud lo antes posible.\n{solicitud_url}")
        mail.send(msg)
    except Exception as e:
        print(f'Error al procesar la solicitud de cita: {e}')
    finally:
        if cur:
            cur.close()
