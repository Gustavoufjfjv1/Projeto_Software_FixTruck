from models import Ocorrencia, Orcamento, Oficina, Veiculo, Motorista, Favorito
from utils import STATUS_RESOLVIDO, haversine, oficina_aberta_agora
from services.erros import ServiceError, agora_local


class OcorrenciaService:
    @staticmethod
    def listar(empresa_id, filtros):
        return {
            'ocorrencias': Ocorrencia.listar_por_empresa(empresa_id, filtros),
            'veiculos': Veiculo.listar_simples(empresa_id),
        }

    @staticmethod
    def form_data(empresa_id):
        return {
            'veiculos': Veiculo.listar_por_empresa(empresa_id),
            'motoristas': Motorista.listar_por_empresa(empresa_id, apenas_ativos=True),
        }

    @staticmethod
    def criar(empresa_id, dados):
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

        tipo_veiculo = dados.get('tipo_veiculo', 'pesado')
        if veiculo_id:
            veiculo = Veiculo.buscar_da_empresa(veiculo_id, empresa_id)
            if veiculo:
                tipo_veiculo = veiculo['tipo_veiculo']
                if not motorista_id and veiculo.get('motorista_id'):
                    motorista_id = veiculo['motorista_id']

        endereco_final = endereco or (f'GPS: {lat}, {lon}' if tem_gps else '')
        oc_id = Ocorrencia.cadastrar({
            'empresa_id': empresa_id,
            'motorista_id': motorista_id,
            'veiculo_id': veiculo_id,
            'tipo_veiculo': tipo_veiculo,
            'tipo_problema': tipo_problema,
            'pane_total': pane_total,
            'lat': lat or None,
            'lon': lon or None,
            'endereco': endereco_final,
            'status': 'aberta',
            'data_abertura': agora_local(),
        })
        return {'mensagem': 'Ocorrência registrada.', 'id': oc_id}

    @staticmethod
    def detalhe(empresa_id, ocorrencia_id):
        oc = Ocorrencia.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        return {
            'ocorrencia': oc,
            'orcamentos': Orcamento.listar_por_ocorrencia(ocorrencia_id),
            'oficinas': Oficina.listar_ativas(),
        }

    @staticmethod
    def buscar_oficinas(empresa_id, ocorrencia_id, raio=None):
        oc = Ocorrencia.buscar_simples_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)

        oficinas = []
        for of in Oficina.listar_ativas():
            of_dict = dict(of)
            if oc.get('lat') and oc.get('lon'):
                try:
                    dist = haversine(
                        float(oc['lat']), float(oc['lon']), of['lat'], of['lon']
                    )
                    of_dict['distancia'] = round(dist, 1)
                except (TypeError, ValueError):
                    of_dict['distancia'] = None
            else:
                of_dict['distancia'] = None

            if raio is not None and of_dict['distancia'] is not None and of_dict['distancia'] > raio:
                continue

            of_dict['aberta_agora'] = oficina_aberta_agora(
                of.get('hora_abertura'), of.get('hora_fechamento')
            )
            of_dict['atende_tipo'] = oc['tipo_problema'].lower() in (
                of.get('especialidades') or ''
            ).lower()
            of_dict['atende_veiculo'] = oc['tipo_veiculo'].lower() in (
                of.get('tipos_veiculo') or ''
            ).lower()
            of_dict['favoritada'] = Favorito.buscar_par(empresa_id, of['id']) is not None
            oficinas.append(of_dict)

        if oc.get('pane_total'):
            oficinas.sort(key=lambda x: (not x.get('tem_guincho', False), x['distancia'] or 9999))
        else:
            oficinas.sort(key=lambda x: (x['distancia'] or 9999))

        return {'ocorrencia': oc, 'oficinas': oficinas, 'raio': raio}

    @staticmethod
    def encerrar(empresa_id, ocorrencia_id, dados):
        oc = Ocorrencia.buscar_simples_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        if oc['status'] == STATUS_RESOLVIDO:
            raise ServiceError('Esta ocorrência já está resolvida.', 400)

        oficina_id = dados.get('oficina_id')
        if not oficina_id:
            raise ServiceError('Selecione uma oficina para encerrar a ocorrência.', 400)

        Ocorrencia.editar(ocorrencia_id, {
            'status': STATUS_RESOLVIDO,
            'oficina_id': oficina_id,
            'motivo_resolucao': dados.get('motivo', ''),
            'observacoes': dados.get('observacoes', ''),
            'data_encerramento': agora_local(),
        })
        return {'mensagem': 'Ocorrência encerrada com status resolvido.'}

    @staticmethod
    def atualizar_status(empresa_id, ocorrencia_id, dados):
        oc = Ocorrencia.buscar_simples_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        novo_status = dados.get('status')
        if novo_status not in ['aberta', 'em_atendimento']:
            raise ServiceError('Status inválido.', 400)
        Ocorrencia.editar(ocorrencia_id, {'status': novo_status})
        return {'mensagem': 'Status atualizado.'}

    @staticmethod
    def vincular_oficina(empresa_id, ocorrencia_id, dados):
        oc = Ocorrencia.buscar_simples_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        oficina_id = dados.get('oficina_id')
        if not oficina_id:
            raise ServiceError('Oficina é obrigatória.', 400)
        Ocorrencia.editar(ocorrencia_id, {
            'oficina_id': oficina_id,
            'status': 'em_atendimento',
        })
        return {'mensagem': 'Oficina vinculada à ocorrência.'}
