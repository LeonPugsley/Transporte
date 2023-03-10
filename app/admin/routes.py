from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.admin.forms import RegistrationAlunoForm, RegistrationMotoristaForm, RegistrationVeiculoForm, \
    RegistrationRotaForm, EditAlunoProfileForm, EditMotoristaProfileForm, EmptyForm, MessageForm, EditVeiculoForm, \
    EditRotaForm
from app.models import Usuario, Aluno, Motorista, Mensagem, Notificacao, Rota, Veiculo, Historico, Rotadia, Data
from app.admin import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    return render_template('admin/index.html', title='Administrador')


@bp.route('/cadastrar_aluno', methods=['GET', 'POST'])
def cadastrar_aluno():
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('main.index'))
    form = RegistrationAlunoForm()
    if form.validate_on_submit():
        rota = Rota.query.filter_by(nome_rota=form.rota.data).first_or_404()
        usuario = Usuario(nome=form.nome.data,
                          telefone=form.telefone.data,
                          email=form.email.data,
                          cpf=form.cpf.data)
        usuario.set_password(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        aluno = Aluno(curso=form.curso.data,
                      instituto=form.instituto.data,
                      periodo=form.periodo.data,
                      categoria=form.categoria.data,
                      usuario_id=usuario.id,
                      rota_id=rota.id)
        db.session.add(aluno)
        db.session.commit()
        flash('Aluno cadastrado!')
        return redirect(url_for('admin.index'))
    return render_template('admin/cadastrar.html', title='Cadastrar', form=form)


@bp.route('/cadastrar_motorista', methods=['GET', 'POST'])
def cadastrar_motorista():
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('main.index'))
    form = RegistrationMotoristaForm()
    if form.validate_on_submit():
        usuario = Usuario(nome=form.nome.data,
                          telefone=form.telefone.data,
                          email=form.email.data,
                          cpf=form.cpf.data,
                          is_admin=form.is_admin.data)
        usuario.set_password(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        motorista = Motorista(habilitacao=form.habilitacao.data,
                              usuario_id=usuario.id)
        db.session.add(motorista)
        db.session.commit()
        flash('Motorista cadastrado!')
        return redirect(url_for('admin.index'))
    return render_template('admin/cadastrar.html', title='Cadastrar',
                           form=form)


# @bp.route('/cadastrar_admin', methods=['GET', 'POST'])
def cadastrar_admin():
    form = RegistrationMotoristaForm()
    if form.validate_on_submit():
        usuario = Usuario(nome=form.nome.data,
                          telefone=form.telefone.data,
                          email=form.email.data,
                          cpf=form.cpf.data,
                          is_admin=form.is_admin.data)
        usuario.set_password(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        flash('admin cadastrado!')
        return redirect(url_for('admin.index'))
    return render_template('admin/cadastrar.html', title='Cadastrar',
                           form=form)


@bp.route('/cadastrar_veiculo', methods=['GET', 'POST'])
def cadastrar_veiculo():
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('main.index'))
    form = RegistrationVeiculoForm()
    if form.validate_on_submit():
        veiculo = Veiculo(modelo=form.modelo.data,
                          placa=form.placa.data,
                          tamanho=form.tamanho.data,
                          lugares=form.lugares.data)
        db.session.add(veiculo)
        db.session.commit()
        flash('Veiculo cadastrado!')
        return redirect(url_for('admin.index'))
    return render_template('admin/cadastrar.html', title='Cadastrar',
                           form=form)


@bp.route('/cadastrar_rota', methods=['GET', 'POST'])
def cadastrar_rota():
    if not current_user.is_authenticated or not current_user.is_admin:
        return redirect(url_for('main.index'))
    form = RegistrationRotaForm()
    if form.validate_on_submit():
        rota = Rota(nome_rota=form.nome_rota.data)
        db.session.add(rota)
        db.session.commit()
        flash('Rota cadastrada!')
        return redirect(url_for('admin.index'))
    return render_template('admin/cadastrar.html', title='Cadastrar',
                           form=form)


@bp.route('/usuario/<nome>')
@login_required
def usuario(nome):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    usuario = Usuario.query.filter_by(nome=nome).first_or_404()
    form = EmptyForm()
    return render_template('admin/usuario.html', usuario=usuario, form=form)


@bp.route('/usuario/<nome>/popup')
@login_required
def usuario_popup(nome):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    usuario = Usuario.query.filter_by(nome=nome).first_or_404()
    form = EmptyForm()
    return render_template('admin/usuario_popup.html', usuario=usuario, form=form)


@bp.route('/editar_perfil_aluno/<nome>', methods=['GET', 'POST'])
@login_required
def editar_perfil_aluno(nome):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    usuario = Usuario.query.filter_by(nome=nome).first_or_404()
    aluno = Aluno.query.filter_by(usuario_id=usuario.id).first()
    # rota = aluno.rota_id
    form = EditAlunoProfileForm(usuario)
    if form.validate_on_submit():
        usuario.nome = form.nome.data
        usuario.telefone = form.telefone.data
        usuario.email = form.email.data
        usuario.cpf = form.cpf.data
        aluno.curso = form.curso.data
        aluno.instituto = form.instituto.data
        aluno.periodo = form.periodo.data
        aluno.categoria = form.categoria.data
        aluno.rota_id = Rota.query.filter_by(nome_rota=form.rota.data).first_or_404().id
        db.session.commit()
        flash('Suas alterações foram salvas.')
        return redirect(url_for('admin.editar_perfil_aluno', nome=usuario.nome))
    elif request.method == 'GET':
        form.nome.data = usuario.nome
        form.telefone.data = usuario.telefone
        form.email.data = usuario.email
        form.cpf.data = usuario.cpf
        form.curso.data = aluno.curso
        form.instituto.data = aluno.instituto
        form.periodo.data = aluno.periodo
        form.categoria.data = aluno.categoria
        form.rota.data = aluno.rota_id
    return render_template('admin/editar_perfil.html', title='Editar Perfil',
                           form=form)


@bp.route('/editar_perfil_motorista/<nome>', methods=['GET', 'POST'])
@login_required
def editar_perfil_motorista(nome):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    usuario = Usuario.query.filter_by(nome=nome).first_or_404()
    motorista = Motorista.query.filter_by(usuario_id=usuario.id).first()
    form = EditMotoristaProfileForm(usuario)
    if form.validate_on_submit():
        usuario.nome = form.nome.data
        usuario.telefone = form.telefone.data
        usuario.email = form.email.data
        usuario.cpf = form.cpf.data
        motorista.habilitacao = form.habilitacao.data
        usuario.is_admin = form.is_admin.data
        db.session.commit()
        flash('Suas alterações foram salvas.')
        return redirect(url_for('admin.editar_perfil_motorista', nome=usuario.nome))
    elif request.method == 'GET':
        form.nome.data = usuario.nome
        form.telefone.data = usuario.telefone
        form.email.data = usuario.email
        form.cpf.data = usuario.cpf
        form.habilitacao.data = motorista.habilitacao
        form.is_admin.data = usuario.is_admin
    return render_template('admin/editar_perfil.html', title='Editar Perfil',
                           form=form)


@bp.route('/editar_veiculo/<id>', methods=['GET', 'POST'])
@login_required
def editar_veiculo(id):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    veiculo = Veiculo.query.filter_by(id=id).first_or_404()
    form = EditVeiculoForm()
    if form.validate_on_submit():
        veiculo.modelo = form.modelo.data
        veiculo.placa = form.placa.data
        veiculo.tamanho = form.tamanho.data
        veiculo.lugares = form.lugares.data
        db.session.commit()
        flash('Suas alterações foram salvas.')
        return redirect(url_for('admin.editar_veiculo', id=veiculo.id))
    elif request.method == 'GET':
        form.modelo.data = veiculo.modelo
        form.placa.data = veiculo.placa
        form.tamanho.data = veiculo.tamanho
        form.lugares.data = veiculo.lugares
    return render_template('admin/editar_perfil.html', title='Editar Perfil',
                           form=form)


@bp.route('/editar_rota/<nome_rota>', methods=['GET', 'POST'])
@login_required
def editar_rota(nome_rota):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    rota = Rota.query.filter_by(nome_rota=nome_rota).first_or_404()
    form = EditRotaForm()
    if form.validate_on_submit():
        rota.nome_rota = form.nome_rota.data
        db.session.commit()
        flash('Suas alterações foram salvas.')
        return redirect(url_for('admin.editar_rota', nome_rota=rota.nome_rota))
    elif request.method == 'GET':
        form.nome_rota.data = rota.nome_rota
    return render_template('admin/editar_perfil.html', title='Editar Perfil',
                           form=form)


@bp.route('/editar_motoristadia/<rota><motorista>', methods=['GET', 'POST'])
@login_required
def editar_motoristadia(rotadia, motorista):
    historico = Historico.query.order_by(Historico.data.desc()).all()
    motoristas = Motorista.query.all()
    veiculos = Veiculo.query.all()
    rotadia.motorista_id = Veiculo.query.filter_by(id=motorista).first_or_404()
    db.session.commit()
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    return render_template('admin/historico.html', title='Historico', historico=historico, motoristas=motoristas,
                           veiculos=veiculos)


@bp.route('/editar_veiculodia/<rota><veiculo>', methods=['GET', 'POST'])
@login_required
def editar_veiculodia(rota, veiculo):
    historico = Historico.query.order_by(Historico.data.desc()).all()
    motoristas = Motorista.query.all()
    veiculos = Veiculo.query.all()
    rotadia = Rotadia.query.filter_by(id=rota).first()
    rotadia.veiculo_id = veiculo
    db.session.commit()
    if not current_user.is_admin:
        return redirect(url_for('main.index'))

    return render_template('admin/historico.html', title='Historico', historico=historico, motoristas=motoristas,
                           veiculos=veiculos)


@bp.route('/mandar_mensagem/<destinatario>', methods=['GET', 'POST'])
@login_required
def mandar_mensagem(destinatario):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    usuario = Usuario.query.filter_by(nome=destinatario).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Mensagem(remetente=current_user, destinatario=usuario,
                       corpo=form.mensagem.data)
        db.session.add(msg)
        usuario.add_notificacao('unread_message_count', usuario.novas_mensagens())
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('admin.index'))
    return render_template('admin/mandar_mensagem.html', title='Mandar Mensagem',
                           form=form, destinatario=destinatario)


