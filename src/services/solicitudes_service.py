from datetime import time, datetime
from babel.dates import format_date
from src.database.database import mysql

def obtener_citas():
    cur = None
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM citas ORDER BY estado DESC, fecha ASC, hora ASC')
        citas = cur.fetchall()

        for cita in citas:
            cita['fecha'] = format_date(datetime.combine(cita['fecha'], time()), 'd MMM', locale='es_ES')
            cita['hora'] = (datetime.min + cita['hora']).time().strftime('%I:%M %p')

        citas_no_leidas = [cita for cita in citas if cita['estado'] == "no leido"]
        citas_leidas = [cita for cita in citas if cita['estado'] == "leido"]

        return citas_no_leidas, citas_leidas
    except Exception as e:
        print(f'Error al obtener citas: {e}')
    finally:
        if cur:
            cur.close()

def obtener_detalle_cita(cita_id):
    cur = None
    try:
        cur = mysql.connection.cursor()

        # Actualiza el estado de la cita a "leido"
        cur.execute('UPDATE citas SET estado = "leido" WHERE id = %s', (cita_id,))
        mysql.connection.commit()

        # Selecciona toda la información de la cita
        cur.execute('SELECT * FROM citas WHERE id = %s', (cita_id,))
        cita = cur.fetchone()

        # Cambia el formato de la fecha y hora
        if cita:
            cita['fecha'] = format_date(datetime.combine(cita['fecha'], time()), 'd \'de\' MMMM', locale='es_ES')
            cita['hora'] = (datetime.min + cita['hora']).time().strftime('%I:%M %p')

        return cita
    except Exception as e:
        print(f'Error al obtener el detalle de la cita: {e}')
    finally:
        if cur:
            cur.close()
