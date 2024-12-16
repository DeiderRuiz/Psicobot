from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from flask_wtf.csrf import generate_csrf
from src.services.session_magnament_services import obtener_perfil_usuario, login_required
from src.services.panel_usuario_service import generar_respuesta, process_markdown

user = Blueprint('user', __name__)

@user.route('/PanelDeUsuario', methods=['GET', 'POST'])
@login_required
def PanelDeUsuario():
    # Redirige al login a quien no tenga rol de usuario
    if session['id_roles'] != 2:
        return redirect(url_for('login.login_view'))

    perfil_usuario = obtener_perfil_usuario(session['id'], 2)

    # Inicializa la conversación si no existe
    if 'conversacion' not in session:
        session['conversacion'] = []

    if request.method == 'POST':
        chat = request.json.get('chat')
        if chat:
            # Añade el mensaje del usuario a la conversación
            session['conversacion'].append({'rol': 'usuario', 'mensaje': chat})
            # Genera la respuesta del chatbot
            respuesta = generar_respuesta(chat)
            # Añade la respuesta del modelo a la conversación
            session['conversacion'].append({'rol': 'modelo', 'mensaje': respuesta})
        return jsonify(session['conversacion'])

    # Procesa Markdown antes de renderizar
    conversacion_html = [
        {'rol': m['rol'], 'mensaje': process_markdown(m['mensaje'])} for m in session.get('conversacion', [])
    ]
    # Generar el token CSRF manualmente para este formulario
    csrf_token = generate_csrf()
    return render_template('private/user.html', conversacion=conversacion_html, perfil_usuario=perfil_usuario,
                           csrf_token=csrf_token)