@bp.route('/mensagens')
@login_required
def mensagens():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    current_user.ultima_vez_lido_mensagem = datetime.utcnow()
    current_user.add_notificacao('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    mensagens = current_user.mensagens_recebidas.order_by(
        Mensagem.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('admin.mensagens', page=mensagens.next_num) \
        if mensagens.has_next else None
    prev_url = url_for('admin.mensagens', page=mensagens.prev_num) \
        if mensagens.has_prev else None
    return render_template('admin/mensagem.html', mensagens=mensagens.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/notificacoes')
@login_required
def notificacoes():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    since = request.args.get('since', 0.0, type=float)
    notificacoes = current_user.notificacoes.filter(
        Notificacao.timestamp > since).order_by(Notificacao.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notificacoes])


@bp.route('/log_alunos')
@login_required
def log_alunos():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    alunos = Aluno.query.all()
    return render_template('admin/log_alunos.html', title='Log de Alunos', alunos=alunos)


@bp.route('/log_motoristas')
@login_required
def log_motoristas():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    motoristas = Motorista.query.all()
    return render_template('admin/log_motoristas.html', title='Log de Motoristas', motoristas=motoristas)


@bp.route('/log_veiculos')
@login_required
def log_veiculos():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    veiculos = Veiculo.query.all()
    return render_template('admin/log_veiculos.html', title='Log de Veiculos', veiculos=veiculos)


@bp.route('/log_rotas')
@login_required
def log_rotas():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    rotas = Rota.query.all()
    return render_template('admin/log_rotas.html', title='Log de Rotas', rotas=rotas)


@bp.route('/historico')
@login_required
def historico():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    historico = Historico.query.order_by(Historico.data.desc()).all()
    motoristas = Motorista.query.all()
    veiculos = Veiculo.query.all()
    return render_template('admin/historico.html', title='Historico', historico=historico, motoristas=motoristas,
                           veiculos=veiculos)


@bp.route('/historico/<data>')
@login_required
def historico_data(data):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))


