from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, mensagem=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if mensagem:
        payload['message'] = mensagem
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(mensagem):
    return error_response(400, mensagem)
