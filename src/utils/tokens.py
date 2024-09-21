from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature, BadSignature

def init_serializer(secret_key, salt="auth"):
    return URLSafeTimedSerializer(secret_key, salt=salt)

def generar_token(email, secret_key, salt='reset-forbidden-password'):
    serializer = init_serializer(secret_key, salt)
    return serializer.dumps(email, salt=salt)

def verificar_token(token, secret_key, salt='reset-forbidden-password', max_age=3600):
    try:
        serializer = init_serializer(secret_key, salt)
        resultado = serializer.loads_unsafe(token, salt=salt, max_age=max_age)
        return resultado, None
    except SignatureExpired:
        return None, 'El enlace de restablecimiento de contraseña ha expirado.'
    except (BadTimeSignature, BadSignature):
        return None, 'El enlace de restablecimiento de contraseña es inválido.'
    except Exception as e:
        return None, f'Ocurrió un error: {str(e)}'