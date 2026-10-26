from repositories import MotoristaRepository, VeiculoRepository
from services.erros import ServiceError


class AtualizarVeiculoService:
    TIPOS_VEICULO = {'leve', 'médio', 'pesado'}

    def executar(self, empresa_id, veiculo_id, dados):
        veiculo = VeiculoRepository.buscar_da_empresa(veiculo_id, empresa_id)
        if not veiculo:
            raise ServiceError('Veículo não encontrado.', 404)

        placa = (dados.get('placa') or '').strip().upper()
        tipo_veiculo = (dados.get('tipo_veiculo') or '').strip().lower()
        if not placa:
            raise ServiceError('Placa é obrigatória.', 400)
        if tipo_veiculo not in self.TIPOS_VEICULO:
            raise ServiceError('Tipo de veículo inválido.', 400)

        duplicado = VeiculoRepository.buscar_placa_da_empresa(
            placa, empresa_id, ignorar_id=veiculo_id
        )
        if duplicado:
            raise ServiceError('Já existe um veículo com esta placa na frota.', 409)

        motorista_id = dados.get('motorista_id') or None
        if motorista_id:
            motorista = MotoristaRepository.buscar_da_empresa(motorista_id, empresa_id)
            if not motorista or not motorista.ativo:
                raise ServiceError('Selecione um motorista ativo da sua empresa.', 400)

        veiculo.placa = placa
        veiculo.modelo = (dados.get('modelo') or '').strip()
        veiculo.marca = (dados.get('marca') or '').strip()
        veiculo.tipo_veiculo = tipo_veiculo
        veiculo.motorista_id = motorista_id
        veiculo.atualizar()
        return {'mensagem': 'Veículo atualizado.'}
