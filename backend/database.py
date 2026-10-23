import os
import sqlite3
from flask import g, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

DATABASE_PATH = os.environ.get(
    'FIXTRUCK_DB', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtruck.db')
)

db = SQLAlchemy()


@event.listens_for(Engine, 'connect')
def _ativar_foreign_keys(conexao, _registro):
    # No SQLite as FKs vêm desligadas por padrão em cada conexão.
    if isinstance(conexao, sqlite3.Connection):
        cursor = conexao.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.close()


def caminho_banco():
    return current_app.config.get('DATABASE_PATH', DATABASE_PATH)


def conectar(caminho=None):
    conn = sqlite3.connect(caminho or caminho_banco())
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def get_db():
    """Conexão sqlite3 para consultas SQL puro nos Repositories."""
    if 'sqlite_db' not in g:
        g.sqlite_db = conectar()
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


def init_db(popular=True):
    """Cria/migra o schema a partir do script oficial e roda o seed idempotente."""
    import migracoes
    import seed

    caminho = caminho_banco()
    conn = conectar(caminho)
    try:
        tabelas_migradas, backup = migracoes.aplicar(conn, caminho)
        inseridas = seed.popular(conn) if popular else 0
        ativas = conn.execute('SELECT COUNT(*) FROM oficinas WHERE ativa = 1').fetchone()[0]
    finally:
        conn.close()
    return {
        'caminho': caminho,
        'tabelas_migradas': tabelas_migradas,
        'backup': backup,
        'oficinas_inseridas': inseridas,
        'oficinas_ativas': ativas,
    }
