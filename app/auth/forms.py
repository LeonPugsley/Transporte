from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    manter_logado = BooleanField('Manter Logado')
    submit = SubmitField('Entrar')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar redefinição de senha')


class ResetPasswordForm(FlaskForm):
    senha = PasswordField('Senha', validators=[DataRequired()])
    senha2 = PasswordField(
        'Repita a senha', validators=[DataRequired(),
                                      EqualTo('senha')])
    submit = SubmitField('Solicitar redefinição de senha')
