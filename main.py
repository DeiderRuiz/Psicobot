#IMPORTACIONES
from flask import Flask, render_template, url_for, request, redirect, session, flash#, jsonify, Response
from flask_mysqldb import MySQL#, MySQLdb
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import StringField, EmailField, TextAreaField, PasswordField, DateField, TimeField, RadioField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Regexp, Length, Optional, EqualTo
from datetime import date, time, datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature, BadSignature
from functools import wraps
from babel.dates import format_date
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import bcrypt
import openai

#LLAVE de la aplicación
app = Flask(__name__)
app.secret_key='psychobot'
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'], "auth")

#CONFIGURAR BASE DE DATOS
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Killjoy-0908'
app.config['MYSQL_DB']='psychobot'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql = MySQL(app)

# Configuración del servidor de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # servidor SMTP
app.config['MAIL_PORT'] = 587  # puerto
app.config['MAIL_USE_TLS'] = True  # O False si no necesitas TLS
app.config['MAIL_USERNAME'] = 'deiderruiz00@gmail.com'  # Correo del emisor
app.config['MAIL_PASSWORD'] = 'wbld bbaf cnmn hysq'  # Contrseña del emisor
app.config['MAIL_DEFAULT_SENDER'] = 'deiderruiz00@gmail.com'  # Emisor por defecto
# Inicializa la extensión de Flask-Mail
mail = Mail(app)

#Validar que los campos de tiempo estén dentro de cierto rango
class TimeRange(object):
    def __init__(self, min_time, max_time, message=None):
        self.min_time = min_time
        self.max_time = max_time
        if not message:
            min_time_12h = self.min_time.strftime('%I:%M %p')
            max_time_12h = self.max_time.strftime('%I:%M %p')
            message = u'El campo debe estar entre %s y %s.' % (min_time_12h, max_time_12h)
        self.message = message

    def __call__(self, form, field):
        if field.data is None:
            return
        if field.data < self.min_time or field.data > self.max_time:
            raise ValidationError(self.message)

#Función para hacer permanente un sesión
@app.before_request
def make_session_permanent():
    session.permanent = True

#Regla de validación personalizada para emails (solo acepta correos institucionales)
class EmailValidator(object):
    def __init__(self, message=None):
        if not message:
            message = u'El correo electrónico debe ser un correo institucional'
        self.message = message
    def __call__(self, form, field):
        if not field.data.endswith('@uajs.edu.co'):
            raise ValidationError(self.message)

#VISTAS
#ruta de una vista
@app.route('/')
#función donde se escribe el contenido de la vista
def index():
    nombre = 'Psicobot'
    date = datetime.now()
    #retorna plantilla HTML renderizada
    return render_template('index.html', nombre = nombre, date = date)

#Vista para rutas de atención
@app.route('/RutasDeAtencion')
def atencion():
    return render_template('atencion.html')

