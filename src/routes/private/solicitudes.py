from flask import Blueprint, render_template, url_for, redirect, session
from src.services.session_magnament_services import obtener_perfil_usuario, login_required
from src.services.solicitudes_service import obtener_citas

citas = Blueprint('citas', __name__)

@citas.route('/solicitudes')
@login_required
def Solicitudes():
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))

    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 1)
    citas_no_leidas, citas_leidas = obtener_citas()
    return render_template('private/solicitudes.html', citas_no_leidas=citas_no_leidas, citas_leidas=citas_leidas,
                           perfil_usuario=perfil_usuario)
