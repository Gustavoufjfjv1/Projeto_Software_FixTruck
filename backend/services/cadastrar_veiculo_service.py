import validacoes as v
from constantes import TIPOS_VEICULO
from models import Veiculo
from services import posse
from services.erros import ServiceError


class CadastrarVeiculoService:
    def executar(self, empresa_id, dados):
        placa = v.placa(dados.get('placa'))
        if Veiculo.query.filter_by(placa=placa).first():
            raise ServiceError('Esta placa já está cadastrada no sistema.', 409)
        motorista = posse.motorista_da_empresa(dados.get('motorista_id'), empresa_id)
        veiculo = Veiculo(
            empresa_id=empresa_id,
            placa=placa,
            modelo=v.texto(dados.get('modelo'), 'Modelo', obrigatorio=False, max_len=60),
            marca=v.texto(dados.get('marca'), 'Marca', obrigatorio=False, max_len=40),
            tipo_veiculo=v.opcao(dados.get('tipo_veiculo') or 'pesado', TIPOS_VEICULO, 'Tipo de veículo'),
            motorista_id=motorista.id if motorista else None,
        )
        veiculo.salvar()
        return {'mensagem': 'Veículo cadastrado na frota.', 'id': veiculo.id, 'placa': placa}
