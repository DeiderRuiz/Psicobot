from flask import Blueprint, render_template, redirect, url_for, flash
from src.utils.validatorsForms import RegisterForm
from src.utils.errors import redirigir_error
from src.services.register_service import comprobar_email, registrar_usuario, generar_codigo_verificacion
from src.services.verificar_cuenta_service import token_verificacion

registro = Blueprint('registro', __name__)

@registro.route('/Registrarse', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    try:
        if form.validate_on_submit():
            nombres = form.nombres.data
            apellidos = form.apellidos.data
            email = form.email.data
            password = form.password.data
            confirm_password = form.confirm_password.data

            existing_email = comprobar_email(email)
            codigo = generar_codigo_verificacion()

            if existing_email:
                flash('El correo electrónico ya está en uso.', 'error')
                return render_template('auth/register.html', form=form)
            elif password == confirm_password:
                registrar_usuario(nombres, apellidos, email, password, codigo)
                success, verificar_codigo_url = token_verificacion(email, codigo)
                if success:
                    return redirect(verificar_codigo_url)
            else:
                flash('Las contraseñas deben coincidir.', 'error')
                return render_template('auth/register.html', form=form)
    except Exception as e:
        return redirigir_error(e)

    return render_template('auth/register.html', form=form)
