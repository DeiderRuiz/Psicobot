from wtforms import ValidationError

# Validar que los campos de tiempo estén dentro de cierto rango
class TimeRange(object):
    def __init__(self, min_time, max_time, message=None):
        self.min_time = min_time
        self.max_time = max_time
        if not message:
            min_time_12h = self.min_time.strftime('%I:%M %p')
            max_time_12h = self.max_time.strftime('%I:%M %p')
            message = u'El horario debe estar entre %s y %s.' % (min_time_12h, max_time_12h)
        self.message = message

    def __call__(self, form, field):
        if field.data is None:
            return
        if field.data < self.min_time or field.data > self.max_time:
            raise ValidationError(self.message)

# Validar 2 o más rangos de horas
class MultipleTimeRange(object):
    def __init__(self, ranges, message=None):
        self.ranges = ranges
        if not message:
            range_strs = []
            for min_time, max_time in self.ranges:
                min_time_12h = min_time.strftime('%I:%M %p')
                max_time_12h = max_time.strftime('%I:%M %p')
                range_strs.append(f'{min_time_12h} y {max_time_12h}')
            message = u'El horario debe estar entre %s.' % ' o '.join(range_strs)
        self.message = message

    def __call__(self, form, field):
        if field.data is None:
            return
        for min_time, max_time in self.ranges:
            if min_time <= field.data <= max_time:
                return
        raise ValidationError(self.message)

# Validar servidor de correo electrónico
class EmailValidator(object):
    def __init__(self, message=None):
        if not message:
            message = u'Por favor, ingresa un correo electrónico institucional válido.'
        self.message = message

    def __call__(self, form, field):
        if not field.data.endswith('@uajs.edu.co'):
            raise ValidationError(self.message)
