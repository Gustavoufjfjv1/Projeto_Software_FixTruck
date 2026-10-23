"""Seed idempotente do FixTruck: pode ser executado quantas vezes quiser sem duplicar dados.

Uso (na pasta backend):  python seed.py
"""
import json
import os
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash

import seed_dados
from horarios import agora_sao_paulo, normalizar_horarios


def _formatar(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None


def popular_oficinas(conn):
    inseridas = 0
    for of in seed_dados.OFICINAS:
        horarios = json.dumps(normalizar_horarios(of['horarios'])) if of['horarios'] else None
        existente = conn.execute(
            'SELECT id FROM oficinas WHERE nome=? AND endereco=?', (of['nome'], of['endereco'])
        ).fetchone()
        if existente:
            # Não sobrescreve dados já existentes; só completa campos vazios.
            conn.execute(
                """UPDATE oficinas SET
                       cidade = COALESCE(cidade, ?),
                       uf = COALESCE(uf, ?),
                       horarios = CASE WHEN horarios IS NULL AND aberta_24h = 0 THEN ? ELSE horarios END
                   WHERE id = ?""",
                (of['cidade'], of['uf'], horarios, existente[0]),
            )
            continue
        conn.execute(
            """INSERT INTO oficinas (nome, endereco, cidade, uf, telefone, lat, lon, especialidades,
                   tipos_veiculo, tem_guincho, aberta_24h, horarios, ativa)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)""",
            (
                of['nome'], of['endereco'], of['cidade'], of['uf'], of['telefone'], of['lat'], of['lon'],
                ','.join(of['especialidades']), ','.join(of['tipos_veiculo']),
                of['tem_guincho'], of['aberta_24h'], horarios,
            ),
        )
        inseridas += 1
    return inseridas


def popular_demo(conn):
    dados = seed_dados.EMPRESA_DEMO
    row = conn.execute('SELECT id FROM empresas WHERE email=?', (dados['email'],)).fetchone()
    if row:
        empresa_id = row[0]
    else:
        empresa_id = conn.execute(
            'INSERT INTO empresas (nome, email, senha, qtd_caminhoes) VALUES (?,?,?,?)',
            (dados['nome'], dados['email'], generate_password_hash(dados['senha']), dados['qtd_caminhoes']),
        ).lastrowid

    motorista_ids = []
    for m in seed_dados.MOTORISTAS_DEMO:
        row = conn.execute(
            'SELECT id FROM motoristas WHERE empresa_id=? AND cnh=? ORDER BY id LIMIT 1',
            (empresa_id, m['cnh']),
        ).fetchone()
        if row:
            motorista_id = row[0]
        else:
            motorista_id = conn.execute(
                'INSERT INTO motoristas (empresa_id, nome, cnh, telefone, ativo) VALUES (?,?,?,?,1)',
                (empresa_id, m['nome'], m['cnh'], m['telefone']),
            ).lastrowid
        motorista_ids.append(motorista_id)
        email_livre = m.get('email') and not conn.execute(
            'SELECT 1 FROM motoristas WHERE email=?', (m['email'],)
        ).fetchone()
        if email_livre:
            # Só cria a credencial demo se o motorista ainda não tiver acesso definido.
            conn.execute(
                'UPDATE motoristas SET email=?, senha=?, trocar_senha=? WHERE id=? AND email IS NULL',
                (m['email'], generate_password_hash(m['senha']), m['trocar_senha'], motorista_id),
            )

    veiculo_ids = []
    for v in seed_dados.VEICULOS_DEMO:
        row = conn.execute('SELECT id, empresa_id FROM veiculos WHERE placa=?', (v['placa'],)).fetchone()
        if row:
            # Placa é única no sistema: se outra empresa já a usa, o veículo demo não é criado.
            veiculo_ids.append(row[0] if row[1] == empresa_id else None)
            continue
        motorista_id = motorista_ids[v['motorista']] if v['motorista'] is not None else None
        veiculo_ids.append(conn.execute(
            """INSERT INTO veiculos (empresa_id, placa, modelo, marca, tipo_veiculo, motorista_id)
               VALUES (?,?,?,?,?,?)""",
            (empresa_id, v['placa'], v['modelo'], v['marca'], v['tipo_veiculo'], motorista_id),
        ).lastrowid)

    ja_tem = conn.execute('SELECT COUNT(*) FROM ocorrencias WHERE empresa_id=?', (empresa_id,)).fetchone()[0]
    if ja_tem:
        return empresa_id

    agora = agora_sao_paulo().replace(tzinfo=None, microsecond=0)
    for oc in seed_dados.OCORRENCIAS_DEMO:
        veiculo = seed_dados.VEICULOS_DEMO[oc['veiculo']]
        abertura = agora - timedelta(days=oc['dias_atras'])
        vinculacao = abertura + timedelta(hours=oc['horas_ate_oficina']) if oc['horas_ate_oficina'] else None
        fim = abertura + timedelta(hours=oc['horas_ate_fim']) if oc['horas_ate_fim'] else None
        oficina_id = None
        if oc['oficina']:
            row = conn.execute('SELECT id FROM oficinas WHERE nome=?', (oc['oficina'],)).fetchone()
            oficina_id = row[0] if row else None
        motorista_id = motorista_ids[veiculo['motorista']] if veiculo['motorista'] is not None else None
        conn.execute(
            """INSERT INTO ocorrencias (empresa_id, motorista_id, veiculo_id, tipo_veiculo, tipo_problema,
                   pane_total, descricao, lat, lon, endereco, status, oficina_id, motivo_resolucao,
                   data_abertura, data_vinculacao, data_encerramento, registrada_por)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                empresa_id, motorista_id, veiculo_ids[oc['veiculo']], veiculo['tipo_veiculo'],
                oc['tipo_problema'], oc['pane_total'], oc.get('descricao'), oc['lat'], oc['lon'],
                oc['endereco'], oc['status'], oficina_id,
                'Problema resolvido na oficina' if oc['status'] == 'resolvido' else None,
                _formatar(abertura), _formatar(vinculacao), _formatar(fim), oc.get('registrada_por', 'empresa'),
            ),
        )
    return empresa_id


def popular(conn):
    inseridas = popular_oficinas(conn)
    popular_demo(conn)
    conn.commit()
    return inseridas


if __name__ == '__main__':
    from app import create_app
    from database import init_db

    app = create_app()
    with app.app_context():
        resumo = init_db()
    print(f"Banco: {resumo['caminho']}")
    if resumo['tabelas_migradas']:
        print(f"Tabelas migradas para o schema oficial: {', '.join(resumo['tabelas_migradas'])}")
        print(f"Backup do banco anterior: {resumo['backup']}")
    print(f"Oficinas inseridas nesta execução: {resumo['oficinas_inseridas']}")
    print(f"Oficinas ativas no banco: {resumo['oficinas_ativas']}")
