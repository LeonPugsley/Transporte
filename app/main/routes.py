from datetime import datetime, date
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy import desc
from app import db
from app.admin.routes import editar_veiculodia
from app.main.forms import EditProfileForm, EmptyForm, MessageForm
from app.models import Usuario, Aluno, Mensagem, Notificacao, Rotadia, Data, Historico, Rota, Motorista, Veiculo
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated or current_user.is_anonymous:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = EmptyForm()
    aluno = Aluno.query.filter_by(usuario_id=current_user.id).first_or_404()
    if form.validate_on_submit():
        pass

    return render_template('index.html', form=form, title='Voce ira Hoje?')


@bp.route('/obrigado')
@login_required
def obrigado():
    aluno = Aluno.query.filter_by(usuario_id=current_user.id).first_or_404()
    aluno.respondido = True
    db.session.commit()
    return render_template('obrigado.html', title='Obrigado')


@bp.route('/alterar')
@login_required
def alterar():
    aluno = Aluno.query.filter_by(usuario_id=current_user.id).first_or_404()
    historico = Historico.query.order_by(Historico.data.desc()).first()
    data = Data.query.filter_by(historico_id=historico.id).first()
    rotadia = Rotadia.query.filter_by(rota_id=aluno.rota_id, data_id=data.id).first()
    aluno.respondido = True
    aluno.confirmado = not aluno.confirmado

    if aluno.confirmado:
        rotadia.confirmados.append(aluno)
    else:
        rotadia.confirmados.remove(aluno)

    if len(rotadia.confirmados) > rotadia.veiculodia.lugares:
        veiculos = Veiculo.query.order_by(Veiculo.lugares).all()

        for veiculo in veiculos:
            if len(rotadia.confirmados) < veiculo.lugares:
                editar_veiculodia(rotadia.id, veiculo.id)
                break

    db.session.commit()
    return render_template('obrigado.html', title='Obrigado')


@bp.route('/confirma', methods=['GET', 'POST'])
@login_required
def confirma():
    historico = Historico.query.order_by(Historico.data.desc()).first()
    if historico is None or historico.data != date.today():
        historico = Historico(data=date.today())
        db.session.add(historico)
        db.session.commit()
        alunos = Aluno.query.order_by(Aluno.id).all()
        rotas = Rota.query.order_by(Rota.id).all()
        usuario_vazio = Usuario.query.filter_by(nome='vazio').first()
        motorista = Motorista.query.filter_by(usuario_id=usuario_vazio.id).first()
        veiculo = Veiculo.query.filter_by(placa="AAA-0000").first()
        data = Data(historico_id=historico.id)
        db.session.add(data)
        db.session.commit()

        for aluno in alunos:
            aluno.respondido = False
            aluno.confirmado = False
            db.session.add(aluno)
            db.session.commit()

        for rota in rotas:
            rotadia = Rotadia(motorista_id=motorista.id, veiculo_id=veiculo.id, rota_id=rota.id, data_id=data.id)
            db.session.add(rotadia)
            db.session.commit()

    aluno = Aluno.query.filter_by(usuario_id=current_user.id).first_or_404()
    data = Data.query.filter_by(historico_id=historico.id).first()
    rotadia = Rotadia.query.filter_by(rota_id=aluno.rota_id, data_id=data.id).first()
    rotadia.confirmados.append(aluno)
    aluno.confirmado = True
    aluno.respondido = True
    db.session.add(aluno)
    db.session.add(rotadia)

    if len(rotadia.confirmados) > rotadia.veiculodia.lugares:
        veiculos = Veiculo.query.order_by(Veiculo.lugares).all()

        for veiculo in veiculos:
            if len(rotadia.confirmados) < veiculo.lugares:
                editar_veiculodia(rotadia.id, veiculo.id)
                break

    db.session.add(historico)
    db.session.commit()
    return render_template('obrigado.html', title='Obrigado')


@bp.route('/usuario/<nome>')
@login_required
def usuario(nome):
    usuario = Usuario.query.filter_by(nome=nome).first_or_404()
    form = EmptyForm()
    return render_template('usuario.html', usuario=usuario, form=form)


@bp.route('/usuario/<nome>/popup')
@login_required
def usuario_popup(nome):
    usuario = Usuario.query.filter_by(nome=nome).first_or_404()
    form = EmptyForm()
    return render_template('usuario_popup.html', usuario=usuario, form=form)


