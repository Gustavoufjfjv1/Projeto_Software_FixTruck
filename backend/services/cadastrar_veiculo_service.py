from models import Veiculo
from repositories import MotoristaRepository, VeiculoRepository
from services.erros import ServiceError


class CadastrarVeiculoService:
    def executar(self, empresa_id, dados):
        placa = (dados.get('placa') or '').strip().upper()
        if not placa:
            raise ServiceError('Placa é obrigatória.', 400)
        tipo_veiculo = (dados.get('tipo_veiculo') or 'pesado').strip().lower()
        if tipo_veiculo not in {'leve', 'médio', 'pesado'}:
            raise ServiceError('Tipo de veículo inválido.', 400)
        if VeiculoRepository.buscar_placa_da_empresa(placa, empresa_id):
            raise ServiceError('Já existe um veículo com esta placa na frota.', 409)

        motorista_id = dados.get('motorista_id') or None
        if motorista_id:
            motorista = MotoristaRepository.buscar_da_empresa(motorista_id, empresa_id)
            if not motorista or not motorista.ativo:
                raise ServiceError('Selecione um motorista ativo da sua empresa.', 400)

        veiculo = Veiculo(
            empresa_id=empresa_id,
            placa=placa,
            modelo=dados.get('modelo', ''),
            marca=dados.get('marca', ''),
            tipo_veiculo=tipo_veiculo,
            motorista_id=motorista_id,
        )
        veiculo.salvar()
        return {'mensagem': 'Veículo cadastrado na frota.'}
