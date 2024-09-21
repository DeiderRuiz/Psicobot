from flask import Blueprint, render_template, session
from src.services.session_magnament_services import obtener_perfil_usuario, login_required
from src.services.solicitudes_service import obtener_detalle_cita

detalleCita = Blueprint('detalleCita', __name__)

@detalleCita.route('/detalle_cita/<id>')
@login_required
def detalle_cita_view(id):
    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 1)
    cita = obtener_detalle_cita(id)
    return render_template('private/detalle_cita.html', cita=cita, perfil_usuario=perfil_usuario)