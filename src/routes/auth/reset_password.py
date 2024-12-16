from flask import Blueprint, render_template, url_for, request, redirect, session, flash
from src.utils.validatorsForms import ResetPasswordForm
from src.services.reset_password_service import obtener_usuario, actualizar_password
from src.utils.tokens import verificar_token
from src.utils.errors import redirigir_error

password = Blueprint('password', __name__)

@password.route('/ResetPassword/<token>', methods=['GET', 'POST'])
def ResetPassword(token):

    try:
        resultado, error = verificar_token(token, secret_key='psychobot')
        if error:
            flash(error, 'danger')
            return redirect(url_for('forbidden.ForbiddenPassword'))

        estado, email = resultado
        form = ResetPasswordForm()

        if request.method == 'GET':
            user = obtener_usuario(email)
            if user:
                idusers = user['idusers']
                session['idusers'] = idusers
            else:
                flash('Usuario no encontrado.', 'danger')
                return redirect(url_for('forbidden.ForbiddenPassword'))

        idusers = session.get('idusers')
        if form.validate_on_submit() and estado:
            password = form.password.data
            confirm_password = form.confirm_password.data
            if password == confirm_password:
                if actualizar_password(token, password, idusers):
                    flash('Tu contraseña ha sido restablecida con éxito.', 'success')
                    return redirect(url_for('login.login_view'))
                else:
                    flash('Token inválido o expirado.', 'danger')
                    return redirect(url_for('forbidden.ForbiddenPassword'))
            else:
                return render_template('auth/ResetPassword.html', mensaje='Las contraseñas deben coincidir.', form=form,
                                       estado=estado, token=token)
    except Exception as e:
        return redirigir_error(e)

    return render_template('auth/ResetPassword.html', form=form, estado=estado, token=token)