#clase para crear inputs y reglas de validación para el login
class LoginForm(FlaskForm):
    nombre_usuario = StringField('Nombre De Usuario o Correo Electrónico', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

# Vista del login
@app.route('/IniciarSesion', methods=['GET', 'POST'])
def login():
    #Instancia de la clase con los campos y reglas de validación del formulario
    form = LoginForm()
    #Valida formulario si las reglas de cada campo se cumplen
    if form.validate_on_submit():
        if 'nombre_usuario' in request.form and 'password':
            nombre_usuario = form.nombre_usuario.data
            password = form.password.data.encode('utf-8')#Lo que se ingresa en el capo de la contraseña se codifica
            cur = mysql.connection.cursor()
            # Intenta encontrar al usuario por nombre de usuario o correo electrónico
            cur.execute('SELECT * FROM users WHERE nombre_usuario = %s OR email = %s', (nombre_usuario, nombre_usuario,))
            #Diccionario que recupera el conjunto de datos involucrados en las Secuencia SQL de arriba
            account = cur.fetchone()
            #Si encuentra un usuario con el nombre de usuario o correo colocado en el campo nombre_usuario...
            if account:
                #Toma la contraseña codificada para compararla con la que está almacenada en la base de datos
                hashed_password = account['password'].encode('utf-8')
                #Si las contraseñas coinciden...
                if bcrypt.checkpw(password, hashed_password):
                    #Almacena información de la sesión
                    session['logged'] = True#Usuario Logeado
                    session['id'] = account['idusers']#ID del susario
                    session['id_roles'] = account['id_roles']#Rol del usuario
                    session['nombre_usuario'] = account['nombre_usuario']#Nombre del usuario
                    session['email'] = account['email']#Email del usuario
                    session['conversacion'] = []#Lista vacía que almacenará la conversación con el chatbot
                    #Si el rol es 1 (Administrador)...
                    if session['id_roles'] == 1:
                        #Redirige al panel de administrador
                        return redirect(url_for('PanelDeAdministracion'))
                    #Si es rol es 2 (estudiante)...
                    elif session['id_roles'] == 2:
                        #Redirige al panel del usuario (En donde se encuentra el chatbot)
                        return redirect(url_for('PanelDeUsuario'))
                #Si las contraseñas no coinciden...
                else:
                    #Renderiza de nuevo la vista del login con un mensaje
                    return render_template('auth/login.html', mensaje='Contraseña Incorrecta', form=form)
            #Si no encuentra un Usuario con el nombre o correo escrito en el campo...
            else:
                # Renderiza de nuevo la vista del login con un mensaje
                return render_template('auth/login.html', mensaje='Usuario No Encontrado', form=form)
    return render_template('auth/login.html', form=form)

#Clase para crea inputs y reglas de validación para el registro
class RegisterForm(FlaskForm):
    nombre_usuario = StringField('Nombre De Usuario', validators=[DataRequired(), Length(min=3, max=25),
                                                                  Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ]',
                                                                         message="El nombre de usuario debe comenzar con una letra"),
                                                                  Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9_]*$',
                                                                         message="El nombre de usuario solo puede contener letras, números y guiones bajos")])
    email = EmailField('Correo Institucional', validators=[DataRequired(), Length(min=3, max=25), EmailValidator()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=25)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), Length(min=6, max=25)])
    submit = SubmitField('Registrarse')

#Vista para registrarse
@app.route('/Registrarse', methods=['GET', 'POST'])
def register():
    # Instancia de la clase con los campos y reglas de validación del formulario
    form = RegisterForm()
    #Valida que se cumplan las reglas de validación de los campos
    if form.validate_on_submit():
        nombre_usuario = form.nombre_usuario.data
        email = form.email.data
        password = form.password.data
        confirm_password= form.confirm_password.data
        # Verificar si el nombre de usuario ya existe
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE nombre_usuario = %s', (nombre_usuario,))
        #Diccionario que conserva el nombre de usuario que se tiene en cuenta en la secuencia SQL
        existing_user = cur.fetchone()
        # Verificar si el correo electrónico ya existe
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        #Otro diccionario pero para el correo
        existing_email = cur.fetchone()
        # Si el usuario ya existe...
        if existing_user:
            #Mostrar un mensaje de error
            return render_template('auth/register.html', mensaje='El nombre de usuario ya existe', form=form)
        elif existing_email:
            # Si el correo electrónico ya está en uso, mostrar un mensaje de error
            return render_template('auth/register.html', mensaje='El correo electrónico ya está en uso', form=form)
        #Si los campos de contraseña y confirmar contraseña coinciden...
        elif password == confirm_password:
            #Registra el nuevo usuario en la base de datos (SOLO REGISTRA USUARIOS CON ROL DE ESUDIANTES, NO ADMINISTRADORES)
            password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            cur.execute('INSERT INTO users (nombre_usuario, email, password, id_roles) VALUES (%s, %s, %s, "2")', (nombre_usuario, email, hashed_password,))
            mysql.connection.commit()
            # Iniciar sesión después de registrarse
            session['logged'] = True
            session['id'] = cur.lastrowid
            session['id_roles'] = 2
            session['nombre_usuario'] = nombre_usuario
            session['email'] = email
            session['conversacion'] = []
            return redirect(url_for('PanelDeUsuario'))  # Redirigir al panel de usuario
        else:
            #NO deja registrar si las contraseñas no coinciden
            return render_template('auth/register.html', mensaje='Las contraseñas no coinciden', form=form)
    return render_template('auth/register.html', form=form)

#clase para crear inputs y reglas de validación para la recuperación de la contraseña
class ForbiddenPasswordForm(FlaskForm):
    email = EmailField('Correo Institucional', validators=[DataRequired()])
    submit = SubmitField('Recuperar contraseña')

