from flask import Blueprint, render_template, redirect, url_for, session
from src.services.session_magnament_services import obtener_perfil_usuario, login_required
from src.services.panel_administracion_service import contar_solicitudes_no_leidas

panel_admin = Blueprint('panel_admin', __name__)

@panel_admin.route('/PanelDeAdministracion')
@login_required
def PanelDeAdministracion():
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))

    # Obtiene el perfil del usuario actual
    perfil_usuario = obtener_perfil_usuario(session['id'], 1)

    # Consulta para contar las solicitudes no leídas
    solicitudes_no_leidas = contar_solicitudes_no_leidas()

    return render_template('private/admin.html', perfil_usuario=perfil_usuario, solicitudes_no_leidas=solicitudes_no_leidas)
