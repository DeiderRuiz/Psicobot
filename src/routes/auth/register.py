from flask import Blueprint, render_template, redirect, url_for, session
from src.utils.validatorsForms import RegisterForm
from src.services.register_service import comprobar_usuario, comprobar_email, registrar_usuario

registro = Blueprint('registro', __name__)

@registro.route('/Registrarse', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        nombre_usuario = form.nombre_usuario.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        existing_user = comprobar_usuario(nombre_usuario)
        existing_email = comprobar_email(email)

        if existing_user:
            return render_template('auth/register.html', mensaje='El nombre de usuario ya existe', form=form)
        elif existing_email:
            return render_template('auth/register.html', mensaje='El correo electrónico ya está en uso', form=form)
        elif password == confirm_password:
            user_id = registrar_usuario(nombre_usuario, email, password)
            session['logged'] = True
            session['id'] = user_id
            session['id_roles'] = 2
            session['nombre_usuario'] = nombre_usuario
            session['email'] = email
            session['conversacion'] = []
            return redirect(url_for('user.PanelDeUsuario'))
        else:
            return render_template('auth/register.html', mensaje='Las contraseñas no coinciden', form=form)

    return render_template('auth/register.html', form=form)