# Vista de recuperación de contraseña
@app.route('/ForbiddenPassword', methods=['GET', 'POST'])
def ForbiddenPassword():
    form = ForbiddenPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', (email, ))
        user = cur.fetchone()
        if user:
            token = serializer.dumps(email, salt='reset-forbidden-password')
            expiration = datetime.now() + timedelta(hours=1)  # El token expira en 1 hora
            rightNow = datetime.now()
            cur.execute('UPDATE users SET token=%s, token_expiration=%s, fecha_solicitud=%s, estado_solicitud="pendiente" WHERE email=%s',
                        (token, expiration, rightNow, email))
            mysql.connection.commit()
            reset_url = url_for('ResetPassword', token=token, _external=True)
            msg = Message("Recuperación de contraseña",
                          recipients=[email])
            msg.body = f"Utiliza este enlace para restablecer tu contraseña: {reset_url}\n\nPor favor, ten en cuenta que este enlace es temporal y expirará en una hora."
            mail.send(msg)
            flash('Te hemos enviado un email con instrucciones, revisa tu correo institucional', 'success')
            return redirect(url_for('ForbiddenPassword'))
    return render_template('auth/ForbiddenPassword.html', form=form)

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=25)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), Length(min=6, max=25)])
    submit = SubmitField('Restablecer contraseña')

# Vista de recuperación de contraseña
@app.route('/ResetPassword/<token>', methods=['GET', 'POST'])
def ResetPassword(token):
    try:
        resultado = serializer.loads_unsafe(token, salt='reset-forbidden-password', max_age=3600)
    except SignatureExpired:
        flash('1. El enlace de restablecimiento de contraseña ha expirado.', 'danger')
        return redirect(url_for('ForbiddenPassword'))
    except BadTimeSignature:
        flash('2. El enlace de restablecimiento de contraseña es inválido.', 'danger')
        return redirect(url_for('ForbiddenPassword'))
    except BadSignature:
        flash('3. El enlace de restablecimiento de contraseña es inválido.', 'danger')
        return redirect(url_for('ForbiddenPassword'))
    except Exception as e:
        flash(f'4. Ocurrió un error: {str(e)}', 'danger')
        return redirect(url_for('ForbiddenPassword'))
    estado = resultado[0]
    email = resultado[1]
    form = ResetPasswordForm()
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute('SELECT idusers FROM users WHERE email = %s', (email,))
        resultado = cur.fetchone()
        if resultado:
            idusers = resultado['idusers']
            session['idusers'] = idusers  # Guardar en la sesión
        else:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('ForbiddenPassword'))
    idusers = session.get('idusers')  # Recuperar desde la sesión

    if form.validate_on_submit() and estado == True:
        password = form.password.data
        confirm_password = form.confirm_password.data
        if password == confirm_password:
            # Registra el nuevo usuario en la base de datos (SOLO REGISTRA USUARIOS CON ROL DE ESUDIANTES, NO ADMINISTRADORES)
            password = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            cur = mysql.connection.cursor()
            cur.execute('UPDATE users SET password = %s, estado = "completo" WHERE idusers = %s', (hashed_password, idusers,))
            mysql.connection.commit()
            flash('Tu contraseña ha sido restablecida exitosamente.', 'success')
            return redirect(url_for('login'))
        else:
            #NO deja registrar si las contraseñas no coinciden
            return render_template('auth/ResetPassword.html', mensaje='Las contraseñas no coinciden', form=form, estado=estado)
    return render_template('auth/ResetPassword.html', form=form, estado=estado)

#Función para cerrar una sesión
@app.route('/CerrarSesion')
def CerrarSesion():
    session.pop('logged', None)
    session.pop('id', None)
    session.pop('id_roles', None)
    session.pop('conversacion', None)
    #Limpia toda la información de la sesión
    memory.clear()
    return redirect(url_for('login'))

#Función para retringir acceso a paginas que requieren login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def obtener_perfil_usuario(nombre_usuario, id_roles):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE nombre_usuario = %s AND id_roles = %s', (nombre_usuario, id_roles))
    return cur.fetchone()

#Vista de administrador
@app.route('/PanelDeAdministracion')
@login_required
def PanelDeAdministracion():
    #Redirige al login a quien no tenga rol de adminitrador (Evita que se ingrese al panel de administración usando la URL)
    if session['id_roles'] != 1:
        return redirect(url_for('login'))
    # Obtiene el perfil del usuario actual
    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 1)
    cur = mysql.connection.cursor()
    # Consulta para contar las solicitudes no leídas
    cur.execute('SELECT COUNT(*) FROM citas WHERE estado = "no leido"')
    solicitudes = cur.fetchone()
    solicitudes_no_leidas = solicitudes['COUNT(*)']
    return render_template('auth/admin.html', perfil_usuario=perfil_usuario, solicitudes_no_leidas=solicitudes_no_leidas)

