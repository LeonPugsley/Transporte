from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import Usuario


class EditProfileForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    email = StringField('Emai', validators=[DataRequired(), Email()])
    cpf = StringField('CPF', validators=[DataRequired()])
    curso = StringField('Curso', validators=[DataRequired()])
    instituto = StringField('Instituto', validators=[DataRequired()])
    periodo = StringField('Periodo', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, usuario, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
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


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class MessageForm(FlaskForm):
    mensagem = TextAreaField('Mensagem', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
