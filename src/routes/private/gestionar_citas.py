from flask import Blueprint, render_template, session, redirect, url_for, flash
from src.services.session_magnament_services import obtener_perfil_usuario, login_required, verificar_permiso
from src.services.gestionar_citas_service import obtener_mis_citas
from src.utils.validatorsForms import CancelarCita
from src.utils.errors import redirigir_error

gestionar_cita = Blueprint('gestionar_cita', __name__)

@gestionar_cita.route('/GestionarCita', methods=['GET', 'POST'])
@gestionar_cita.route('/GestionarCita/<int:page_num>', methods=['GET', 'POST'])
@login_required
def gestionar_cita_view(page_num=1):
    if session['id_roles'] != 2:
        return redirect(url_for('login.login_view'))
    idusers = session['id']

    try:
        if verificar_permiso(session['id_roles'], 4):
            # Instancia del formulario de eliminación
            form = CancelarCita()
            perfil_usuario = obtener_perfil_usuario(session['id'], 2)
            citas, total_paginas = obtener_mis_citas(page_num, idusers)
        else:
            flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
            session['error_redirected'] = True
            return redirect(url_for('views.error_view'))
    except Exception as e:
        return redirigir_error(e)

    return render_template('private/gestionar_citas.html', citas=citas, form=form,
                           perfil_usuario=perfil_usuario, total_paginas=total_paginas, page_num=page_num)
