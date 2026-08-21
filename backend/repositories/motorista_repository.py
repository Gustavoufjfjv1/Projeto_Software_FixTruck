from models import Motorista, Veiculo


class MotoristaRepository:
    """Consultas de motoristas com joins."""

    @staticmethod
    def listar_por_empresa(empresa_id, apenas_ativos=False):
        query = Motorista.query.filter_by(empresa_id=empresa_id)
        if apenas_ativos:
            query = query.filter_by(ativo=1)
        return [m.to_dict() for m in query.order_by(Motorista.nome).all()]

    @staticmethod
    def listar_com_veiculo(empresa_id):
        motoristas = Motorista.query.filter_by(empresa_id=empresa_id).order_by(Motorista.nome).all()
        resultado = []
        for m in motoristas:
            veiculo = Veiculo.query.filter_by(motorista_id=m.id).first()
            resultado.append(m.to_dict({
                'veiculo_placa': veiculo.placa if veiculo else None,
            }))
        return resultado

    @staticmethod
    def buscar_da_empresa(motorista_id, empresa_id):
        return Motorista.query.filter_by(id=motorista_id, empresa_id=empresa_id).first()
