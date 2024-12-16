from flask import Blueprint, render_template, session, redirect, url_for, flash
from src.services.session_magnament_services import obtener_perfil_usuario, login_required, verificar_permiso
from src.services.solicitudes_service import obtener_detalle_cita, obtener_detalle_mi_cita
from src.utils.validatorsForms import CancelarCita, CitaAtendida, AceptarCita
from src.utils.errors import redirigir_error

detalleCita = Blueprint('detalleCita', __name__)
cancelar_citas = Blueprint('cancelar_citas', __name__)

@detalleCita.route('/detalle_cita/<id>')
@login_required
def detalle_cita_view(id):
    if session['id_roles'] != 1 and session['id_roles'] != 2:
        return redirect(url_for('login.login_view'))
    idusers = session['id']

    try:
        cita = mi_cita = form_atendido = form_aceptar = None
        if session['id_roles'] == 1 and verificar_permiso(session['id_roles'], 3):
            perfil_usuario = obtener_perfil_usuario(session['id'], 1)
            form = CancelarCita()
            form_atendido = CitaAtendida()
            form_aceptar = AceptarCita()
            cita = obtener_detalle_cita(id)
            if cita is None:
                # Redirige o maneja el caso cuando no se encuentra la cita
                return redirect(url_for('citas.Solicitudes'))
        elif session['id_roles'] == 2 and verificar_permiso(session['id_roles'], 4):
            perfil_usuario = obtener_perfil_usuario(session['id'], 2)
            form = CancelarCita()
            mi_cita = obtener_detalle_mi_cita(id, idusers)
            if mi_cita is None:
                # Redirige o maneja el caso cuando no se encuentra la cita
                return redirect(url_for('gestionar_cita.gestionar_cita_view'))
        else:
            flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
            session['error_redirected'] = True
            return redirect(url_for('views.error_view'))
    except Exception as e:
        return redirigir_error(e)

    return render_template('private/detalle_cita.html', mi_cita=mi_cita, form=form, form_atendido=form_atendido,
                           form_aceptar=form_aceptar, cita=cita, perfil_usuario=perfil_usuario)
