from flask import Blueprint, render_template, redirect, url_for, session, request
from src.services.login_service import obtener_usuario, comprobar_password, crear_sesion
from src.utils.validatorsForms import LoginForm

login = Blueprint('login', __name__)

# Vista del login
@login.route('/IniciarSesion', methods=['GET', 'POST'])
def login_view():
    form = LoginForm()
    if form.validate_on_submit():
        if 'nombre_usuario' in request.form and 'password':
            nombre_usuario = form.nombre_usuario.data
            password = form.password.data.encode('utf-8')
            account = obtener_usuario(nombre_usuario)
            if account:
                if comprobar_password(password, account['password']):
                    crear_sesion(account)
                    if session['id_roles'] == 1:
                        return redirect(url_for('panel_admin.PanelDeAdministracion'))
                    elif session['id_roles'] == 2:
                        return redirect(url_for('user.PanelDeUsuario'))
                else:
                    return render_template('auth/login.html', mensaje='Contraseña Incorrecta', form=form)
            else:
                return render_template('auth/login.html', mensaje='Usuario No Encontrado', form=form)

    return render_template('auth/login.html', form=form)