#Clase con los campos y reglas de validación del formulario de horario de atención
class HorarioForm(FlaskForm):
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dia = SelectField('Días de la semana', choices=[('', 'Seleccionar día')] + [(dia, dia) for dia in dias_semana], validators=[DataRequired()])
    hora_inicio_am = TimeField('Hora de inicio', validators=[Optional(), TimeRange(min_time=time(6), max_time=time(12,00))])
    hora_fin_am = TimeField('Hora de fin', validators=[Optional(), TimeRange(min_time=time(6), max_time=time(12,00))])
    hora_inicio_pm = TimeField('Hora de inicio', validators=[Optional(), TimeRange(min_time=time(12), max_time=time(18,00))])
    hora_fin_pm = TimeField('Hora de fin', validators=[Optional(), TimeRange(min_time=time(12), max_time=time(18,00))])
    submit = SubmitField('Aceptar')

#Vista de los horarios
@app.route('/Horarios', methods=['GET', 'POST'])
@login_required
def Horarios():
    # Redirige al login a quien no tenga rol de adminitrador (Evita que se ingrese al panel de administración usando la URL)
    if session['id_roles'] != 1:
        return redirect(url_for('login'))

    # Selecciona de la base de datos las fechas establecidas para el horario de atención en una semana (de martes a martes por ejemplo)
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM horarios ORDER BY FIELD(dia, "Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"), hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm')
    horarios = cur.fetchall()

    # Muestra las fechas del horario de atención que se encuentran en la base de datos, en caso de encontrarlas
    for horario in horarios:
        # Formatea las horas para eliminar los segundos y convertirlas a formato de 12 horas
        if horario['hora_inicio_am'] is not None:
            horario['hora_inicio_am'] = datetime.strptime(':'.join(str(horario['hora_inicio_am']).split(':')[:2]),'%H:%M').strftime('%I:%M %p')
        if horario['hora_fin_am'] is not None:
            horario['hora_fin_am'] = datetime.strptime(':'.join(str(horario['hora_fin_am']).split(':')[:2]), '%H:%M').strftime('%I:%M %p')
        if horario['hora_inicio_pm'] is not None:
            horario['hora_inicio_pm'] = datetime.strptime(':'.join(str(horario['hora_inicio_pm']).split(':')[:2]), '%H:%M').strftime('%I:%M %p')
        if horario['hora_fin_pm'] is not None:
            horario['hora_fin_pm'] = datetime.strptime(':'.join(str(horario['hora_fin_pm']).split(':')[:2]), '%H:%M').strftime('%I:%M %p')

    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 1)
    #Instancia de la clase del formulario de horario de atención
    form = HorarioForm()
    #Si las reglas se cumplen...
    if form.validate_on_submit():
        dia = form.dia.data
        hora_inicio_am = form.hora_inicio_am.data
        hora_fin_am = form.hora_fin_am.data
        hora_inicio_pm = form.hora_inicio_pm.data
        hora_fin_pm = form.hora_fin_pm.data

        # Verifica si al menos un horario (De mañana o tarde) está completo
        if hora_inicio_am is None and hora_fin_am is None and hora_inicio_pm is None and hora_fin_pm is None:
            return render_template('auth/horarios.html', mensaje='Error: Debe colocar al menos un horario, ya sea jornada de la mañana o de la tarde', form=form, perfil_usuario=perfil_usuario, horarios=horarios)
        # Verifica que los horarios estén completos (QUe se coloque la hora de inicio y fin de algún horario mañana o tarde)
        if (hora_inicio_am and not hora_fin_am) or (hora_fin_am and not hora_inicio_am) or (hora_inicio_pm and not hora_fin_pm) or (hora_fin_pm and not hora_inicio_pm):
            return render_template('auth/horarios.html', mensaje='Si estableces una hora de inicio o fin en la jornada de la mañana o la tarde, asegúrate de completar ambas horas.', form=form, perfil_usuario=perfil_usuario, horarios=horarios)
        # Verifica que los horarios sean correctos (Que la hora de inicio no sea mayor a la de fin o que no haya una hora de la tarde en horario de la mañana)
        if (hora_inicio_am and hora_fin_am and hora_inicio_am < hora_fin_am) or (hora_inicio_pm and hora_fin_pm and hora_inicio_pm < hora_fin_pm):
            #Se incropora las horas correctas en la base de datos para crear el nuevo horario
            cur = mysql.connection.cursor()
            # Consulta si el día ya existe en la base de datos
            cur.execute('SELECT dia FROM horarios WHERE dia = %s', (dia,))
            theDay = cur.fetchone()
            if theDay:
                # Actualiza la información existente
                cur.execute(
                    'UPDATE horarios SET hora_inicio_am = %s, hora_fin_am = %s, hora_inicio_pm = %s, hora_fin_pm = %s WHERE dia = %s',
                    (hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm, dia))
                flash('Se ha actualizado el horario de atención correctamente', 'success')
            else:
                cur.execute('INSERT INTO horarios (dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm) VALUES (%s, %s, %s, %s, %s )', (dia, hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm))
                flash('Se ha agregado un nuevo horario de atención correctamente', 'success')
            mysql.connection.commit()
            return redirect(url_for('Horarios'))
        #Sino...
        else:
            return render_template('auth/horarios.html', mensaje='Error: La hora de inicio NO debe ser mayor a la hora final', form=form, perfil_usuario=perfil_usuario, horarios=horarios)
    return render_template('auth/horarios.html', form=form, perfil_usuario=perfil_usuario, horarios=horarios)

