from flask import Blueprint, render_template, url_for, redirect, session, request, flash
from src.services.session_magnament_services import obtener_perfil_usuario, login_required, verificar_permiso
from src.services.solicitudes_service import obtener_citas, alerta_de_citas
from src.utils.validatorsForms import BuscarCita
from src.utils.errors import redirigir_error

citas = Blueprint('citas', __name__)


@citas.route('/solicitudes', methods=['GET', 'POST'])
@citas.route('/solicitudes/<int:page_num>', methods=['GET', 'POST'])
@login_required
def Solicitudes(page_num=1):
    if session['id_roles'] != 1:
        return redirect(url_for('login.login_view'))

    try:
        if verificar_permiso(session['id_roles'], 3):
            alertas = alerta_de_citas()
            form = BuscarCita()
            buscar = request.args.get('buscar', form.buscar.data)
            filtros = {
                'estudiante': request.args.get('estudiante', '') == 'True',
                'egresado': request.args.get('egresado', '') == 'True',
                'egresado_no_graduado': request.args.get('egresado_no_graduado', '') == 'True',
                'docente': request.args.get('docente', '') == 'True',
                'administrativo': request.args.get('administrativo', '') == 'True',
                'pendiente': request.args.get('pendiente', '') == 'True',
                'aceptada': request.args.get('aceptada', '') == 'True',
                'cancelada': request.args.get('cancelada', '') == 'True',
                'atendida': request.args.get('atendida', '') == 'True'
            }

            perfil_usuario = obtener_perfil_usuario(session['id'], 1)

            if form.validate_on_submit():
                buscar = form.buscar.data
                filtros = {
                    'estudiante': form.estudiante.data,
                    'egresado': form.egresado.data,
                    'egresado_no_graduado': form.egresado_no_graduado.data,
                    'docente': form.docente.data,
                    'administrativo': form.administrativo.data,
                    'pendiente': form.pendiente.data,
                    'aceptada': form.aceptada.data,
                    'cancelada': form.cancelada.data,
                    'atendida': form.atendida.data
                }

                # Limpiar los filtros no seleccionados
                filtros_limpios = {k: v for k, v in filtros.items() if v}
                filtros_aplicados = '&'.join([f"{k}=True" for k in filtros_limpios])
                if filtros_aplicados:
                    filtros_aplicados = '&' + filtros_aplicados

                return redirect(url_for('citas.Solicitudes', page_num=page_num, buscar=buscar) + filtros_aplicados)
            else:
                form.buscar.data = buscar
                form.estudiante.data = filtros['estudiante']
                form.egresado.data = filtros['egresado']
                form.egresado_no_graduado.data = filtros['egresado_no_graduado']
                form.docente.data = filtros['docente']
                form.administrativo.data = filtros['administrativo']
                form.pendiente.data = filtros['pendiente']
                form.aceptada.data = filtros['aceptada']
                form.cancelada.data = filtros['cancelada']
                form.atendida.data = filtros['atendida']

            citas, total_paginas = obtener_citas(page_num, buscar, **filtros)
        else:
            flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
            session['error_redirected'] = True
            return redirect(url_for('views.error_view'))

    except Exception as e:
        return redirigir_error(e)

    filtros_limpios = {k: v for k, v in filtros.items() if v}
    filtros_aplicados = '&'.join([f"{k}=True" for k in filtros_limpios])
    if filtros_aplicados:
        filtros_aplicados = '&' + filtros_aplicados

    return render_template('private/solicitudes.html', citas=citas, total_paginas=total_paginas, page_num=page_num,
                           perfil_usuario=perfil_usuario, form=form, buscar=buscar, filtros_aplicados=filtros_aplicados,
                           alertas=alertas)
