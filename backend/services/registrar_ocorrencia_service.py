from models import Ocorrencia
from repositories import VeiculoRepository
from services.erros import ServiceError, agora_local


class RegistrarOcorrenciaService:
    def executar(self, empresa_id, dados, motorista=None):
        """Registra uma ocorrência. Com `motorista`, só aceita veículo vinculado a ele."""
        veiculo_id = dados.get('veiculo_id') or None
        motorista_id = dados.get('motorista_id') or None
        tipo_problema = dados.get('tipo_problema')
        pane_total = 1 if dados.get('pane_total') else 0
        descricao = (dados.get('descricao') or '').strip() or None
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

        tipo_veiculo = dados.get('tipo_veiculo', 'pesado')
        if motorista is not None:
            if not veiculo_id:
                raise ServiceError('Selecione o veículo vinculado a você.', 422)
            if not descricao or len(descricao) < 5:
                raise ServiceError('Descreva o problema (mínimo 5 caracteres).', 422)
            veiculo = VeiculoRepository.buscar_da_empresa(veiculo_id, empresa_id)
            if not veiculo or veiculo.motorista_id != motorista.id:
                raise ServiceError('Você só pode registrar ocorrências do veículo vinculado a você.', 403)
            tipo_veiculo = veiculo.tipo_veiculo
            motorista_id = motorista.id
        elif veiculo_id:
            veiculo = VeiculoRepository.buscar_da_empresa(veiculo_id, empresa_id)
            if veiculo:
                tipo_veiculo = veiculo.tipo_veiculo
                if not motorista_id and veiculo.motorista_id:
                    motorista_id = veiculo.motorista_id

        endereco_final = endereco or (f'GPS: {lat}, {lon}' if tem_gps else '')
        ocorrencia = Ocorrencia(
            empresa_id=empresa_id,
            motorista_id=motorista_id,
            veiculo_id=veiculo_id,
            tipo_veiculo=tipo_veiculo,
            tipo_problema=tipo_problema,
            pane_total=pane_total,
            descricao=descricao,
            lat=lat or None,
            lon=lon or None,
            endereco=endereco_final,
            status='aberta',
            data_abertura=agora_local(),
            registrada_por='motorista' if motorista is not None else 'empresa',
        )
        ocorrencia.salvar()
        return {'mensagem': 'Ocorrência registrada.', 'id': ocorrencia.id}