class DeleteDayForm(FlaskForm):
    submit = SubmitField('Si, Borrar horario')

@app.route('/eliminar_horario/<dia>', methods=['GET', 'POST'])
@login_required
def eliminar_horario(dia):
    # Redirige al login a quien no tenga rol de administrador
    if session['id_roles'] != 1:
        return redirect(url_for('login'))

    # Instancia del formulario de eliminación
    form = DeleteDayForm()

    if form.validate_on_submit():
        # Elimina el horario de la base de datos
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM horarios WHERE dia = %s', (dia,))
        mysql.connection.commit()
        flash('Horario eliminado correctamente', 'success')
        return redirect(url_for('Horarios'))

    return render_template('auth/eliminar_horario.html', form=form, dia=dia)

#Vista de las solicitudes
@app.route('/solicitudes')
@login_required
def Solicitudes():
    # Redirige al login a quien no tenga rol de adminitrador (Evita que se ingrese al panel de administración usando la URL)
    if session['id_roles'] != 1:
        return redirect(url_for('login'))
    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 1)
    #Selecciona todas las solicitudes de orientación psicologicas que han hecho los estudiantes ordenandolas por fechas
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM citas ORDER BY estado DESC, fecha ASC, hora ASC')
    citas = cur.fetchall()
    #Formatea la fecha y hora
    for cita in citas:
        cita['fecha'] = format_date(datetime.combine(cita['fecha'], time()), 'd MMM', locale='es_ES')
        cita['hora'] = (datetime.min + cita['hora']).time().strftime('%I:%M %p')
    citas_no_leidas = [cita for cita in citas if cita['estado'] == "no leido"]
    citas_leidas = [cita for cita in citas if cita['estado'] == "leido"]
    return render_template('auth/solicitudes.html', citas_no_leidas=citas_no_leidas, citas_leidas=citas_leidas, perfil_usuario=perfil_usuario)

#Vista que muestra los detalles de una cita (por ID) en concreto
@app.route('/detalle_cita/<id>')
@login_required
def detalle_cita(id):
    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 1)
    #Actualiza el estado de esa cita en concreto de "No leído" a "leido" cuando se le da click a esa cita
    cur = mysql.connection.cursor()
    cur.execute('UPDATE citas SET estado = "leido" WHERE id = %s', (id,))
    mysql.connection.commit()
    #Selecciona toda la información almacenada de la cita en especifico
    cur.execute('SELECT * FROM citas WHERE id = %s', (id,))
    cita = cur.fetchone()
    #Cambia formato con el que se muesra la fecha y hora
    cita['fecha'] = format_date(datetime.combine(cita['fecha'], time()), 'd \'de\' MMMM', locale='es_ES')
    cita['hora'] = (datetime.min + cita['hora']).time().strftime('%I:%M %p')
    return render_template('auth/detalle_cita.html', cita=cita, perfil_usuario=perfil_usuario)

#CODIGO DEL CHATBOT
#Nueva instancia de la clase (ChatOpenAI) que se usará para interactuar con el modelo (ft:gpt-3.5-turbo-0125:personal::94x67a1Q) de la API de OpenAI
llm = ChatOpenAI(temperature=0.5,
                 model='ft:gpt-3.5-turbo-0125:personal::9mpoKFq7',
                 top_p=1,
                 frequency_penalty=0.5,
                 presence_penalty=0,
                 openai_api_key='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')
