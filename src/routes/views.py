from flask import Blueprint, render_template, session, redirect, url_for

views = Blueprint('views', __name__)

# Vista de inicio
@views.route('/')
def index():
    return render_template('index.html')

# Vista para rutas de atención
@views.route('/RutasDeAtencion')
def atencion():
    return render_template('atencion.html')

# Vista para acerca de
@views.route('/Acerca-De')
def about():
    return render_template('about.html')

# Vista para acerca de
@views.route('/error')
def error_view():
    if not session.get('error_redirected'):
        return redirect(url_for('views.index'))
    session.pop('error_redirected', None)
    return render_template('errors.html')
