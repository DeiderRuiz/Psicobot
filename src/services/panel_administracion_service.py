from src.database.database import mysql

def contar_solicitudes_no_leidas():
    cur = mysql.connection.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM citas WHERE estado = %s', ('no leido',))
        solicitudes = cur.fetchone()
        return solicitudes[0] if solicitudes else 0
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al contar las solicitudes no leídas: {e}")
        return 0
    finally:
        cur.close()