#Esto formatea las entradas y define como presenta la información el modelo
template = """
Eres Psicobot, un asistente psicologico virtual y empático que trata de ayudar a los estudiantes de Corposucre con la gestión de sus emociones lo mejor posible.

Conversación previa:
{chat_history}

Nueva pregunta del humano: {question}
AI:
"""
#Nueva instancia de la clase PromptTemplate usando el template que está arriba
prompt_template = PromptTemplate.from_template(template)
#Nueva instancia de la clase ConversationBufferMemory,AQUÍ SE LAMACENA EL HISTORIAL DEL CHAT PARA DARLE MEMORIA AL CHATBOT
memory = ConversationBufferMemory(memory_key="chat_history")
#Nueva instancia de la clase LLMChain para ENCADENAR TODAS LAS PERTES ANTERIORES Y MANTENER EL HILO DE LA CONVERSACIÓN CON EL USUARIO
conversation = LLMChain(
    llm=llm,
    prompt=prompt_template,
    memory=memory,
    # ESTE PARAMETRO DEBE ESTAR EN TRUE SI SE LE QUIERE HACER SEGUIMIENTO A LO QUE PASA EN EL CHAIN
    verbose=True
)

#Vista del panel de usuario
@app.route('/PanelDeUsuario', methods=['GET', 'POST'])
@login_required
def PanelDeUsuario():
    #Redirige al login a quien no tenga rol de usuario
    if session['id_roles'] != 2:
        return redirect(url_for('login'))
    #Verifica si "conversacion" se inició al logearse el usuario y la inicia en caso de que no sea así
    if 'conversacion' not in session:
        session['conversacion'] = []
    # Obtiene el perfil del usuario actual
    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 2)
    #Verifica que el metodo de la solicitud sea POST
    if request.method == 'POST':
        #Obtiene todo lo que se escriba en el campo chat
        chat = request.form.get('chat')
        #Si se ha escrito un mensaje en Chat...
        if chat != None:
            # Añade ese mensaje del usuario a la lista
            session['conversacion'].append({'rol': 'usuario', 'mensaje': chat})
            # Luego llama a la API de OpenAI
            respuesta = conversation(chat)
            # Y añade la respuesta del modelo a la lista
            session['conversacion'].append({'rol': 'modelo', 'mensaje': respuesta['text']})
            #return jsonify({'usuario': {'rol': 'usuario', 'mensaje': chat}, 'modelo': {'rol': 'modelo', 'mensaje': respuesta['text']}})
            #return redirect(url_for('PanelDeUsuario'))
    #Renderiza la vista del chatbot con todos los mensajes tanto del chatbot, como del usuario (Almacenados en Conversación)
    return render_template('auth/user.html', conversacion=session.get('conversacion', []), perfil_usuario=perfil_usuario)

