from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import Usuario
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(nome=form.nome.data).first()
        if usuario is None or not usuario.check_password(form.senha.data):
            flash('Usuario ou Senha invalidos')
            return redirect(url_for('auth.login'))
        login_user(usuario, remember=form.manter_logado.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Entrar', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario:
            send_password_reset_email(usuario)
        flash('Confira em seu email as instruções para redefinição de senha')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Resetar Senha', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    usuario = Usuario.verify_reset_password_token(token)
    if not usuario:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        usuario.set_password(form.senha.data)
        db.session.commit()
        flash('Sua senha foi redefinida.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
