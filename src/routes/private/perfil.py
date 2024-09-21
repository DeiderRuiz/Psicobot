from flask import Blueprint, render_template, url_for, request, redirect, session
from src.services.session_magnament_services import obtener_perfil_usuario, login_required
from src.services.perfil_service import actualizar_perfil, cambiar_contrasena, borrar_cuenta
from src.utils.validatorsForms import UpdateProfileForm, ChangePasswordForm, DeleteAccountForm

profile = Blueprint('profile', __name__)

# Vista del perfil del usuario
@profile.route('/perfil/<nombre_usuario>', methods=['GET', 'POST'])
@login_required
def perfil(nombre_usuario):
    # Obtiene el rol del usuario actual
    id_roles = session['id_roles']
    idusers = session['id']
    # Verifica que el usuario logueado es el mismo que el usuario del perfil que se está intentando ver
    if nombre_usuario != session['nombre_usuario'] and id_roles == 1:
        return redirect(url_for('panel_admin.PanelDeAdministracion'))
    if nombre_usuario != session['nombre_usuario'] and id_roles == 2:
        return redirect(url_for('user.PanelDeUsuario'))
    # Obtiene el perfil del usuario actual
    perfil_usuario = obtener_perfil_usuario(nombre_usuario, id_roles)
    # Si el método de la solicitud es POST, entonces el usuario quiere actualizar su información
    update_profile_form = UpdateProfileForm()
    change_password_form = ChangePasswordForm()
    delete_account_form = DeleteAccountForm()
    if request.method == 'GET':
        update_profile_form.nombre_usuario.data = perfil_usuario['nombre_usuario']
        update_profile_form.email.data = perfil_usuario['email']
    # Si las reglas se cumplen...
    if request.method == 'POST':
        if update_profile_form.validate_on_submit() and update_profile_form.updateProfile.data:
            actualizar_perfil(idusers, update_profile_form.nombre_usuario.data,update_profile_form.email.data)
            session['nombre_usuario'] = update_profile_form.nombre_usuario.data
            session['email'] = update_profile_form.email.data
            return render_template('private/perfil.html', update_profile_form=update_profile_form,
                                   change_password_form=change_password_form,
                                   delete_account_form=delete_account_form, perfil_usuario=perfil_usuario)
        elif change_password_form.validate_on_submit() and change_password_form.updatePassword.data:
            # Cambiar contraseña
            cambiar_contrasena(idusers, change_password_form.password.data)
            # Actualizar los datos del formulario de actualización de perfil
            update_profile_form.nombre_usuario.data = session['nombre_usuario']
            update_profile_form.email.data = session['email']
            return render_template('private/perfil.html', update_profile_form=update_profile_form,
                                   change_password_form=change_password_form, delete_account_form=delete_account_form,
                                   perfil_usuario=perfil_usuario)
        elif delete_account_form.validate_on_submit() and delete_account_form.DeleteAccount.data:
            # Borrar cuenta
            borrar_cuenta(idusers)
            return redirect(url_for('login.login_view'))
        #pass
    return render_template('private/perfil.html', update_profile_form=update_profile_form, change_password_form=change_password_form, delete_account_form=delete_account_form, perfil_usuario=perfil_usuario)