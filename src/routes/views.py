from flask import Blueprint, render_template

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
