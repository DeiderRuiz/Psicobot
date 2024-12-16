from flask import flash, url_for
import math
from datetime import time, datetime, timedelta
from babel.dates import format_date
from src.database.database import mysql

def obtener_citas(page_num, buscar, estudiante, egresado, egresado_no_graduado, docente, administrativo, pendiente, aceptada, cancelada, atendida):
    per_page = 25
    offset = (page_num - 1) * per_page

    # Construir filtro de búsqueda general
    buscar = f"%{buscar or ''}%"
    params = [buscar, buscar, buscar, buscar, buscar]

    # Condiciones para el filtro 'publico'
    publico_condiciones = []
    if estudiante:
        publico_condiciones.append("publico = %s")
        params.append("estudiante")
    if egresado:
        publico_condiciones.append("publico = %s")
        params.append("egresado")
    if egresado_no_graduado:
        publico_condiciones.append("publico = %s")
        params.append("egresado no graduado")
    if docente:
        publico_condiciones.append("publico = %s")
        params.append("docente")
    if administrativo:
        publico_condiciones.append("publico = %s")
        params.append("administrativo")

    # Condiciones para el filtro 'progreso'
    progreso_condiciones = []
    if pendiente:
        progreso_condiciones.append("progreso = %s")
        params.append("pendiente")
    if aceptada:
        progreso_condiciones.append("progreso = %s")
        params.append("aceptada")
    if cancelada:
        progreso_condiciones.append("progreso = %s")
        params.append("cancelada")
    if atendida:
        progreso_condiciones.append("progreso = %s")
        params.append("atendida")

    # Crear consulta base
    query_base = '''SELECT COUNT(*) FROM citas WHERE (nombres LIKE %s OR apellidos LIKE %s OR email LIKE %s OR cellphone LIKE %s OR asunto LIKE %s)'''
    query_select = '''SELECT * FROM citas WHERE (nombres LIKE %s OR apellidos LIKE %s OR email LIKE %s OR cellphone LIKE %s OR asunto LIKE %s)'''

    # Aplicar condiciones de 'publico' si existen
    if publico_condiciones:
        query_base += " AND (" + " OR ".join(publico_condiciones) + ")"
        query_select += " AND (" + " OR ".join(publico_condiciones) + ")"

    # Aplicar condiciones de 'progreso' si existen
    if progreso_condiciones:
        query_base += " AND (" + " OR ".join(progreso_condiciones) + ")"
        query_select += " AND (" + " OR ".join(progreso_condiciones) + ")"

    # Orden y límites
    query_select += ''' ORDER BY 
                        CASE WHEN estado = "no leido" THEN 0 
                             WHEN estado = "leido" THEN 1 
                        END, 
                        fecha DESC, 
                        hora DESC, 
                        CASE progreso 
                            WHEN 'pendiente' THEN 0 
                            WHEN 'aceptada' THEN 1 
                            WHEN 'atendida' THEN 2 
                            WHEN 'cancelada' THEN 3 
                        END 
                        LIMIT %s OFFSET %s'''
    params.extend([per_page, offset])

    print("Consulta COUNT SQL:", query_base)
    print("Parámetros COUNT:", params[:len(params) - 2])
    print("Consulta SELECT SQL:", query_select)
    print("Parámetros SELECT:", params)

    # Ejecutar consultas
    cursor = mysql.connection.cursor()
    cursor.execute(query_base, params[:len(params) - 2])  # Excluir 'per_page' y 'offset' para COUNT
    total_citas = cursor.fetchone()['COUNT(*)']

    cur = mysql.connection.cursor()
    cur.execute(query_select, params)
    citas = cur.fetchall()

    total_paginas = math.ceil(total_citas / per_page)

    for cita in citas:
        cita['fecha'] = format_date(datetime.combine(cita['fecha'], time()), 'd MMM', locale='es_ES')
        cita['hora'] = (datetime.min + cita['hora']).time().strftime('%I:%M %p')

    return citas, total_paginas

def alerta_de_citas():
    ahora = datetime.now()

    # Consulta para obtener todas las citas pendientes o aceptadas
    query = '''
        SELECT * FROM citas 
        WHERE progreso IN ('pendiente', 'aceptada')
    '''
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    citas = cursor.fetchall()
    alertas = []

    for cita in citas:
        # Convertir la hora de timedelta a time
        hora_cita = (datetime.min + cita['hora']).time()
        cita_fecha_hora = datetime.combine(cita['fecha'], hora_cita)

        enlace_cita = url_for('detalleCita.detalle_cita_view', id=cita['id'])

        # Flash para cita pendiente dentro del rango
        if cita['progreso'] == 'pendiente' and ahora >= cita_fecha_hora - timedelta(hours=1) and ahora <= cita_fecha_hora:
            hora_cita_12h = hora_cita.strftime('%I:%M %p')
            alertas.append({
                'category': 'warning',
                'message': f"Tienes una cita pendiente con {cita['nombres']} {cita['apellidos']} a las {hora_cita_12h}. Click aquí para ver los detalles.",
                'enlace': enlace_cita
            })

        # Flash para cita aceptada que ya pasó
        elif cita['progreso'] == 'aceptada' and ahora > cita_fecha_hora:
            alertas.append({
                'category': 'warning',
                'message': f"La cita con {cita['nombres']} {cita['apellidos']} ha pasado. ¿Fue atendida? Click aquí para ver los detalles.",
                'enlace': enlace_cita
            })
    return alertas

def obtener_detalle_cita(cita_id):
    cur = mysql.connection.cursor()

    # Actualiza el estado de la cita a "leido"
    cur.execute('UPDATE citas SET estado = "leido" WHERE id = %s', (cita_id,))
    mysql.connection.commit()

    # Selecciona toda la información de la cita
    cur.execute('SELECT * FROM citas WHERE id = %s', (cita_id,))
    cita = cur.fetchone()

    # Cambia el formato de la fecha y hora
    if cita:
        cita['fecha'] = format_date(datetime.combine(cita['fecha'], time()), 'd \'de\' MMMM' '\' de\' Y',
                                    locale='es_ES')
        cita['hora'] = (datetime.min + cita['hora']).time().strftime('%I:%M %p')

    return cita


def obtener_detalle_mi_cita(cita_id, idusers):
    cur = mysql.connection.cursor()

    # Selecciona toda la información de la cita
    cur.execute('SELECT * FROM citas WHERE id = %s AND idusers = %s', (cita_id, idusers))
    mi_cita = cur.fetchone()

    # Cambia el formato de la fecha y hora
    if mi_cita:
        mi_cita['fecha'] = format_date(datetime.combine(mi_cita['fecha'], time()), 'd \'de\' MMMM' '\' de\' Y',
                                       locale='es_ES')
        mi_cita['hora'] = (datetime.min + mi_cita['hora']).time().strftime('%I:%M %p')

    return mi_cita
