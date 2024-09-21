from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField, PasswordField, DateField, TimeField, RadioField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Regexp, Length, Optional, EqualTo
from datetime import date, time
from src.utils.validators import TimeRange, MultipleTimeRange, EmailValidator

def clean_whitespace(data):
    return ' '.join(data.split())

def strip_and_normalize_whitespace(form, field):
    field.data = clean_whitespace(field.data)
    if not field.data:
        raise ValidationError('Este campo es requerido.')


# Clase para crear inputs y reglas de validación para el login
class LoginForm(FlaskForm):
    nombre_usuario = StringField('Nombre De Usuario o Correo Institucional', validators=[
        DataRequired(),
        Length(min=3, max=150),
        Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ][a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$|^.*@.*\..*$',
               message="Debe ser un nombre de usuario válido o un correo electrónico"),
        strip_and_normalize_whitespace
    ])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

# Clase para crea inputs y reglas de validación para el registro
class RegisterForm(FlaskForm):
    nombre_usuario = StringField('Nombre De Usuario', validators=[DataRequired(), Length(min=3, max=50),
                                                                  Regexp(
                                                                      r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ][a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$',
                                                                      message="El nombre de usuario solo puede contener letras y espacios, y debe comenzar con una letra"),strip_and_normalize_whitespace])
    email = EmailField('Correo Institucional', validators=[DataRequired(), Length(min=3, max=150), EmailValidator(),strip_and_normalize_whitespace])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), Length(min=6, max=50)])
    submit = SubmitField('Registrarse')

# Clase para crear inputs y reglas de validación para la recuperación de la contraseña
class ForbiddenPasswordForm(FlaskForm):
    email = EmailField('Correo Institucional', validators=[DataRequired(),strip_and_normalize_whitespace])
    submit = SubmitField('Recuperar contraseña')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), Length(min=6, max=50)])
    submit = SubmitField('Restablecer contraseña')

# Clase con los campos y reglas de validación del formulario de horario de atención
class HorarioForm(FlaskForm):
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dia = SelectField('Días de la semana', choices=[('', 'Seleccionar día')] + [(dia, dia) for dia in dias_semana], validators=[DataRequired()])
    hora_inicio_am = TimeField('Hora de inicio', validators=[Optional(), TimeRange(min_time=time(8, 00), max_time=time(10,00))])
    hora_fin_am = TimeField('Hora de fin', validators=[Optional(), TimeRange(min_time=time(9, 00), max_time=time(11,00))])
    hora_inicio_pm = TimeField('Hora de inicio', validators=[Optional(), TimeRange(min_time=time(14, 00), max_time=time(17,00))])
    hora_fin_pm = TimeField('Hora de fin', validators=[Optional(), TimeRange(min_time=time(15, 0), max_time=time(18,00))])
    submit = SubmitField('Aceptar')

class DeleteDayForm(FlaskForm):
    submit = SubmitField('Si, Borrar horario')

# Clase para crear los campos del formulario de citas de orientación psicologica y sus reglas de validación
class NotificarForm(FlaskForm):
    # Definir 2 rangos de tiempo para el campo "hora"
    ranges = [(time(8, 0), time(11, 0)), (time(14, 0), time(18, 0))]
    time_range_validator = MultipleTimeRange(ranges)
    # Reglas de validación
    numero_id = StringField('Número de Identificación', validators=[DataRequired(), Regexp(r'^\d{8,10}$', message="Debe ser un número de hasta 10 dígitos"),strip_and_normalize_whitespace])
    nombres = StringField('Nombres', validators=[DataRequired(), Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$', message="Solo se permiten letras"),strip_and_normalize_whitespace])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$', message="Solo se permiten letras"),strip_and_normalize_whitespace])
    email = EmailField('Correo Insitucional', validators=[DataRequired(), EmailValidator(),strip_and_normalize_whitespace])
    cellphone = StringField('Número de contacto', validators=[DataRequired(), Regexp(r'^\d{10,12}$', message="Debe ser un número de exactamente 10 dígitos"),strip_and_normalize_whitespace])
    publico = RadioField('Publico al que pertenece', choices=[('estudiante', 'Estudiante'), ('egresado', 'Egresado'),
                                                              ('egresado no graduado', 'Egresado NO Graduado'),
                                                              ('docente', 'Docente'),
                                                              ('administrativo', 'Administrativo')],
                         validators=[DataRequired()])
    carreras = ['Administración de Empresas', 'Administración de Negocios Internacionales', 'Comunicación Social', 'Contaduría Pública', 'Derecho', 'Enfermería', 'Fisioterapia', 'Ingeniería Electrónica', 'Ingeniería de Sistemas', 'Ingeniería Industrial', 'Mercadeo', 'Psicología', 'Seguridad y Salud en el Trabajo', 'Tecnología en Seguridad y Salud en el Trabajo']
    programa = SelectField('Programa', choices=[('', 'Seleccionar programa')] + [(programa, programa) for programa in carreras], validators=[DataRequired()])
    semestre = SelectField('Semestre', choices=[('', 'Seleccionar semestre')] + [(str(i), str(i)) for i in range(1, 11)] + [('11', 'No Aplica')], validators=[DataRequired()])
    fecha = DateField('Fecha para la cita', format='%Y-%m-%d', validators=[DataRequired()], render_kw={'min': date.today()})
    hora = TimeField('Hora para la cita', validators=[DataRequired(), time_range_validator])
    asunto = TextAreaField('Motivo de consulta', validators=[DataRequired(),strip_and_normalize_whitespace])
    submit = SubmitField('Enviar')

# Clase para crea inputs y reglas de validación para actualizar la cuenta
class UpdateProfileForm(FlaskForm):
    nombre_usuario = StringField('Nombre De Usuario', validators=[DataRequired(), Length(min=3, max=50),
                                                                  Regexp(
                                                                      r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ][a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$',
                                                                      message="El nombre de usuario solo puede contener letras y espacios, y debe comenzar con una letra"),strip_and_normalize_whitespace])
    email = EmailField('Correo Institucional', validators=[DataRequired(), Length(min=3, max=150), EmailValidator(),strip_and_normalize_whitespace])
    updateProfile = SubmitField('Actualizar Perfil')

class ChangePasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), Length(min=6, max=50), EqualTo('password', message='Las contraseñas deben coincidir')])
    updatePassword = SubmitField('Cambiar Contraseña')

class DeleteAccountForm(FlaskForm):
    DeleteAccount = SubmitField('Si, Borrar cuenta')
