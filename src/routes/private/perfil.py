from flask import Blueprint, render_template, url_for, request, redirect, session, flash
from src.services.session_magnament_services import obtener_perfil_usuario, login_required, verificar_permiso
from src.services.perfil_service import actualizar_perfil, cambiar_contrasena, borrar_cuenta
from src.utils.validatorsForms import UpdateProfileForm, ChangePasswordForm, DeleteAccountForm
from src.utils.errors import redirigir_error

profile = Blueprint('profile', __name__)

# Vista del perfil del usuario
@profile.route('/perfil/<int:idusers>', methods=['GET', 'POST'])
@login_required
def perfil(idusers):
    # Obtiene el rol del usuario actual
    id_roles = session['id_roles']
    id = session['id']
    # Verifica que el usuario logueado es el mismo que el usuario del perfil que se está intentando ver
    if id != idusers and id_roles == 1:
        return redirect(url_for('panel_admin.PanelDeAdministracion'))
    if id != idusers and id_roles == 2:
        return redirect(url_for('user.PanelDeUsuario'))

    perfil_usuario = obtener_perfil_usuario(idusers, id_roles)
    # Si el método de la solicitud es POST, entonces el usuario quiere actualizar su información
    update_profile_form = UpdateProfileForm()
    change_password_form = ChangePasswordForm()
    delete_account_form = DeleteAccountForm()
    if request.method == 'GET':
        update_profile_form.nombres.data = perfil_usuario['nombres']
        update_profile_form.apellidos.data = perfil_usuario['apellidos']
        update_profile_form.email.data = perfil_usuario['email']
    # Si las reglas se cumplen...
    if request.method == 'POST':
        if update_profile_form.validate_on_submit() and update_profile_form.updateProfile.data:
            actualizar_perfil(idusers, update_profile_form.nombres.data, update_profile_form.apellidos.data, update_profile_form.email.data)
            session['nombres'] = update_profile_form.nombres.data
            session['apellidos'] = update_profile_form.apellidos.data
            session['email'] = update_profile_form.email.data
            return redirect(url_for('profile.perfil', idusers=perfil_usuario['idusers']))
        elif change_password_form.validate_on_submit() and change_password_form.updatePassword.data:
            # Cambiar contraseña
            cambiar_contrasena(idusers, change_password_form.password.data)
            # Actualizar los datos del formulario de actualización de perfil
            update_profile_form.nombres.data = session['nombres']
            update_profile_form.apellidos.data = session['apellidos']
            update_profile_form.email.data = session['email']

        elif delete_account_form.validate_on_submit() and delete_account_form.DeleteAccount.data:
            if verificar_permiso(session['id_roles'], 2):
                # Borrar cuenta
                borrar_cuenta(idusers)
                return redirect(url_for('login.login_view'))
            else:
                flash("No tienes los permisos necesarios para realizar esta acción.", "fatal error")
                session['error_redirected'] = True
                return redirect(url_for('views.error_view'))
    #try:
        # Obtiene el perfil del usuario actual

    #except Exception as e:
#        return redirigir_error(e)
        # pass

    return render_template('private/perfil.html', update_profile_form=update_profile_form,
                           change_password_form=change_password_form, delete_account_form=delete_account_form,
                           perfil_usuario=perfil_usuario)
