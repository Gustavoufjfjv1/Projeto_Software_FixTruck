"""Migração segura do banco SQLite para o schema do script oficial.

Estratégia (recomendada pela documentação do SQLite para alterações de schema):
1. Executa o script oficial (CREATE TABLE IF NOT EXISTS) — cria o que faltar.
2. Para cada tabela cujo CREATE armazenado diverge do script, cria a tabela nova,
   copia as colunas em comum (aplicando defaults/normalizações), apaga a antiga e
   renomeia a nova. Nenhuma linha é descartada; se a cópia falhar, tudo é desfeito.
3. Antes de qualquer reconstrução, faz uma cópia do arquivo (fixtruck.db.bak-AAAAMMDDHHMMSS).
"""
import os
import re
import shutil
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'create_database.sql')

_RE_TABELA = re.compile(r'CREATE TABLE IF NOT EXISTS (\w+) \((.*?)\n\);', re.DOTALL)

# Expressões SQL usadas ao copiar uma coluna da tabela antiga (placeholder {col}).
TRANSFORMACOES = {}


def ler_script():
    with open(SCRIPT_PATH, encoding='utf-8') as f:
        return f.read()


def tabelas_do_script(script=None):
    script = script or ler_script()
    tabelas = {}
    for m in _RE_TABELA.finditer(script):
        tabelas[m.group(1)] = m.group(0).rstrip(';')
    return tabelas


def normalizar_sql(sql):
    sql = re.sub(r'--[^\n]*', '', sql or '')
    sql = sql.replace('IF NOT EXISTS ', '').replace('"', '')
    sql = re.sub(r'\s+', ' ', sql).strip().rstrip(';').lower()
    sql = re.sub(r'\s*([(),])\s*', r'\1', sql)
    return sql


def _colunas(conn, tabela):
    return {
        r[1]: {'notnull': bool(r[3]), 'default': r[4]}
        for r in conn.execute(f'PRAGMA table_info({tabela})').fetchall()
    }


def _reconstruir(conn, tabela, create_sql):
    antigas = _colunas(conn, tabela)
    temporaria = f'{tabela}__novo'
    conn.execute(create_sql.replace(
        f'CREATE TABLE IF NOT EXISTS {tabela} (', f'CREATE TABLE {temporaria} (', 1
    ))
    novas = _colunas(conn, temporaria)
    destino, origem = [], []
    for col, info in novas.items():
        if col not in antigas:
            continue
        expr = TRANSFORMACOES.get(tabela, {}).get(col, '{col}').format(col=col)
        if info['notnull'] and info['default'] is not None:
            expr = f'COALESCE({expr}, {info["default"]})'
        destino.append(col)
        origem.append(expr)
    conn.execute(
        f'INSERT INTO {temporaria} ({", ".join(destino)}) '
        f'SELECT {", ".join(origem)} FROM {tabela}'
    )
    conn.execute(f'DROP TABLE {tabela}')
    conn.execute(f'ALTER TABLE {temporaria} RENAME TO {tabela}')


def _horarios_legados(conn):
    """Lê hora_abertura/hora_fechamento do schema antigo antes da reconstrução."""
    cols = _colunas(conn, 'oficinas') if _existe(conn, 'oficinas') else {}
    if 'hora_abertura' not in cols or 'horarios' in cols:
        return []
    return conn.execute('SELECT id, hora_abertura, hora_fechamento FROM oficinas').fetchall()


def _existe(conn, tabela):
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tabela,)
    ).fetchone() is not None


def _aplicar_horarios_legados(conn, legados):
    from horarios import horarios_uniformes, normalizar_horarios
    import json
    for oficina_id, abertura, fechamento in legados:
        abertura = (abertura or '08:00')[:5]
        fechamento = (fechamento or '18:00')[:5]
        if abertura == fechamento or (abertura == '00:00' and fechamento in ('23:59', '24:00')):
            conn.execute('UPDATE oficinas SET aberta_24h=1 WHERE id=?', (oficina_id,))
            continue
        try:
            horarios = normalizar_horarios(horarios_uniformes(abertura, fechamento))
        except ValueError:
            continue
        conn.execute(
            'UPDATE oficinas SET horarios=? WHERE id=? AND horarios IS NULL',
            (json.dumps(horarios), oficina_id),
        )


def _ajustes_de_dados(conn):
    conn.execute("UPDATE ocorrencias SET status='resolvido' WHERE status='encerrada'")
    for empresa_id, senha in conn.execute('SELECT id, senha FROM empresas').fetchall():
        senha = senha or ''
        if not (senha.startswith('pbkdf2:') or senha.startswith('scrypt:')):
            conn.execute(
                'UPDATE empresas SET senha=? WHERE id=?', (generate_password_hash(senha), empresa_id)
            )


def _backup(caminho_banco):
    if not caminho_banco or not os.path.exists(caminho_banco) or os.path.getsize(caminho_banco) == 0:
        return None
    destino = f'{caminho_banco}.bak-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    shutil.copy2(caminho_banco, destino)
    return destino


def aplicar(conn, caminho_banco=None):
    """Deixa o banco idêntico ao script oficial. Retorna (tabelas_reconstruidas, arquivo_backup)."""
    esperadas = tabelas_do_script()
    existentes = {
        nome: sql for nome, sql in conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    divergentes = [
        t for t in esperadas
        if t in existentes and normalizar_sql(existentes[t]) != normalizar_sql(esperadas[t])
    ]
    backup = _backup(caminho_banco) if divergentes else None
    legados = _horarios_legados(conn)

    conn.commit()
    conn.execute('PRAGMA foreign_keys = OFF')
    try:
        conn.execute('BEGIN')
        for tabela in divergentes:
            _reconstruir(conn, tabela, esperadas[tabela])
        for tabela, create_sql in esperadas.items():
            conn.execute(create_sql)
        _aplicar_horarios_legados(conn, legados)
        _ajustes_de_dados(conn)
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.execute('PRAGMA foreign_keys = ON')
    return divergentes, backup
