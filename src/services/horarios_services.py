from datetime import datetime
from src.database.database import mysql

def obtener_horarios():
    cur = mysql.connection.cursor()
    try:
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
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al obtener los horarios: {e}")
        return []
    finally:
        cur.close()

def actualizar_o_insertar_horario(dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm):
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT dia FROM horarios WHERE dia = %s', (dia,))
        theDay = cur.fetchone()

        if theDay:
            cur.execute(
                'UPDATE horarios SET hora_inicio_am = %s, hora_fin_am = %s, hora_inicio_pm = %s, hora_fin_pm = %s WHERE dia = %s',
                (hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm, dia))
            mensaje = 'Se ha actualizado el horario de atención correctamente'
            tipo = 'success'
        else:
            cur.execute(
                'INSERT INTO horarios (dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm) VALUES (%s, %s, %s, %s, %s)',
                (dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm))
            mensaje = 'Se ha agregado un nuevo horario de atención correctamente'
            tipo = 'success'

        mysql.connection.commit()
        return mensaje, tipo
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al actualizar o insertar el horario: {e}")
        return 'Ocurrió un error al actualizar o insertar el horario', 'error'
    finally:
        cur.close()

def eliminar_horario_bd(dia):
    cur = mysql.connection.cursor()
    try:
        cur.execute('DELETE FROM horarios WHERE dia = %s', (dia,))
        mysql.connection.commit()
        return 'Se ha eliminado el horario de atención correctamente', 'success'
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al eliminar el horario: {e}")
        return 'Ocurrió un error al eliminar el horario', 'error'
    finally:
        cur.close()