#Clase para crear los campos del formulario de citas de orientación psicologica y sus reglas de validación
class NotificarForm(FlaskForm):
    numero_id = StringField('Número de Identificación', validators=[DataRequired(), Regexp(r'^\d{1,10}$', message="Debe ser un número de hasta 10 dígitos")])
    nombres = StringField('Nombres', validators=[DataRequired(), Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$', message="Solo se permiten letras")])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$', message="Solo se permiten letras")])
    email = EmailField('Correo Insitucional', validators=[DataRequired(), EmailValidator()])
    cellphone = StringField('Número de contacto', validators=[DataRequired(), Regexp(r'^\d{10}$', message="Debe ser un número de exactamente 10 dígitos")])
    publico = RadioField('Publico al que pertenece', choices=[('estudiante', 'Estudiante'), ('egresado', 'Egresado'),
                                                              ('egresado no graduado', 'Egresado NO Graduado'),
                                                              ('docente', 'Docente'),
                                                              ('administratico', 'Administratico')],
                         validators=[DataRequired()])
    programa = StringField('Programa', validators=[DataRequired(), Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$', message="Solo se permiten letras")])
    semestre = SelectField('Semestre', choices=[('', 'Seleccionar semestre')] + [(str(i), str(i)) for i in range(1, 11)] + [('11', 'No Aplica')], validators=[DataRequired()])
    fecha = DateField('Fecha', format='%Y-%m-%d', validators=[DataRequired()], render_kw={'min': date.today()})
    hora = TimeField('Hora', validators=[DataRequired(), TimeRange(min_time=time(6), max_time=time(18,59))])
    asunto = TextAreaField('Motivo de consulta', validators=[DataRequired()])
    submit = SubmitField('Enviar')

#Vista para notificar al correo
@app.route('/SolicitarCita', methods=['GET', 'POST'])
@login_required
def SolicitarCita():
    # Redirige al login a quien no tenga rol de usuario
    if session['id_roles'] != 2:
        return redirect(url_for('login'))
    perfil_usuario = obtener_perfil_usuario(session['nombre_usuario'], 2)
    #Selecciona de la base de datos las fechas establecidas para el horario de atención en una semana (de martes a martes por ejemplo)
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM horarios ORDER BY FIELD(dia, "Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"), hora_inicio_am, hora_fin_am, hora_inicio_pm, hora_fin_pm')
    horarios = cur.fetchall()
    #Muestra las fechas del horario de atención que se encuentran en la base de datos, en casode encontrarlas
    for horario in horarios:
        # Formatea las horas para eliminar los segundos y convertirlas a formato de 12 horas
        if horario['hora_inicio_am'] is not None:
            horario['hora_inicio_am'] = datetime.strptime(':'.join(str(horario['hora_inicio_am']).split(':')[:2]),'%H:%M').strftime('%I:%M %p')
        if horario['hora_fin_am'] is not None:
            horario['hora_fin_am'] = datetime.strptime(':'.join(str(horario['hora_fin_am']).split(':')[:2]),'%H:%M').strftime('%I:%M %p')
        if horario['hora_inicio_pm'] is not None:
            horario['hora_inicio_pm'] = datetime.strptime(':'.join(str(horario['hora_inicio_pm']).split(':')[:2]),'%H:%M').strftime('%I:%M %p')
        if horario['hora_fin_pm'] is not None:
            horario['hora_fin_pm'] = datetime.strptime(':'.join(str(horario['hora_fin_pm']).split(':')[:2]),'%H:%M').strftime('%I:%M %p')
    #Instancia de la clase con los campos y reglas de validación del formulario
    form = NotificarForm()
    #Valida el formulario si todos los campos cumplan las reglas de validación
    if form.validate_on_submit():
        numero_id = form.numero_id.data
        nombres = form.nombres.data
        apellidos = form.apellidos.data
        email = form.email.data
        cellphone = form.cellphone.data
        publico = form.publico.data
        programa = form.programa.data
        semestre = form.semestre.data
        fecha = form.fecha.data
        hora = form.hora.data
        asunto = form.asunto.data
        #Agrega la solicitud de cita a la tabla de citas
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO citas (numero_id, nombres, apellidos, email, cellphone, publico, programa, semestre, fecha, hora, asunto, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "no leido")', (numero_id, nombres, apellidos, email, cellphone, publico, programa, semestre, fecha, hora, asunto))
        #Se conecta a la bse de datos para guardar los datos
        mysql.connection.commit()
        # Convertir la hora a formato de 12 horas sin segundos
        hora_str = hora.strftime('%H:%M:%S')  # Convertir a cadena
        hora_24 = datetime.strptime(hora_str, '%H:%M:%S')
        hora_12 = hora_24.strftime('%I:%M %p')  # Formato 12 horas sin segundos
        solicitud_url = url_for('Solicitudes', _external=True)
        msg = Message("Solicitud de Cita de Orientación Psicológica",
                      recipients=["deider_ruiz@uajs.edu.co"])
        msg.body = f"Se ha recibido una nueva solicitud de cita de orientación psicológica.\n\nDetalles de la solicitud:\n\nSolicitante: {nombres} {apellidos}\nCorreo electrónico: {email}\nNúmero de Telefono: {cellphone}\nFecha y hora de la solicitud: {fecha} a las {hora_12}\nAsunto: {asunto}\n\nPor favor, revise esta solicitud lo antes posible.\n{solicitud_url}"
        mail.send(msg)
        # Redirige a la vista de las de la solicitud con un mensaje de exito
        flash('La solicitud de cita de oprientación psicológica se ha enviado correctamente', 'success')
        return redirect(url_for('SolicitarCita'))
    else:#Sino se cumple alguna regla de validación no manda nada y muestra mensajes de error
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en el campo {getattr(form, field).label.text}: {error}")
    return render_template('auth/solicitar_cita.html', horarios=horarios, form=form, perfil_usuario=perfil_usuario)

def actualizar_perfil(idusers, nombre_usuario, email):
    try:
        cur = mysql.connection.cursor()
        # Verificar si el nuevo nombre de usuario ya existe
        cur.execute('SELECT * FROM users WHERE nombre_usuario = %s', (nombre_usuario,))
        existing_user = cur.fetchone()
        if existing_user and existing_user['idusers'] != idusers:
            flash('El nombre de usuario ya existe, intenta con otro diferente', 'error')
        else:
            cur.execute('UPDATE users SET nombre_usuario = %s, email = %s WHERE idusers = %s', (nombre_usuario, email, idusers))
            mysql.connection.commit()
            flash('¡Perfil actualizado! Es posible que los cambios tarden en mostrarse.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error al actualizar el perfil: {}'.format(e), 'error')

def cambiar_contrasena(idusers, password):
    try:
        password = password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute('UPDATE users SET password = %s WHERE idusers = %s', (hashed_password, idusers))
        mysql.connection.commit()
        flash('Contraseña cambiada con éxito', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error al cambiar la contraseña: {}'.format(e), 'error')

def borrar_cuenta(idusers):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM users WHERE idusers = %s', [idusers])
        mysql.connection.commit()
        flash('Cuenta borrada con éxito', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Error al borrar la cuenta: {}'.format(e), 'error')

#Clase para crea inputs y reglas de validación para actualizar la cuenta
class UpdateProfileForm(FlaskForm):
    nombre_usuario = StringField('Nombre De Usuario', validators=[DataRequired(), Length(min=3, max=40),
                                                                  Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ]',
                                                                         message="El nombre de usuario debe comenzar con una letra"),
                                                                  Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9_]*$',
                                                                         message="El nombre de usuario solo puede contener letras, números y guiones bajos")])
    email = EmailField('Correo Institucional', validators=[DataRequired(), Length(min=3, max=40), EmailValidator()])
    updateProfile = SubmitField('Actualizar Perfil')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=25)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), Length(min=6, max=25), EqualTo('password', message='Las contraseñas deben coincidir')])
    updatePassword = SubmitField('Cambiar Contraseña')

