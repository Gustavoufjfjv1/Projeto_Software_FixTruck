from models import Veiculo
from services.erros import ServiceError


class CadastrarVeiculoService:
    def executar(self, empresa_id, dados):
        placa = (dados.get('placa') or '').strip().upper()
        if not placa:
            raise ServiceError('Placa é obrigatória.', 400)
        veiculo = Veiculo(
            empresa_id=empresa_id,
            placa=placa,
            modelo=dados.get('modelo', ''),
            marca=dados.get('marca', ''),
            tipo_veiculo=dados.get('tipo_veiculo', 'pesado'),
            motorista_id=dados.get('motorista_id') or None,
        )
        veiculo.salvar()
        return {'mensagem': 'Veículo cadastrado na frota.'}
