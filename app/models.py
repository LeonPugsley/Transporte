import base64
import json
import jwt
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta, date
from hashlib import md5
from flask import current_app, url_for
from time import time
from app import db, login


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class Usuario(UserMixin, PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, index=True, default=False)
    nome = db.Column(db.String(64), index=True, unique=True)
    telefone = db.Column(db.String(14), unique=True)
    senha_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    cpf = db.Column(db.String(11), index=True, unique=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    aluno = db.relationship('Aluno', cascade="all,delete", backref='usuario_aluno')
    motorista = db.relationship('Motorista', cascade="all,delete", backref='usuario_motorista')
    ultima_vez_lido_mensagem = db.Column(db.DateTime)
    mensagens_enviadas = db.relationship('Mensagem',
                                         foreign_keys='Mensagem.remetente_id',
                                         backref='remetente', lazy='dynamic')
    mensagens_recebidas = db.relationship('Mensagem',
                                          foreign_keys='Mensagem.destinatario_id',
                                          backref='destinatario', lazy='dynamic')
    notificacoes = db.relationship('Notificacao', backref='usuario',
                                   lazy='dynamic')

    def __repr__(self):
        return '<Usuario {}>'.format(self.nome)

    def set_password(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'resetar_senha': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id.self = jwt.decode(token, current_app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['resetar_senha']
        except:
            return
        return Usuario.query.get(id)

    def novas_mensagens(self):
        ultima_vez_visto = self.ultima_vez_lido_mensagem or datetime(1900, 1, 1)
        return Mensagem.query.filter_by(destinatario=self).filter(
            Mensagem.timestamp > ultima_vez_visto).count()

    def add_notificacao(self, name, data):
        self.notificacoes.filter_by(name=name).delete()
        n = Notificacao(name=name, payload_json=json.dumps(data), usuario=self)
        db.session.add(n)
        return n

    def to_dict(self, incluir_email=False):
        data = {
            'id': self.id,
            'nome': self.nome,
            'criado_em': self.criado_em.isoformat() + 'Z',

            '_links': {
                'self': url_for('api.get_user', id=self.id),

                'avatar': self.avatar(128)
            }
        }
        if incluir_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, novo_usuario=False):
        for campo in ['nome', 'email']:
            if campo in data:
                setattr(self, campo, data[campo])
        if novo_usuario and 'senha' in data:
            self.set_password(data['senha'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        usuario = Usuario.query.filter_by(token=token).first()
        if usuario is None or usuario.token_expiration < datetime.utcnow():
            return None
        return usuario

    @login.user_loader
    def load_user(id):
        return Usuario.query.get(int(id))


class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    categoria = db.Column(db.String(10), index=True)
    curso = db.Column(db.String(50), index=True)
    instituto = db.Column(db.String(10), index=True)
    periodo = db.Column(db.String(10), index=True)
    respondido = db.Column(db.Boolean, index=True, default=False)
    confirmado = db.Column(db.Boolean, index=True, default=False)
    rotadia_id = db.Column(db.Integer, db.ForeignKey('rotadia.id'))
    rota_id = db.Column(db.Integer, db.ForeignKey('rota.id'))

    def __repr__(self):
        return '<Aluno {}>'.format(self.usuario_aluno.nome)


class Motorista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habilitacao = db.Column(db.String(10), index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    motoristasdia = db.relationship('Rotadia', cascade="all,delete", backref='motoristadia')

    def __repr__(self):
        return '<Motorista {}>'.format(self.usuario_motorista.nome)


class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(50), index=True)
    placa = db.Column(db.String(10), index=True)
    tamanho = db.Column(db.String(10), index=True)
    lugares = db.Column(db.Integer, index=True)
    usado = db.Column(db.Boolean, default=False)
    veiculosdia = db.relationship('Rotadia', cascade="all,delete", backref='veiculodia')

    def __repr__(self):
        return '<Veiculo {}>'.format(self.placa)


class Rota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_rota = db.Column(db.String(50), index=True)
    rotasdia = db.relationship('Rotadia', backref='nomerotadia')
    alunos = db.relationship('Aluno', backref='rota')

    def __repr__(self):
        return '<Rota {}>'.format(self.nome_rota)


class Rotadia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    confirmados = db.relationship('Aluno', backref='Rotadia')
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'))
    finalizada = db.Column(db.Boolean, default=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motorista.id'))
    rota_id = db.Column(db.Integer, db.ForeignKey('rota.id'))
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'))

    def __repr__(self):
        return '<dia {}>'.format(self.id)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    historico_id = db.Column(db.Integer, db.ForeignKey('historico.id'))
    rotasdia = db.relationship('Rotadia', cascade="all,delete", backref='datarota')

    def __repr__(self):
        return '<Data {}>'.format(self.id)


class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=date.today(), unique=True)
    datas = db.relationship('Data', cascade="all,delete", backref='historico')

    def __repr__(self):
        return '<Historico {}>'.format(self.data)


class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    corpo = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.corpo)


class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
