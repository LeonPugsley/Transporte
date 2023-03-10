from app import create_app, db
from app.models import Usuario, Aluno, Motorista, Rota, Veiculo, Mensagem, Notificacao, Historico, Rotadia, Data

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Usuario': Usuario, 'Aluno': Aluno, 'Motorista': Motorista, 'Rota': Rota, 'Veiculo': Veiculo,
            'Mensagem': Mensagem, 'Notificação': Notificacao, 'Historico': Historico, 'Rotadia': Rotadia, 'Data': Data}
