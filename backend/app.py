import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, g, request, send_from_directory
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from database import db, init_db, DATABASE_PATH
from controllers import registrar_blueprints

_MENSAGENS_UNIQUE = {
    'veiculos.placa': 'Esta placa já está cadastrada no sistema.',
    'empresas.email': 'Este e-mail já está cadastrado.',
    'motoristas.email': 'Este e-mail já é usado por outro motorista.',
    'favoritos.empresa_id': 'Esta oficina já está nos favoritos.',
}


def mensagem_integridade(texto):
    """Traduz erros de integridade do SQLite em respostas amigáveis (nunca 500)."""
    if 'UNIQUE constraint failed' in texto:
        for coluna, mensagem in _MENSAGENS_UNIQUE.items():
            if coluna in texto:
                return mensagem, 409
        return 'Registro duplicado.', 409
    if 'FOREIGN KEY constraint failed' in texto:
        return 'Registro relacionado não existe ou ainda está em uso.', 422
    if 'CHECK constraint failed' in texto:
        return 'Valor fora das opções permitidas.', 422
    if 'NOT NULL constraint failed' in texto:
        return 'Campo obrigatório não informado.', 422
    return 'Dados inválidos.', 422


def create_app(config=None):
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend'),
        static_url_path='',
    )
    app.secret_key = os.environ.get('FIXTRUCK_SECRET', 'fixtruck-secret-2024')
    app.config['DATABASE_PATH'] = DATABASE_PATH
    if config:
        app.config.update(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.config['DATABASE_PATH']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        return response

    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            return ('', 204)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
        sqlite_db = g.pop('sqlite_db', None)
        if sqlite_db is not None:
            sqlite_db.close()

    @app.errorhandler(IntegrityError)
    @app.errorhandler(sqlite3.IntegrityError)
    def erro_integridade(erro):
        db.session.rollback()
        mensagem, status = mensagem_integridade(str(getattr(erro, 'orig', erro)))
        return jsonify({'erro': mensagem}), status

    @app.errorhandler(404)
    def nao_encontrado(erro):
        if request.path.startswith('/api/'):
            return jsonify({'erro': 'Recurso não encontrado.'}), 404
        return erro

    @app.errorhandler(405)
    def metodo_nao_permitido(_erro):
        return jsonify({'erro': 'Método não permitido.'}), 405

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        if isinstance(erro, HTTPException):
            return erro
        db.session.rollback()
        app.logger.exception('Erro inesperado')
        return jsonify({'erro': 'Erro interno. Tente novamente.'}), 500

    @app.get('/api/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'fixtruck-api'})

    registrar_blueprints(app)

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    return app


app = create_app()


if __name__ == '__main__':
    with app.app_context():
        resumo = init_db()
        print(f"Banco pronto em {resumo['caminho']} — {resumo['oficinas_ativas']} oficinas ativas.")
    app.run(debug=True, port=5000)
