from flask_mail import Mail
from dotenv import load_dotenv
import os
import logging

# Cargar las variables del archivo .env
load_dotenv()

mail = Mail()

def init_mail(app):
    # Configuración del servidor de correo
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    # Intentar inicializar la app con el mail
    try:
        mail.init_app(app)
    except Exception as e:
        logging.error(f"Error al inicializar el correo: {e}")
        raise e
