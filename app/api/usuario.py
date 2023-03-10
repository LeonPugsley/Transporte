from flask import jsonify, request, url_for, abort
from app import db
from app.models import Usuario
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request


@bp.route('/usuario/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(Usuario.query.get_or_404(id).to_dict())


@bp.route('/usuarios', methods=['GET'])
@token_auth.login_required
def get_users():
    pagina = request.args.get('page', 1, type=int)
    por_pagina = min(request.args.get('per_page', 10, type=int), 100)
    data = Usuario.to_collection_dict(Usuario.query, pagina, por_pagina, 'api.get_users')
    return jsonify(data)


@bp.route('/usuarios', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'nome' not in data or 'email' not in data or 'senha' not in data:
        return bad_request('deve conter nome, email e password preenchidos')
    if Usuario.query.filter_by(nome=data['nome']).first():
        return bad_request('Por favor use um nome diferente')
    if Usuario.query.filter_by(email=data['email']).first():
        return bad_request('Por favor use um email diferente')
    usuario = Usuario()
    usuario.from_dict(data, novo_usuario=True)
    db.session.add(usuario)
    db.session.commit()
    response = jsonify(usuario.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=usuario.id)
    return response


@bp.route('/usuarios/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    usuario = Usuario.query.get_or_404(id)
    data = request.get_json() or {}
    if 'nome' in data and data['nome'] != usuario.nome and \
            Usuario.query.filter_by(nome=data['nome']).first():
        return bad_request('Por favor use um nome diferente')
    if 'email' in data and data['email'] != usuario.email and \
            Usuario.query.filter_by(email=data['email']).first():
        return bad_request('Por favor use um email diferente')
    usuario.from_dict(data, novo_usuario=False)
    db.session.commit()
    return jsonify(usuario.to_dict())
