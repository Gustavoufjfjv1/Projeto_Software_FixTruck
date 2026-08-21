import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'fixtruck.db')
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

db = SQLAlchemy()


def _ensure_column(table, column, definition):
    """Adiciona uma coluna em bancos já existentes (db.create_all() não altera tabelas)."""
    inspector = inspect(db.engine)
    colunas = [c['name'] for c in inspector.get_columns(table)]
    if column not in colunas:
        with db.engine.begin() as conn:
            conn.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {definition}'))


def init_db(app=None):
    """Cria tabelas e popula dados demo se necessário."""
    from models import Empresa, Motorista, Veiculo, Oficina, Ocorrencia  # noqa: F401

    db.create_all()
    _ensure_column('ocorrencias', 'data_vinculacao', 'TEXT')

    if Oficina.query.count() == 0:
        oficinas = [
            Oficina(nome='Auto Mecânica Silva', endereco='Av. Paulista, 1000 - SP',
                    telefone='(11) 99001-1111', lat=-23.5613, lon=-46.6558,
                    especialidades='mecânica,elétrica', tipos_veiculo='leve,médio,pesado',
                    tem_guincho=1, hora_abertura='07:00', hora_fechamento='18:00'),
            Oficina(nome='Borracharia Rápida BR', endereco='Rod. Anhanguera KM 45',
                    telefone='(11) 98002-2222', lat=-23.5200, lon=-46.6300,
                    especialidades='borracharia', tipos_veiculo='leve,médio,pesado',
                    tem_guincho=1, hora_abertura='06:00', hora_fechamento='22:00'),
            Oficina(nome='Elétrica Diesel Master', endereco='Av. dos Caminhoneiros, 500',
                    telefone='(11) 97003-3333', lat=-23.5900, lon=-46.6100,
                    especialidades='elétrica,mecânica', tipos_veiculo='médio,pesado',
                    tem_guincho=0, hora_abertura='08:00', hora_fechamento='17:00'),
            Oficina(nome='Hidráulica & Freios SP', endereco='Rua das Indústrias, 200',
                    telefone='(11) 96004-4444', lat=-23.5500, lon=-46.6800,
                    especialidades='hidráulica,freios', tipos_veiculo='pesado',
                    tem_guincho=1, hora_abertura='08:00', hora_fechamento='18:00'),
            Oficina(nome='Oficina do Zé Mecânico', endereco='Estrada Velha, KM 12',
                    telefone='(11) 95005-5555', lat=-23.5750, lon=-46.6400,
                    especialidades='mecânica', tipos_veiculo='leve,médio',
                    tem_guincho=0, hora_abertura='08:00', hora_fechamento='17:00'),
            Oficina(nome='Truck Center Premium', endereco='Av. Industrial, 1500',
                    telefone='(11) 94006-6666', lat=-23.5450, lon=-46.6650,
                    especialidades='mecânica,elétrica,hidráulica,borracharia',
                    tipos_veiculo='leve,médio,pesado', tem_guincho=1,
                    hora_abertura='00:00', hora_fechamento='23:59'),
            Oficina(nome='Mecânica Rodo Sul', endereco='Rod. Castelo Branco KM 30',
                    telefone='(11) 93007-7777', lat=-23.6000, lon=-46.6200,
                    especialidades='mecânica,elétrica', tipos_veiculo='pesado',
                    tem_guincho=1, hora_abertura='07:00', hora_fechamento='19:00'),
            Oficina(nome='Auto Peças & Serviços', endereco='Rua das Oficinas, 88',
                    telefone='(11) 92008-8888', lat=-23.5350, lon=-46.6900,
                    especialidades='mecânica,borracharia', tipos_veiculo='leve,médio',
                    tem_guincho=0, hora_abertura='08:00', hora_fechamento='18:00'),
        ]
        for of in oficinas:
            db.session.add(of)

        empresa = Empresa.query.filter_by(email='demo@fixtruck.com').first()
        if not empresa:
            empresa = Empresa(
                nome='Transportadora Demo',
                email='demo@fixtruck.com',
                senha=generate_password_hash('123456'),
                qtd_caminhoes=12,
            )
            db.session.add(empresa)
            db.session.flush()

        if Motorista.query.filter_by(empresa_id=empresa.id).count() == 0:
            motoristas = [
                Motorista(empresa_id=empresa.id, nome='Carlos Mendes',
                          cnh='12345678901', telefone='(11) 99111-1111'),
                Motorista(empresa_id=empresa.id, nome='José Ferreira',
                          cnh='98765432100', telefone='(11) 99222-2222'),
                Motorista(empresa_id=empresa.id, nome='Ana Paula Souza',
                          cnh='45678912300', telefone='(11) 99333-3333'),
            ]
            for m in motoristas:
                db.session.add(m)
            db.session.flush()

            mids = [m.id for m in Motorista.query.filter_by(empresa_id=empresa.id).order_by(Motorista.id).all()]
            veiculos = [
                Veiculo(empresa_id=empresa.id, placa='ABC1D23', modelo='Actros 2651',
                        marca='Mercedes', tipo_veiculo='pesado', motorista_id=mids[0]),
                Veiculo(empresa_id=empresa.id, placa='DEF4G56', modelo='FH 540',
                        marca='Volvo', tipo_veiculo='pesado', motorista_id=mids[1]),
                Veiculo(empresa_id=empresa.id, placa='GHI7J89', modelo='Delivery 9.170',
                        marca='VW', tipo_veiculo='médio', motorista_id=mids[2]),
                Veiculo(empresa_id=empresa.id, placa='JKL0M12', modelo='Daily 35S14',
                        marca='Iveco', tipo_veiculo='leve', motorista_id=None),
            ]
            for v in veiculos:
                db.session.add(v)
            db.session.flush()

            vids = [v.id for v in Veiculo.query.filter_by(empresa_id=empresa.id).order_by(Veiculo.id).all()]
            ocorrencias = [
                Ocorrencia(
                    empresa_id=empresa.id, motorista_id=mids[0], veiculo_id=vids[0],
                    tipo_veiculo='pesado', tipo_problema='mecânica', pane_total=1,
                    lat='-23.5613', lon='-46.6558', endereco='Rodovia Anhanguera KM 45',
                    status='resolvido', oficina_id=1,
                    data_abertura='2024-05-01 09:00', data_encerramento='2024-05-01 13:30',
                ),
                Ocorrencia(
                    empresa_id=empresa.id, motorista_id=mids[1], veiculo_id=vids[1],
                    tipo_veiculo='pesado', tipo_problema='borracharia', pane_total=0,
                    lat='-23.5200', lon='-46.6300', endereco='Av. Brasil, 500',
                    status='resolvido', oficina_id=2,
                    data_abertura='2024-05-10 14:00', data_encerramento='2024-05-10 15:45',
                ),
                Ocorrencia(
                    empresa_id=empresa.id, motorista_id=mids[2], veiculo_id=vids[2],
                    tipo_veiculo='médio', tipo_problema='elétrica', pane_total=0,
                    lat='-23.5900', lon='-46.6100', endereco='Rod. Dutra KM 180',
                    status='em_atendimento', oficina_id=None,
                    data_abertura='2024-05-20 08:30', data_encerramento=None,
                ),
                Ocorrencia(
                    empresa_id=empresa.id, motorista_id=mids[0], veiculo_id=vids[0],
                    tipo_veiculo='pesado', tipo_problema='mecânica', pane_total=0,
                    lat='-23.5500', lon='-46.6800', endereco='Centro, São Paulo',
                    status='aberta', oficina_id=None,
                    data_abertura='2024-05-22 07:15', data_encerramento=None,
                ),
            ]
            for oc in ocorrencias:
                db.session.add(oc)

        db.session.commit()

    # Garante frota demo em bancos antigos
    empresa = Empresa.query.filter_by(email='demo@fixtruck.com').first()
    if empresa:
        if Motorista.query.filter_by(empresa_id=empresa.id).count() == 0:
            for dados in [
                ('Carlos Mendes', '12345678901', '(11) 99111-1111'),
                ('José Ferreira', '98765432100', '(11) 99222-2222'),
                ('Ana Paula Souza', '45678912300', '(11) 99333-3333'),
            ]:
                db.session.add(Motorista(
                    empresa_id=empresa.id, nome=dados[0], cnh=dados[1], telefone=dados[2]
                ))
            db.session.commit()

        if Veiculo.query.filter_by(empresa_id=empresa.id).count() == 0:
            mids = [m.id for m in Motorista.query.filter_by(empresa_id=empresa.id).order_by(Motorista.id).all()]
            for dados in [
                ('ABC1D23', 'Actros 2651', 'Mercedes', 'pesado', mids[0] if mids else None),
                ('DEF4G56', 'FH 540', 'Volvo', 'pesado', mids[1] if len(mids) > 1 else None),
                ('GHI7J89', 'Delivery 9.170', 'VW', 'médio', mids[2] if len(mids) > 2 else None),
                ('JKL0M12', 'Daily 35S14', 'Iveco', 'leve', None),
            ]:
                db.session.add(Veiculo(
                    empresa_id=empresa.id, placa=dados[0], modelo=dados[1],
                    marca=dados[2], tipo_veiculo=dados[3], motorista_id=dados[4],
                ))
            db.session.commit()

    # Migra senhas antigas em texto puro para hash (upgrade de bancos criados antes do hashing)
    for empresa in Empresa.query.all():
        if empresa.senha and not empresa.senha.startswith(('pbkdf2:', 'scrypt:')):
            empresa.senha = generate_password_hash(empresa.senha)
    db.session.commit()
