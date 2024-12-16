from flask import flash, redirect, url_for, session
import logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

def redirigir_error(e):
    logging.error(f"Error crítico: {e}")
    flash("Ha ocurrido un error inesperado. Intenta de nuevo más tarde.", "fatal error")
    session['error_redirected'] = True
    return redirect(url_for('views.error_view'))
