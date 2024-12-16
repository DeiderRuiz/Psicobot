from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from src.services.login_service import obtener_usuario, comprobar_password, crear_sesion
from src.utils.validatorsForms import LoginForm, SolicitarCodigoForm
from src.services.verificar_codigo_service import crear_nuevo_codigo
from src.services.register_service import generar_codigo_verificacion
from src.services.verificar_cuenta_service import token_verificacion
from src.utils.errors import redirigir_error

login = Blueprint('login', __name__)

# Vista del login
@login.route('/IniciarSesion', methods=['GET', 'POST'])
def login_view():
    form = LoginForm()
    nuevoCodigoForm = SolicitarCodigoForm()

    try:
        if form.validate_on_submit():
            if 'email' in request.form and 'password':
                email = form.email.data
                password = form.password.data.encode('utf-8')
                account, estado = obtener_usuario(email)
                if estado is not None:
                    if comprobar_password(password, account['password']):
                        if estado is False:
                            flash('Cuenta no verificada.', 'warning')
                            session['idusuario'] = account['idusers']
                            session['email'] = email
                            return render_template('auth/login.html', mensaje='Generar código de verificación',
                                                   form=form,
                                                   nuevoCodigoForm=nuevoCodigoForm)
                        else:
                            crear_sesion(account)
                            if session['id_roles'] == 1:
                                return redirect(url_for('panel_admin.PanelDeAdministracion'))
                            elif session['id_roles'] == 2:
                                return redirect(url_for('user.PanelDeUsuario'))
                    else:
                        flash('Contraseña incorrecta.', 'error')
                        return render_template('auth/login.html', form=form, nuevoCodigoForm=nuevoCodigoForm)
                else:
                    flash('Usuario no encontrado.', 'error')
                    return render_template('auth/login.html', form=form, nuevoCodigoForm=nuevoCodigoForm)

        if nuevoCodigoForm.validate_on_submit():
            user_id = session.get('idusuario')
            email = session.get('email')
            nuevoCodigo = generar_codigo_verificacion()
            resultado, mensaje = crear_nuevo_codigo(user_id, nuevoCodigo)
            if resultado:
                success, verificar_codigo_url = token_verificacion(email, nuevoCodigo)
                if success:
                    flash(mensaje, 'success')
                    return redirect(verificar_codigo_url)
            else:
                return render_template('auth/login.html', mensaje=mensaje, form=form,
                                       nuevoCodigoForm=nuevoCodigoForm)
    except Exception as e:
        return redirigir_error(e)

    return render_template('auth/login.html', form=form, nuevoCodigoForm=nuevoCodigoForm)
