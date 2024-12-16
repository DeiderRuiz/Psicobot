import math
from datetime import time, datetime
from babel.dates import format_date
from src.database.database import mysql

def obtener_mis_citas(page_num, idusers):
    per_page = 5
    offset = (page_num - 1) * per_page

    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) FROM citas WHERE idusers = %s', (idusers,))
    numero_citas = cur.fetchone()['COUNT(*)']
    cur.execute('SELECT * FROM citas WHERE idusers = %s ORDER BY fecha DESC, hora DESC LIMIT %s OFFSET %s',
                (idusers, per_page, offset))
    citas = cur.fetchall()

    for cita in citas:
        cita['fecha'] = format_date(datetime.combine(cita['fecha'], time()), 'd \'de\' MMMM' '\' de\' Y',
                                    locale='es_ES')
        cita['hora'] = (datetime.min + cita['hora']).time().strftime('%I:%M %p')

    total_paginas = math.ceil(numero_citas / per_page)

    return citas, total_paginas
