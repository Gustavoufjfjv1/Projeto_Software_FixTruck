import os
import sqlite3
from flask import g, current_app
from flask_sqlalchemy import SQLAlchemy

DATABASE_PATH = os.environ.get(
    'FIXTRUCK_DB', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtruck.db')
)

db = SQLAlchemy()


def caminho_banco():
    return current_app.config.get('DATABASE_PATH', DATABASE_PATH)


def get_db():
    """Conexão sqlite3 para consultas SQL puro nos Repositories."""
    if 'sqlite_db' not in g:
        g.sqlite_db = sqlite3.connect(caminho_banco())
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


def init_db(popular=True):
    """Cria/migra o schema a partir do script oficial e roda o seed idempotente."""
    import migracoes
    import seed

    caminho = caminho_banco()
    conn = sqlite3.connect(caminho)
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
