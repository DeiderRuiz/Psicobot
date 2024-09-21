from flask import Blueprint, render_template, url_for, redirect, session, flash
from src.services.session_magnament_services import obtener_perfil_usuario, login_required
from src.services.horarios_services import obtener_horarios, actualizar_o_insertar_horario, eliminar_horario_bd
from src.utils.validatorsForms import HorarioForm, DeleteDayForm

horario = Blueprint('horario', __name__)
eliminar_horarios = Blueprint('eliminar_horarios', __name__)

@horario.route('/Horarios', methods=['GET', 'POST'])
@login_required
def Horarios():
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))

    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 1)
    horarios = obtener_horarios()

    form = HorarioForm()
    if form.validate_on_submit():
        dia = form.dia.data
        hora_inicio_am = form.hora_inicio_am.data
        hora_fin_am = form.hora_fin_am.data
        hora_inicio_pm = form.hora_inicio_pm.data
        hora_fin_pm = form.hora_fin_pm.data

        if hora_inicio_am is None and hora_fin_am is None and hora_inicio_pm is None and hora_fin_pm is None:
            mensaje = 'Error: Debe colocar al menos un horario, ya sea jornada de la mañana o de la tarde'
            return render_template('private/horarios.html', mensaje=mensaje, form=form, perfil_usuario=perfil_usuario,
                                   horarios=horarios)

        if (hora_inicio_am and not hora_fin_am) or (hora_fin_am and not hora_inicio_am) or (
                hora_inicio_pm and not hora_fin_pm) or (hora_fin_pm and not hora_inicio_pm):
            mensaje = 'Si estableces una hora de inicio o fin en la jornada de la mañana o la tarde, asegúrate de completar ambas horas.'
            return render_template('private/horarios.html', mensaje=mensaje, form=form, perfil_usuario=perfil_usuario,
                                   horarios=horarios)

        if (hora_inicio_am and hora_fin_am and hora_inicio_am < hora_fin_am) or (
                hora_inicio_pm and hora_fin_pm and hora_inicio_pm < hora_fin_pm):
            mensaje, tipo = actualizar_o_insertar_horario(dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm)
            flash(mensaje, tipo)
            return redirect(url_for('horario.Horarios'))

        else:
            mensaje = 'Error: La hora de inicio NO debe ser mayor a la hora final'
            return render_template('private/horarios.html', mensaje=mensaje, form=form, perfil_usuario=perfil_usuario, horarios=horarios)
    return render_template('private/horarios.html', form=form, perfil_usuario=perfil_usuario, horarios=horarios)

@eliminar_horarios.route('/eliminar_horario/<dia>', methods=['GET', 'POST'])
@login_required
def eliminar_horario(dia):
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))

    # Instancia del formulario de eliminación
    form = DeleteDayForm()

    if form.validate_on_submit():
        # Llamada a la función que elimina el horario de la base de datos
        eliminar_horario_bd(dia)
        flash('Horario eliminado correctamente', 'success')
        return redirect(url_for('horario.Horarios'))

    return render_template('private/eliminar_horario.html', form=form, dia=dia)