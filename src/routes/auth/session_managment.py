from flask import Blueprint
from src.services.session_magnament_services import CerrarSesion

logout = Blueprint('logout', __name__)

@logout.route('/CerrarSesion')
def cerrar_sesion():
    return CerrarSesion()
