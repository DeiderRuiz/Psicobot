from flask import Blueprint, render_template, url_for, redirect, flash
from src.utils.validatorsForms import ForbiddenPasswordForm
from src.utils.errors import redirigir_error
from src.services.forbidden_password_service import gestionar_recuperacion_contrasena

forbidden = Blueprint('forbidden', __name__)

@forbidden.route('/ForbiddenPassword', methods=['GET', 'POST'])
def ForbiddenPassword():
    form = ForbiddenPasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        try:
            # Gestionar recuperación de contraseña
            if gestionar_recuperacion_contrasena(email):
                flash('Te hemos enviado un correo con instrucciones. Revisa tu correo institucional.', 'success')
                return redirect(url_for('forbidden.ForbiddenPassword'))
            else:
                flash('El correo electrónico no está registrado en nuestro sistema.', 'error')
        except Exception as e:
            return redirigir_error(e)

    return render_template('auth/ForbiddenPassword.html', form=form)
