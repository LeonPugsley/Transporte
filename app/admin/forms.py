from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import Usuario


class RegistrationAlunoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cpf = StringField('CPF', validators=[DataRequired()])
    curso = StringField('Curso', validators=[DataRequired()])
    instituto = StringField('Instituto', validators=[DataRequired()])
    periodo = StringField('Periodo', validators=[DataRequired()])
    categoria = StringField('Categoria', validators=[DataRequired()])
    rota = StringField('Nome da Rota', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    senha2 = PasswordField(
        'Repita a Senha', validators=[DataRequired(),
                                      EqualTo('senha')])
    submit = SubmitField('Cadastrar')

    def validate_nome(self, nome):
        usuario = Usuario.query.filter_by(nome=nome.data).first()
        if usuario is not None:
            raise ValidationError('Por favor use um nome diferente.')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario is not None:
            raise ValidationError('Por favor use um email diferente.')

    def validate_telefone(self, telefone):
        usuario = Usuario.query.filter_by(email=telefone.data).first()
        if usuario is not None:
            raise ValidationError('Por favor use um telefone diferente.')

    def validate_cpf(self, cpf):
        usuario = Usuario.query.filter_by(email=cpf.data).first()
        if usuario is not None:
            raise ValidationError('Por favor use um CPF diferente.')


class RegistrationMotoristaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    cpf = StringField('CPF', validators=[DataRequired()])
    habilitacao = StringField('Habilitação', validators=[DataRequired()])
    is_admin = BooleanField('Conceder permição de administrador?')
    senha = PasswordField('Senha', validators=[DataRequired()])
    senha2 = PasswordField(
        'Repita a Senha', validators=[DataRequired(),
                                      EqualTo('senha')])
    submit = SubmitField('Cadastrar')

    def validate_nome(self, nome):
        usuario = Usuario.query.filter_by(nome=nome.data).first()
        if usuario is not None:
            raise ValidationError('Por favor use um nome diferente.')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario is not None:
            raise ValidationError('Por favor use um email diferente.')

    def validate_telefone(self, telefone):
        usuario = Usuario.query.filter_by(email=telefone.data).first()
        if usuario is not None:
            raise ValidationError('Por favor use um telefone diferente.')

    def validate_cpf(self, cpf):
        usuario = Usuario.query.filter_by(email=cpf.data).first()
        if usuario is not None:
            raise ValidationError('Por favor use um CPF diferente.')


class RegistrationVeiculoForm(FlaskForm):
    modelo = StringField('Modelo', validators=[DataRequired()])
    placa = StringField('Placa', validators=[DataRequired()])
    tamanho = StringField('Tamanho', validators=[DataRequired()])
    lugares = IntegerField('Lugares', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')


class RegistrationRotaForm(FlaskForm):
    nome_rota = StringField('Nome da Rota', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')


class EditAlunoProfileForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    email = StringField('Emai', validators=[DataRequired(), Email()])
    cpf = StringField('CPF', validators=[DataRequired()])
    curso = StringField('Curso', validators=[DataRequired()])
    instituto = StringField('Instituto', validators=[DataRequired()])
    periodo = StringField('Periodo', validators=[DataRequired()])
    categoria = StringField('Categoria', validators=[DataRequired()])
    rota = StringField('Rota do Aluno', validators=[DataRequired()])
    submit = SubmitField('Editar')

    def __init__(self, usuario, *args, **kwargs):
        super(EditAlunoProfileForm, self).__init__(*args, **kwargs)
        self.nome_original = usuario.nome
        self.email_original = usuario.email
        self.telefone_original = usuario.telefone
        self.cpf_original = usuario.cpf

    def validate_username(self, nome):
        if nome.data != self.nome_original:
            usuario = Usuario.query.filter_by(nome=self.nome.data).first()
            if usuario is not None:
                raise ValidationError('Por favor use um nome diferente.')

    def validate_email(self, email):
        if email.data != self.email_original:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario is not None:
                raise ValidationError('Por favor use um email diferente.')

    def validate_telefone(self, telefone):
        if telefone.data != self.telefone_original:
            usuario = Usuario.query.filter_by(email=telefone.data).first()
            if usuario is not None:
                raise ValidationError('Por favor use um telefone diferente.')

    def validate_cpf(self, cpf):
        if cpf.data != self.cpf_original:
            usuario = Usuario.query.filter_by(email=cpf.data).first()
            if usuario is not None:
                raise ValidationError('Por favor use um CPF diferente.')


class EditMotoristaProfileForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    email = StringField('Emai', validators=[DataRequired(), Email()])
    cpf = StringField('CPF', validators=[DataRequired()])
    habilitacao = StringField('Habilitação', validators=[DataRequired()])
    is_admin = BooleanField('Conceder permição de administrador?')

    submit = SubmitField('Editar')

    def __init__(self, usuario, *args, **kwargs):
        super(EditMotoristaProfileForm, self).__init__(*args, **kwargs)
        self.nome_original = usuario.nome
        self.email_original = usuario.email
        self.telefone_original = usuario.telefone
        self.cpf_original = usuario.cpf

    def validate_username(self, nome):
        if nome.data != self.nome_original:
            usuario = Usuario.query.filter_by(nome=self.nome.data).first()
            if usuario is not None:
                raise ValidationError('Por favor use um nome diferente.')

    def validate_email(self, email):
        if email.data != self.email_original:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario is not None:
                raise ValidationError('Por favor use um email diferente.')

    def validate_telefone(self, telefone):
        if telefone.data != self.telefone_original:
            usuario = Usuario.query.filter_by(email=telefone.data).first()
            if usuario is not None:
                raise ValidationError('Por favor use um telefone diferente.')

    def validate_cpf(self, cpf):
        if cpf.data != self.cpf_original:
            usuario = Usuario.query.filter_by(email=cpf.data).first()
            if usuario is not None:
                raise ValidationError('Por favor use um CPF diferente.')


class EditVeiculoForm(FlaskForm):
    modelo = StringField('Modelo', validators=[DataRequired()])
    placa = StringField('Placa', validators=[DataRequired()])
    tamanho = StringField('Tamanho', validators=[DataRequired()])
    lugares = IntegerField('Lugares', validators=[DataRequired()])
    submit = SubmitField('Editar')


class EditRotaForm(FlaskForm):
    nome_rota = StringField('Nome da Rota', validators=[DataRequired()])
    submit = SubmitField('Editar')


class EmptyForm(FlaskForm):
    submit = SubmitField('Enviar')


class MessageForm(FlaskForm):
    mensagem = TextAreaField('Mensagem', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Enviar')