class DeleteAccountForm(FlaskForm):
    DeleteAccount = SubmitField('Si, Borrar cuenta')

# Vista del perfil del usuario
@app.route('/perfil/<nombre_usuario>', methods=['GET', 'POST'])
@login_required
def perfil(nombre_usuario):
    # Obtiene el rol del usuario actual
    id_roles = session['id_roles']
    idusers = session['id']
    # Verifica que el usuario logueado es el mismo que el usuario del perfil que se está intentando ver
    if nombre_usuario != session['nombre_usuario'] and id_roles == 1:
        return redirect(url_for('PanelDeAdministracion'))
    if nombre_usuario != session['nombre_usuario'] and id_roles == 2:
        return redirect(url_for('PanelDeUsuario'))
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
            return render_template('auth/perfil.html', update_profile_form=update_profile_form,
                                   change_password_form=change_password_form,
                                   delete_account_form=delete_account_form, perfil_usuario=perfil_usuario)
        elif change_password_form.validate_on_submit() and change_password_form.updatePassword.data:
            # Cambiar contraseña
            cambiar_contrasena(idusers, change_password_form.password.data)
            # Actualizar los datos del formulario de actualización de perfil
            update_profile_form.nombre_usuario.data = session['nombre_usuario']
            update_profile_form.email.data = session['email']
            return render_template('auth/perfil.html', update_profile_form=update_profile_form,
                                   change_password_form=change_password_form, delete_account_form=delete_account_form,
                                   perfil_usuario=perfil_usuario)
        elif delete_account_form.validate_on_submit() and delete_account_form.DeleteAccount.data:
            # Borrar cuenta
            borrar_cuenta(idusers)
            return redirect(url_for('login'))
        #pass
    return render_template('auth/perfil.html', update_profile_form=update_profile_form, change_password_form=change_password_form, delete_account_form=delete_account_form, perfil_usuario=perfil_usuario)

#prevenir inyección HTML mediante URL
#convierte codigo enviado desde la URL transofmandolo en un string
from markupsafe import escape
@app.route('/code/<path:code>')
def code(code):
    return f'<code>{escape(code)}</code>'

#Verifica que el Script actual se ejecute de forma directa, en lugar decuando se importa algún modulo
if __name__== '__main__':
    #Inicia la app de Flask en modo DEPURACIÓN, en el HOST 0.0.0.0 y PUERTO 5000 y permite la ejecución de múltiples solicitudes simultáneamente
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
