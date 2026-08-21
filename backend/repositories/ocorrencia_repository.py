from sqlalchemy import func
from database import db
from models import Ocorrencia, Oficina, Veiculo, Motorista


def _filtro_periodo(query, periodo):
    if periodo == '7d':
        return query.filter(Ocorrencia.data_abertura >= func.datetime('now', '-7 days'))
    if periodo == '30d':
        return query.filter(Ocorrencia.data_abertura >= func.datetime('now', '-30 days'))
    if periodo == '90d':
        return query.filter(Ocorrencia.data_abertura >= func.datetime('now', '-90 days'))
    return query


class OcorrenciaRepository:
    """Consultas complexas de ocorrências (filtros, joins, agregações)."""

    @staticmethod
    def listar_por_empresa(empresa_id, filtros=None):
        filtros = filtros or {}
        query = (
            db.session.query(
                Ocorrencia,
                Oficina.nome.label('oficina_nome'),
                Veiculo.placa.label('veiculo_placa'),
                Motorista.nome.label('motorista_nome'),
            )
            .outerjoin(Oficina, Ocorrencia.oficina_id == Oficina.id)
            .outerjoin(Veiculo, Ocorrencia.veiculo_id == Veiculo.id)
            .outerjoin(Motorista, Ocorrencia.motorista_id == Motorista.id)
            .filter(Ocorrencia.empresa_id == empresa_id)
        )

        if filtros.get('tipo'):
            query = query.filter(Ocorrencia.tipo_problema == filtros['tipo'])
        if filtros.get('veiculo'):
            query = query.filter(Ocorrencia.veiculo_id == filtros['veiculo'])

        status = filtros.get('status', '')
        if status == 'abertas':
            query = query.filter(Ocorrencia.status.in_(['aberta', 'em_atendimento']))
        elif status:
            query = query.filter(Ocorrencia.status == status)

        query = _filtro_periodo(query, filtros.get('periodo', ''))

        rows = query.order_by(Ocorrencia.data_abertura.desc()).all()
        resultado = []
        for oc, oficina_nome, veiculo_placa, motorista_nome in rows:
            resultado.append(oc.to_dict({
                'oficina_nome': oficina_nome,
                'veiculo_placa': veiculo_placa,
                'motorista_nome': motorista_nome,
            }))
        return resultado

    @staticmethod
    def buscar_detalhe(ocorrencia_id, empresa_id):
        row = (
            db.session.query(
                Ocorrencia,
                Oficina.nome.label('oficina_nome'),
                Veiculo.placa.label('veiculo_placa'),
                Veiculo.modelo.label('veiculo_modelo'),
                Motorista.nome.label('motorista_nome'),
            )
            .outerjoin(Oficina, Ocorrencia.oficina_id == Oficina.id)
            .outerjoin(Veiculo, Ocorrencia.veiculo_id == Veiculo.id)
            .outerjoin(Motorista, Ocorrencia.motorista_id == Motorista.id)
            .filter(Ocorrencia.id == ocorrencia_id, Ocorrencia.empresa_id == empresa_id)
            .first()
        )
        if not row:
            return None
        oc, oficina_nome, veiculo_placa, veiculo_modelo, motorista_nome = row
        return oc.to_dict({
            'oficina_nome': oficina_nome,
            'veiculo_placa': veiculo_placa,
            'veiculo_modelo': veiculo_modelo,
            'motorista_nome': motorista_nome,
        })

    @staticmethod
    def buscar_da_empresa(ocorrencia_id, empresa_id):
        return Ocorrencia.query.filter_by(id=ocorrencia_id, empresa_id=empresa_id).first()

    @staticmethod
    def contar_abertas(empresa_id):
        return Ocorrencia.query.filter(
            Ocorrencia.empresa_id == empresa_id,
            Ocorrencia.status.in_(['aberta', 'em_atendimento']),
        ).count()

    @staticmethod
    def contar_total(empresa_id, periodo=''):
        query = Ocorrencia.query.filter_by(empresa_id=empresa_id)
        return _filtro_periodo(query, periodo).count()

    @staticmethod
    def contar_por_status(empresa_id, status, periodo=''):
        query = Ocorrencia.query.filter_by(empresa_id=empresa_id, status=status)
        return _filtro_periodo(query, periodo).count()

    @staticmethod
    def contar_veiculos_atendidos(empresa_id):
        return db.session.query(func.count(func.distinct(Ocorrencia.veiculo_id))).filter(
            Ocorrencia.empresa_id == empresa_id,
            Ocorrencia.veiculo_id.isnot(None),
        ).scalar()

    @staticmethod
    def tempo_medio_resolucao(empresa_id, periodo=''):
        query = db.session.query(
            func.avg(
                (func.julianday(Ocorrencia.data_encerramento) - func.julianday(Ocorrencia.data_abertura))
                * 24 * 60
            )
        ).filter(
            Ocorrencia.empresa_id == empresa_id,
            Ocorrencia.status == 'resolvido',
            Ocorrencia.data_encerramento.isnot(None),
        )
        return _filtro_periodo(query, periodo).scalar()

    @staticmethod
    def tempo_medio_ate_oficina(empresa_id, periodo=''):
        query = db.session.query(
            func.avg(
                (func.julianday(Ocorrencia.data_vinculacao) - func.julianday(Ocorrencia.data_abertura))
                * 24 * 60
            )
        ).filter(
            Ocorrencia.empresa_id == empresa_id,
            Ocorrencia.data_vinculacao.isnot(None),
        )
        return _filtro_periodo(query, periodo).scalar()

    @staticmethod
    def problema_mais_comum(empresa_id):
        row = (
            db.session.query(Ocorrencia.tipo_problema, func.count().label('c'))
            .filter(Ocorrencia.empresa_id == empresa_id)
            .group_by(Ocorrencia.tipo_problema)
            .order_by(func.count().desc())
            .first()
        )
        return row[0] if row else '-'

    @staticmethod
    def listar_recentes(empresa_id, limite=5):
        rows = (
            db.session.query(Ocorrencia, Oficina.nome, Veiculo.placa)
            .outerjoin(Oficina, Ocorrencia.oficina_id == Oficina.id)
            .outerjoin(Veiculo, Ocorrencia.veiculo_id == Veiculo.id)
            .filter(Ocorrencia.empresa_id == empresa_id)
            .order_by(Ocorrencia.data_abertura.desc())
            .limit(limite)
            .all()
        )
        return [
            oc.to_dict({'oficina_nome': of_nome, 'veiculo_placa': placa})
            for oc, of_nome, placa in rows
        ]

    @staticmethod
    def listar_abertas(empresa_id, limite=5):
        rows = (
            db.session.query(Ocorrencia, Veiculo.placa)
            .outerjoin(Veiculo, Ocorrencia.veiculo_id == Veiculo.id)
            .filter(
                Ocorrencia.empresa_id == empresa_id,
                Ocorrencia.status.in_(['aberta', 'em_atendimento']),
            )
            .order_by(Ocorrencia.pane_total.desc(), Ocorrencia.data_abertura.desc())
            .limit(limite)
            .all()
        )
        return [oc.to_dict({'veiculo_placa': placa}) for oc, placa in rows]

    @staticmethod
    def agregados_relatorio(empresa_id, periodo=''):
        por_tipo_q = _filtro_periodo(
            db.session.query(Ocorrencia.tipo_problema, func.count().label('c'))
            .filter(Ocorrencia.empresa_id == empresa_id),
            periodo,
        )
        por_tipo = por_tipo_q.group_by(Ocorrencia.tipo_problema).all()

        veiculo_label = func.coalesce(Veiculo.placa, Ocorrencia.tipo_veiculo).label('veiculo')
        por_veiculo_q = _filtro_periodo(
            db.session.query(veiculo_label, func.count().label('c'))
            .select_from(Ocorrencia)
            .outerjoin(Veiculo, Ocorrencia.veiculo_id == Veiculo.id)
            .filter(Ocorrencia.empresa_id == empresa_id),
            periodo,
        )
        por_veiculo = por_veiculo_q.group_by(veiculo_label).all()

        mes = func.strftime('%m/%Y', Ocorrencia.data_abertura).label('mes')
        por_mes_q = _filtro_periodo(
            db.session.query(mes, func.count().label('c'))
            .select_from(Ocorrencia)
            .filter(Ocorrencia.empresa_id == empresa_id),
            periodo,
        )
        por_mes = por_mes_q.group_by(mes).order_by(Ocorrencia.data_abertura.desc()).limit(6).all()

        ranking_q = _filtro_periodo(
            db.session.query(Oficina.nome, func.count().label('c'))
            .select_from(Ocorrencia)
            .join(Oficina, Ocorrencia.oficina_id == Oficina.id)
            .filter(Ocorrencia.empresa_id == empresa_id),
            periodo,
        )
        ranking_oficinas = ranking_q.group_by(Oficina.id).order_by(func.count().desc()).limit(5).all()

        return {
            'por_tipo': [{'tipo_problema': t, 'c': c} for t, c in por_tipo],
            'por_veiculo': [{'veiculo': v, 'c': c} for v, c in por_veiculo],
            'por_mes': [{'mes': m, 'c': c} for m, c in por_mes],
            'ranking_oficinas': [{'nome': n, 'c': c} for n, c in ranking_oficinas],
        }
