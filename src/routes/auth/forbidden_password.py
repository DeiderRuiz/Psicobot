from flask import Blueprint, render_template, url_for, redirect, flash
from src.utils.validatorsForms import ForbiddenPasswordForm
from src.services.forbidden_password_service import gestionar_recuperacion_contrasena

forbidden = Blueprint('forbidden', __name__)

@forbidden.route('/ForbiddenPassword', methods=['GET', 'POST'])
def ForbiddenPassword():
    form = ForbiddenPasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        # Llamar al servicio que gestiona la recuperación de contraseña
        if gestionar_recuperacion_contrasena(email):
            flash('Te hemos enviado un email con instrucciones, revisa tu correo institucional', 'success')
            return redirect(url_for('forbidden.ForbiddenPassword'))
        else:
            flash('El correo electrónico no está registrado en nuestro sistema', 'danger')

    return render_template('auth/ForbiddenPassword.html', form=form)