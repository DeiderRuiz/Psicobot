from datetime import datetime
from src.database.database import mysql

def obtener_horarios():
    cur = mysql.connection.cursor()
    cur.execute(
        'SELECT * FROM horarios ORDER BY FIELD(dia, "Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"), hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm'
    )
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

def actualizar_o_insertar_horario(dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm):
    cur = mysql.connection.cursor()
    cur.execute('SELECT dia FROM horarios WHERE dia = %s', (dia,))
    theDay = cur.fetchone()

    if theDay:
        cur.execute(
            'UPDATE horarios SET hora_inicio_am = %s, hora_fin_am = %s, hora_inicio_pm = %s, hora_fin_pm = %s WHERE dia = %s',
            (hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm, dia))
        mensaje = 'El horario de atención se ha actualizado correctamente.'
        tipo = 'success'
    else:
        cur.execute(
            'INSERT INTO horarios (dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm) VALUES (%s, %s, %s, %s, %s)',
            (dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm))
        mensaje = 'Se ha agregado correctamente un nuevo horario de atención'
        tipo = 'success'

    mysql.connection.commit()
    return mensaje, tipo

def eliminar_horario_bd(dia):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM horarios WHERE dia = %s', (dia,))
    mysql.connection.commit()
