from flask import Blueprint, render_template, url_for, request, redirect, session, flash
from src.utils.validatorsForms import VerificarCodigoForm, SolicitarCodigoForm
from src.services.verificar_codigo_service import obtener_usuario, verificar_codigo, crear_nuevo_codigo
from src.utils.tokens import verificar_token
from src.services.register_service import generar_codigo_verificacion
from src.services.verificar_cuenta_service import token_verificacion
from src.utils.errors import redirigir_error

codigo = Blueprint('codigo', __name__)

@codigo.route('/VerificarCodigo/<token>', methods=['GET', 'POST'])
def VerificarCodigo(token):
    resultado, error = verificar_token(token, secret_key='psychobot')
    if error:
        flash(error, 'error')
        return redirect(url_for('login.login_view'))

    try:
        estado, email = resultado
        form = VerificarCodigoForm()
        nuevoCodigoForm = SolicitarCodigoForm()

        if request.method == 'GET':
            user = obtener_usuario(email)
            if user:
                idusers = user['idusers']
                session['idusers'] = idusers
            else:
                flash('Usuario no encontrado.', 'danger')
                return redirect(url_for('login.login_view'))

        idusers = session.get('idusers')
        if form.validate_on_submit() and estado:
            codigo = form.codigo.data
            print(codigo, token, idusers)
            if codigo:
                success, error_message = verificar_codigo(token, codigo, idusers)
                if success:
                    flash('Tu cuenta ha sido verificada con éxito.', 'success')
                    return redirect(url_for('login.login_view'))
                else:
                    return render_template('auth/VerificarCodigo.html', mensaje=error_message, form=form,
                                           nuevoCodigoForm=nuevoCodigoForm, estado=estado, token=token)
            else:
                return render_template('auth/VerificarCodigo.html', mensaje='El codigo es incorrecto o ha expirado.',
                                       form=form, nuevoCodigoForm=nuevoCodigoForm,
                                       estado=estado, token=token)

        if nuevoCodigoForm.validate_on_submit():
            nuevoCodigo = generar_codigo_verificacion()
            resultado, mensaje = crear_nuevo_codigo(idusers, nuevoCodigo)
            if resultado:
                success, verificar_codigo_url = token_verificacion(email, nuevoCodigo)
                if success:
                    flash(mensaje, 'success')
                    return redirect(verificar_codigo_url)
            else:
                return render_template('auth/VerificarCodigo.html', mensaje=mensaje, form=form,
                                       nuevoCodigoForm=nuevoCodigoForm, estado=estado, token=token)
    except Exception as e:
        return redirigir_error(e)

    return render_template('auth/VerificarCodigo.html', form=form, nuevoCodigoForm=nuevoCodigoForm, estado=estado, token=token)
