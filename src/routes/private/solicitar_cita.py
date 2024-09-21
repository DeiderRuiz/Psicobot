from flask import Blueprint, render_template, url_for, redirect, session, flash
from src.services.session_magnament_services import obtener_perfil_usuario, login_required
from src.services.solicitar_cita_service import obtener_horarios_formateados, procesar_solicitud_cita
from src.utils.validatorsForms import NotificarForm

solicitud = Blueprint('solicitud', __name__)

@solicitud.route('/SolicitarCita', methods=['GET', 'POST'])
@login_required
def SolicitarCita():
    if session['id_roles'] != 2:
        return redirect(url_for('login.login_view'))

    # Obtiene el perfil del usuario y los horarios de atención desde el servicio
    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 2)
    horarios = obtener_horarios_formateados()

    form = NotificarForm()

    if form.validate_on_submit():
        # Si el formulario es válido, procesa la solicitud y envía el correo
        procesar_solicitud_cita(form)
        flash('La solicitud de cita de orientación psicológica se ha enviado correctamente', 'success')
        return redirect(url_for('solicitud.SolicitarCita'))
    else:
        # Manejo de errores de validación del formulario
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en el campo {getattr(form, field).label.text}: {error}")

    return render_template('private/solicitar_cita.html', horarios=horarios, form=form, perfil_usuario=perfil_usuario)
