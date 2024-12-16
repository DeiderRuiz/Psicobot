from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from src.services.session_magnament_services import login_required, verificar_permiso
from src.services.estados_cita_service import cancelar_cita_db, cita_atendida_db, aceptar_cita_db
from src.utils.validatorsForms import CancelarCita, CitaAtendida, AceptarCita
from src.utils.errors import redirigir_error

cancelar_citas = Blueprint('cancelar_citas', __name__)
atender_citas = Blueprint('atender_citas', __name__)
aceptar_citas = Blueprint('aceptar_citas', __name__)

@cancelar_citas.route('/cancelar_cita/<id>', methods=['GET', 'POST'])
@login_required
def cancelar_cita(id):
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1 and session['id_roles'] != 2:
        return redirect(url_for('login.login_view'))
    idroles = session['id_roles']

    try:
        if verificar_permiso(session['id_roles'], 7):
            # Instancia del formulario de eliminación
            form = CancelarCita()
            motivo = request.form.get('motivo', 'No especificado')
            if form.validate_on_submit():
                # Llamada a la función que elimina el horario de la base de datos
                cancelar_cita_db(id, idroles, motivo)
                flash('La solicitud de cita para orientación psicológica se ha cancelado con éxito.', 'success')
                if session['id_roles'] == 1:  # Admin
                    return redirect(url_for('citas.Solicitudes'))
                elif session['id_roles'] == 2:  # Estudiante
                    return redirect(url_for('gestionar_cita.gestionar_cita_view'))
        else:
            flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
            session['error_redirected'] = True
            return redirect(url_for('views.error_view'))
    except Exception as e:
        return redirigir_error(e)

    return render_template('private/gestionar_citas.html', form=form, id=id)

@atender_citas.route('/atender_cita/<id>', methods=['GET', 'POST'])
@login_required
def atender_cita(id):
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))
    try:
        if verificar_permiso(session['id_roles'], 6):
            # Instancia del formulario de eliminación
            form = CitaAtendida()
            if form.validate_on_submit():
                # Llamada a la función que elimina el horario de la base de datos
                cita_atendida_db(id)
                flash('La solicitud de cita para orientación psicológica se marcó como atendida.', 'success')
                return redirect(url_for('citas.Solicitudes'))
        else:
            flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
            session['error_redirected'] = True
            return redirect(url_for('views.error_view'))
    except Exception as e:
        return redirigir_error(e)

    return render_template('private/solicitar_cita.html', form=form)

@aceptar_citas.route('/aceptar_cita/<id>', methods=['GET', 'POST'])
@login_required
def aceptar_cita(id):
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))
    idroles = session['id_roles']

    try:
        if verificar_permiso(session['id_roles'], 6):
            # Instancia del formulario de eliminación
            form = AceptarCita()
            mensaje = request.form.get('mensaje', 'No especificado')
            if form.validate_on_submit():
                # Llamada a la función que elimina el horario de la base de datos
                aceptar_cita_db(id, idroles, mensaje)
                flash('La solicitud de cita para orientación psicológica ha sido aceptada con éxito.', 'success')
                return redirect(url_for('citas.Solicitudes'))
        else:
            flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
            session['error_redirected'] = True
            return redirect(url_for('views.error_view'))
    except Exception as e:
        return redirigir_error(e)

    return render_template('private/solicitar_cita.html', form=form)
