from flask_mail import Mail
import logging

mail = Mail()

def init_mail(app):
    # Configuración del servidor de correo
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'deiderruiz00@gmail.com'
    app.config['MAIL_PASSWORD'] = 'wbld bbaf cnmn hysq'
    app.config['MAIL_DEFAULT_SENDER'] = 'deiderruiz00@gmail.com'

    # Intentar inicializar la app con el mail
    try:
        mail.init_app(app)
    except Exception as e:
        logging.error(f"Error al inicializar el correo: {e}")
        raise e
