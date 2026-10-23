from utils import STATUS_RESOLVIDO
from repositories import OcorrenciaRepository, VeiculoRepository
from services.erros import ServiceError


class AtualizarOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, dados):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        if oc.status == STATUS_RESOLVIDO:
            raise ServiceError('Uma ocorrência já resolvida não pode ser editada.', 400)

        veiculo_id = dados.get('veiculo_id') or None
        motorista_id = dados.get('motorista_id') or None
        tipo_problema = dados.get('tipo_problema')
        pane_total = 1 if dados.get('pane_total') else 0
        lat = dados.get('lat')
        lon = dados.get('lon')
        via = (dados.get('via') or '').strip()
        km = (dados.get('km') or '').strip()
        cidade = (dados.get('cidade') or '').strip()
        endereco = (dados.get('endereco') or '').strip()

        if not endereco:
            partes = []
            if via:
                partes.append(via)
            if km:
                partes.append(f'KM {km}')
            if cidade:
                partes.append(cidade)
            endereco = ' — '.join(partes)

        if not tipo_problema:
            raise ServiceError('Tipo de problema é obrigatório.', 400)

        tem_gps = bool(lat and lon)
        tem_endereco = bool(endereco)
        if not tem_gps and not tem_endereco:
            raise ServiceError(
                'Informe o local (rodovia/avenida, KM e cidade) ou capture a localização GPS.',
                400,
            )

        tipo_veiculo = dados.get('tipo_veiculo', oc.tipo_veiculo)
        if veiculo_id:
            veiculo = VeiculoRepository.buscar_da_empresa(veiculo_id, empresa_id)
            if veiculo:
                tipo_veiculo = veiculo.tipo_veiculo
                if not motorista_id and veiculo.motorista_id:
                    motorista_id = veiculo.motorista_id

        endereco_final = endereco or (f'GPS: {lat}, {lon}' if tem_gps else '')

        oc.motorista_id = motorista_id
        oc.veiculo_id = veiculo_id
        oc.tipo_veiculo = tipo_veiculo
        oc.tipo_problema = tipo_problema
        oc.pane_total = pane_total
        oc.descricao = (dados.get('descricao') or '').strip() or None
        oc.lat = lat or None
        oc.lon = lon or None
        oc.endereco = endereco_final
        oc.atualizar()
        return {'mensagem': 'Ocorrência atualizada.'}
