from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import Usuario
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(nome, senha):
    usuario = Usuario.query.filter_by(nome=nome).first()
    if usuario and usuario.check_password(senha):
        return usuario


@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)


@token_auth.verify_token
def verify_token(token):
    return Usuario.check_token(token) if token else None


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)