@bp.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = EditProfileForm(current_user)
    aluno = Aluno.query.filter_by(usuario_id=current_user.id).first()
    if form.validate_on_submit():
        current_user.nome = form.nome.data
        current_user.telefone = form.telefone.data
        current_user.email = form.email.data
        current_user.cpf = form.cpf.data
        aluno.curso = form.curso.data
        aluno.instituto = form.instituto.data
        aluno.periodo = form.periodo.data
        db.session.commit()
        flash('Suas alterações foram salvas.')
        return redirect(url_for('main.editar_perfil'))
    elif request.method == 'GET':
        form.nome.data = current_user.nome
        form.telefone.data = current_user.telefone
        form.email.data = current_user.email
        form.cpf.data = current_user.cpf
        form.curso.data = aluno.curso
        form.instituto.data = aluno.instituto
        form.periodo.data = aluno.periodo
    return render_template('editar_perfil.html', title='Editar Perfil',
                           form=form)


@bp.route('/mandar_mensagem/<destinatario>', methods=['GET', 'POST'])
@login_required
def mandar_mensagem(destinatario):
    usuario = Usuario.query.filter_by(nome=destinatario).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Mensagem(remetente=current_user, destinatario=usuario,
                       corpo=form.mensagem.data)
        db.session.add(msg)
        usuario.add_notificacao('unread_message_count', usuario.novas_mensagens())
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('main.index'))
    return render_template('mandar_mensagem.html', title='Mandar Mensagem',
                           form=form, destinatario=destinatario)


@bp.route('/mensagens')
@login_required
def mensagens():
    current_user.ultima_vez_lido_mensagem = datetime.utcnow()
    current_user.add_notificacao('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    mensagens = current_user.mensagens_recebidas.order_by(
        Mensagem.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.mensagens', page=mensagens.next_num) \
        if mensagens.has_next else None
    prev_url = url_for('main.mensagens', page=mensagens.prev_num) \
        if mensagens.has_prev else None
    return render_template('mensagem.html', mensagens=mensagens.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/notificacoes')
@login_required
def notificacoes():
    since = request.args.get('since', 0.0, type=float)
    notificacoes = current_user.notificacoes.filter(
        Notificacao.timestamp > since).order_by(Notificacao.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notificacoes])


@bp.route('/conf', methods=['GET', 'POST'])
def conf():
    for i in range(50):
        historico = Historico.query.order_by(Historico.data.desc()).first()
        if historico is None or historico.data != date.today():
            historico = Historico(data=date.today())
            db.session.add(historico)
            db.session.commit()
            alunos = Aluno.query.order_by(Aluno.id).all()
            rotas = Rota.query.order_by(Rota.id).all()
            usuario_vazio = Usuario.query.filter_by(nome='vazio').first()
            motorista = Motorista.query.filter_by(usuario_id=usuario_vazio.id).first()
            veiculo = Veiculo.query.filter_by(placa="AAA-0000").first()
            data = Data(historico_id=historico.id)
            db.session.add(data)
            db.session.commit()

            for aluno in alunos:
                aluno.respondido = False
                aluno.confirmado = False
                db.session.add(aluno)
                db.session.commit()

            for rota in rotas:
                rotadia = Rotadia(motorista_id=motorista.id, veiculo_id=veiculo.id, rota_id=rota.id, data_id=data.id)
                db.session.add(rotadia)
                db.session.commit()

        aluno = Aluno.query.filter_by(usuario_id=i+8).first_or_404()
        data = Data.query.filter_by(historico_id=historico.id).first()
        rotadia = Rotadia.query.filter_by(rota_id=aluno.rota_id, data_id=data.id).first()
        rotadia.confirmados.append(aluno)
        aluno.confirmado = True
        aluno.respondido = True
        db.session.add(aluno)
        db.session.add(rotadia)

        if len(rotadia.confirmados) > rotadia.veiculodia.lugares:
            veiculos = Veiculo.query.order_by(Veiculo.lugares).all()

            for veiculo in veiculos:
                if len(rotadia.confirmados) < veiculo.lugares:
                    editar_veiculodia(rotadia.id, veiculo.id)
                    break

        db.session.add(historico)
        db.session.commit()

    return render_template('obrigado.html', title='Obrigado')
