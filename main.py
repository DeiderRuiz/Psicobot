# IMPORTACIONES
from flask import Flask, session
from flask_talisman import Talisman
import os
from dotenv import load_dotenv
from src.database.database import mysql
from src.utils.email_config import init_mail
from src.routes.views import views
from src.routes.auth.login import login
from src.routes.auth.session_managment import logout
from src.routes.auth.register import registro
from src.routes.auth.forbidden_password import forbidden
from src.routes.auth.reset_password import password
from src.routes.auth.verificar_codigo import codigo
from src.routes.private.panel_administracion import panel_admin
from src.routes.private.panel_usuario import user
from src.routes.private.perfil import profile
from src.routes.private.horarios import horario, eliminar_horarios
from src.routes.private.solicitar_cita import solicitud
from src.routes.private.gestionar_citas import gestionar_cita
from src.routes.private.estados_cita import cancelar_citas, atender_citas, aceptar_citas
from src.routes.private.solicitudes import citas
from src.routes.private.detalles_cita import detalleCita

# Cargar las variables del archivo .env
load_dotenv()

# LLAVE de la aplicación
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'  # Convertir a booleano
app.config['HOST'] = os.getenv('FLASK_HOST', '0.0.0.0')
app.config['PORT'] = int(os.getenv('FLASK_PORT', 5000))

# Define una política de seguridad de contenido
content_security_policy = {
    'default-src': ["'self'"],
    'script-src': ["'self'", 'https://unpkg.com', 'https://ajax.googleapis.com', "'unsafe-eval'"],
    # 'style-src': ["'self'", 'https://fonts.googleapis.com', "'unsafe-inline'"],
    'style-src': ["'self'", 'https://fonts.googleapis.com'],
    'font-src': ["'self'", 'https://fonts.gstatic.com'],
    'img-src': ["'self'", 'data:'],
    'connect-src': ["'self'"],
    'frame-ancestors': ["'none'"],
    'form-action': ["'self'"]
}
Talisman(app, content_security_policy=content_security_policy)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS')

# Conectar a la base de datos
mysql.init_app(app)
# Conectar al servidor de correo electrónico
init_mail(app)


# Función para hacer permanente un sesión
@app.before_request
def make_session_permanent():
    session.permanent = True


# VISTAS
# Registro del Blueprint
app.register_blueprint(views)
# llamar al login
app.register_blueprint(login)
# llamar al register
app.register_blueprint(registro)
# llamar al cierre de sesión
app.register_blueprint(logout)
# llamar al restablecimiento de contraseña
app.register_blueprint(forbidden)
app.register_blueprint(password)
app.register_blueprint(codigo)
# llamar al panel de administración
app.register_blueprint(panel_admin)
# llamar al panel de los horarios
app.register_blueprint(horario)
app.register_blueprint(eliminar_horarios)
# llamar al panel de administración
app.register_blueprint(citas)
app.register_blueprint(detalleCita)
# llamar al panel de usuario
app.register_blueprint(user)
# llamar a la solicitud de cita
app.register_blueprint(solicitud)
app.register_blueprint(gestionar_cita)
app.register_blueprint(cancelar_citas)
app.register_blueprint(atender_citas)
app.register_blueprint(aceptar_citas)
# llamar al perfil
app.register_blueprint(profile)

# Verifica que el Script actual se ejecute de forma directa, en lugar decuando se importa algún modulo
# permite la ejecución de múltiples solicitudes simultáneamente
if __name__ == '__main__':
    # Inicia la app de Flask con las variables de configuración
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'], threaded=True)
