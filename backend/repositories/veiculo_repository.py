from database import db
from models import Veiculo, Motorista


class VeiculoRepository:
    """Consultas de veículos com joins."""

    @staticmethod
    def listar_por_empresa(empresa_id):
        rows = (
            db.session.query(Veiculo, Motorista.nome)
            .outerjoin(Motorista, Veiculo.motorista_id == Motorista.id)
            .filter(Veiculo.empresa_id == empresa_id)
            .order_by(Veiculo.placa)
            .all()
        )
        return [v.to_dict({'motorista_nome': nome}) for v, nome in rows]

    @staticmethod
    def listar_simples(empresa_id):
        veiculos = Veiculo.query.filter_by(empresa_id=empresa_id).order_by(Veiculo.placa).all()
        return [{'id': v.id, 'placa': v.placa, 'modelo': v.modelo} for v in veiculos]

    @staticmethod
    def buscar_da_empresa(veiculo_id, empresa_id):
        return Veiculo.query.filter_by(id=veiculo_id, empresa_id=empresa_id).first()
