from flask import Blueprint, render_template, url_for, redirect, session, flash
from src.services.session_magnament_services import obtener_perfil_usuario, login_required, verificar_permiso
from src.services.solicitar_cita_service import procesar_solicitud_cita, verificar_disponibilidad
from src.services.horarios_services import obtener_horarios
from src.utils.validatorsForms import NotificarForm
from src.utils.errors import redirigir_error

solicitud = Blueprint('solicitud', __name__)

@solicitud.route('/SolicitarCita', methods=['GET', 'POST'])
@login_required
def SolicitarCita():
    if session['id_roles'] != 2:
        return redirect(url_for('login.login_view'))
    idusers = session['id']

    try:
        # Obtiene el perfil del usuario y los horarios de atención desde el servicio
        perfil_usuario = obtener_perfil_usuario(session['id'], 2)
        horarios = obtener_horarios()

        form = NotificarForm()

        if form.validate_on_submit():
            if verificar_permiso(session['id_roles'], 5):
                # Si el formulario es válido, procesa la solicitud y envía el correo
                horario_disponible = verificar_disponibilidad(form)
                if horario_disponible:
                    flash('Hay una solicitud de orientación psicológica programada para esta fecha y hora. Intenta con otro horario diferente.', 'error')
                    return render_template('private/solicitar_cita.html', horarios=horarios, form=form, perfil_usuario=perfil_usuario)
                else:
                    procesar_solicitud_cita(form, idusers)
                    flash('La solicitud de cita para orientación psicológica se ha enviado con éxito.', 'success')
                    return redirect(url_for('solicitud.SolicitarCita'))
            else:
                flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
                session['error_redirected'] = True
                return redirect(url_for('views.error_view'))
        else:
            # Manejo de errores de validación del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error en el campo {getattr(form, field).label.text}: {error}")
    except Exception as e:
        return redirigir_error(e)

    return render_template('private/solicitar_cita.html', horarios=horarios, form=form, perfil_usuario=perfil_usuario)
