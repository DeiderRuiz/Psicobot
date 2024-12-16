from flask import Blueprint, render_template, url_for, redirect, session, flash
from src.services.session_magnament_services import obtener_perfil_usuario, login_required, verificar_permiso
from src.services.horarios_services import obtener_horarios, actualizar_o_insertar_horario, eliminar_horario_bd
from src.utils.validatorsForms import HorarioForm, DeleteDayForm
from src.utils.errors import redirigir_error

horario = Blueprint('horario', __name__)
eliminar_horarios = Blueprint('eliminar_horarios', __name__)

@horario.route('/Horarios', methods=['GET', 'POST'])
@login_required
def Horarios():
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))

    try:
        perfil_usuario = obtener_perfil_usuario(session['id'], 1)
        horarios = obtener_horarios()

        form = HorarioForm()
        if form.validate_on_submit():
            if verificar_permiso(session['id_roles'], 9) and verificar_permiso(session['id_roles'], 10):
                dia = form.dia.data
                hora_inicio_am = form.hora_inicio_am.data
                hora_fin_am = form.hora_fin_am.data
                hora_inicio_pm = form.hora_inicio_pm.data
                hora_fin_pm = form.hora_fin_pm.data

                if hora_inicio_am is None and hora_fin_am is None and hora_inicio_pm is None and hora_fin_pm is None:
                    flash('Debes ingresar al menos un horario, ya sea para el turno de la mañana o de la tarde.',
                          'error')
                    return render_template('private/horarios.html', form=form,
                                           perfil_usuario=perfil_usuario,
                                           horarios=horarios)

                if (hora_inicio_am and not hora_fin_am) or (hora_fin_am and not hora_inicio_am) or (
                        hora_inicio_pm and not hora_fin_pm) or (hora_fin_pm and not hora_inicio_pm):
                    flash(
                        'Si estableces una hora de inicio o de fin en el turno de la mañana o de la tarde, asegúrate de completar ambas horas.',
                        'error')
                    return render_template('private/horarios.html', form=form,
                                           perfil_usuario=perfil_usuario,
                                           horarios=horarios)

                if (hora_inicio_am and hora_fin_am and hora_inicio_am < hora_fin_am) or (
                        hora_inicio_pm and hora_fin_pm and hora_inicio_pm < hora_fin_pm):
                    mensaje, tipo = actualizar_o_insertar_horario(dia, hora_inicio_am, hora_fin_am, hora_inicio_pm,
                                                                  hora_fin_pm)
                    flash(mensaje, tipo)
                    return redirect(url_for('horario.Horarios'))
                else:
                    flash('La hora de inicio no debe ser mayor que la hora final.', 'error')
                    return render_template('private/horarios.html', form=form,
                                           perfil_usuario=perfil_usuario, horarios=horarios)
            else:
                flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
                session['error_redirected'] = True
                return redirect(url_for('views.error_view'))
    except Exception as e:
        return redirigir_error(e)

    return render_template('private/horarios.html', form=form, perfil_usuario=perfil_usuario, horarios=horarios)

@eliminar_horarios.route('/eliminar_horario/<dia>', methods=['GET', 'POST'])
@login_required
def eliminar_horario(dia):
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))

    try:
        # Instancia del formulario de eliminación
        form = DeleteDayForm()

        if form.validate_on_submit():
            if verificar_permiso(session['id_roles'], 11):
                # Llamada a la función que elimina el horario de la base de datos
                eliminar_horario_bd(dia)
                flash('El horario se ha eliminado con éxito.', 'success')
                return redirect(url_for('horario.Horarios'))
            else:
                flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
                session['error_redirected'] = True
                return redirect(url_for('views.error_view'))
    except Exception as e:
        return redirigir_error(e)

    return render_template('private/eliminar_horario.html', form=form, dia=dia)
