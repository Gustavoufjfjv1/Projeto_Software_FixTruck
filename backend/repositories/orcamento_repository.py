from database import db
from models import Orcamento, Ocorrencia, Oficina, Veiculo


class OrcamentoRepository:
    """Consultas complexas de orçamentos."""

    @staticmethod
    def listar_por_empresa(empresa_id, status=''):
        query = (
            db.session.query(
                Orcamento,
                Oficina.nome.label('oficina_nome'),
                Ocorrencia.tipo_problema,
                Ocorrencia.status.label('oc_status'),
                Veiculo.placa.label('veiculo_placa'),
            )
            .join(Ocorrencia, Orcamento.ocorrencia_id == Ocorrencia.id)
            .join(Oficina, Orcamento.oficina_id == Oficina.id)
            .outerjoin(Veiculo, Ocorrencia.veiculo_id == Veiculo.id)
            .filter(Ocorrencia.empresa_id == empresa_id)
        )
        if status:
            query = query.filter(Orcamento.status == status)
        rows = query.order_by(Orcamento.data_envio.desc()).all()
        resultado = []
        for orc, oficina_nome, tipo_problema, oc_status, veiculo_placa in rows:
            data = orc.to_dict({
                'oficina_nome': oficina_nome,
                'tipo_problema': tipo_problema,
                'oc_status': oc_status,
                'veiculo_placa': veiculo_placa,
                'total': (orc.valor_pecas or 0) + (orc.valor_mao_obra or 0),
            })
            resultado.append(data)
        return resultado

    @staticmethod
    def listar_por_ocorrencia(ocorrencia_id):
        rows = (
            db.session.query(Orcamento, Oficina.nome)
            .join(Oficina, Orcamento.oficina_id == Oficina.id)
            .filter(Orcamento.ocorrencia_id == ocorrencia_id)
            .order_by(Orcamento.data_envio.desc())
            .all()
        )
        return [
            orc.to_dict({
                'oficina_nome': nome,
                'total': (orc.valor_pecas or 0) + (orc.valor_mao_obra or 0),
            })
            for orc, nome in rows
        ]

    @staticmethod
    def contar_pendentes(empresa_id):
        return (
            db.session.query(Orcamento)
            .join(Ocorrencia, Orcamento.ocorrencia_id == Ocorrencia.id)
            .filter(Ocorrencia.empresa_id == empresa_id, Orcamento.status == 'pendente')
            .count()
        )

    @staticmethod
    def buscar_da_empresa(orcamento_id, empresa_id):
        return (
            db.session.query(Orcamento)
            .join(Ocorrencia, Orcamento.ocorrencia_id == Ocorrencia.id)
            .filter(Orcamento.id == orcamento_id, Ocorrencia.empresa_id == empresa_id)
            .first()
        )