@bp.route('/excluir/<id>')
@login_required
def excluir(id):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    if Usuario.query.get(id).aluno:
        url = 'admin.log_alunos'
    else:
        url = 'admin.log_motoristas'
    db.session.delete(Usuario.query.get(id))
    db.session.commit()
    return redirect(url_for(url))


@bp.route('/excluir_veiculo/<id>')
@login_required
def excluir_veiculo(id):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    db.session.delete(Veiculo.query.get(id))
    db.session.commit()
    return redirect(url_for('admin.log_veiculos'))


@bp.route('/excluir_rota/<id>')
@login_required
def excluir_rota(id):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    db.session.delete(Rota.query.get(id))
    db.session.commit()
    return redirect(url_for('admin.log_rotas'))


@bp.route('/popular')
def popular():
    for i in range(50):
        usuario = Usuario(nome="usuario"+str(i),
                          telefone=49153456541+i,
                          email="teste"+str(i)+'@teste.com',
                          cpf=98385274111+i)
        usuario.set_password("teste")
        db.session.add(usuario)
        db.session.commit()
        if i % 2 == 0:
            aluno = Aluno(curso="Farmacia",
                          instituto="UNOESC",
                          periodo="noturno",
                          categoria="Mensalista",
                          usuario_id=usuario.id,
                          rota_id=Rota.query.filter_by(nome_rota="Videira").first_or_404().id)
        elif i % 3 == 0:
            aluno = Aluno(curso="Computacao",
                          instituto="UNOESC",
                          periodo="noturno",
                          categoria="Diarista",
                          usuario_id=usuario.id,
                          rota_id=Rota.query.filter_by(nome_rota="Videira").first_or_404().id)
        else:
            aluno = Aluno(curso="Direito",
                          instituto="UNOESC",
                          periodo="diurno",
                          categoria="mensalista",
                          usuario_id=usuario.id,
                          rota_id=Rota.query.filter_by(nome_rota="Joacaba").first_or_404().id)
        db.session.add(aluno)
        db.session.commit()

    return redirect(url_for('admin.log_alunos'))
