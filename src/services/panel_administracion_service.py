from src.database.database import mysql

def contar_solicitudes_no_leidas():
    cur = mysql.connection.cursor()
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(*) FROM citas WHERE estado = "no leido"')
        solicitudes = cur.fetchone()
        print(solicitudes)
        return solicitudes['COUNT(*)']
    except Exception as e:
        # Manejo de errores, registrar o manejar la excepción
        print(f"Error al contar las solicitudes no leídas: {e}")
        return 0
    finally:
        cur.close()
