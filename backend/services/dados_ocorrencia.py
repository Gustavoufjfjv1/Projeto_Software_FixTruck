import validacoes as v
from constantes import TIPOS_PROBLEMA
from services import posse
from services.erros import ServiceError


def _montar_endereco(via, km, cidade):
    partes = []
    if via:
        partes.append(via)
    if km:
        partes.append(f'KM {km}')
    if cidade:
        partes.append(cidade)
    return ' — '.join(partes)


def extrair_dados_ocorrencia(empresa_id, dados, motorista=None):
    """Valida o formulário de ocorrência (empresa ou motorista) e confere a posse de veículo/motorista."""
    tipo_problema = v.opcao(dados.get('tipo_problema'), TIPOS_PROBLEMA, 'Tipo de problema')
    descricao = v.texto(
        dados.get('descricao'), 'Descrição', obrigatorio=motorista is not None,
        max_len=500, min_len=5 if motorista is not None else 1,
    )
    lat, lon = v.coordenadas(dados.get('lat'), dados.get('lon'), obrigatorio=False)
    via = v.texto(dados.get('via'), 'Rodovia/avenida', obrigatorio=False, max_len=120)
    km = v.texto(dados.get('km'), 'KM', obrigatorio=False, max_len=10)
    cidade = v.texto(dados.get('cidade'), 'Cidade', obrigatorio=False, max_len=80)
    endereco = v.texto(dados.get('endereco'), 'Endereço', obrigatorio=False, max_len=255) \
        or _montar_endereco(via, km, cidade)
    if lat is None and not endereco:
        raise v.erro('Informe o local (rodovia/avenida, KM e cidade) ou capture a localização GPS.')

    if motorista is not None:
        if v.identificador(dados.get('veiculo_id'), 'Veículo') is None:
            raise v.erro('Selecione o veículo vinculado a você.')
        veiculo = posse.veiculo_da_empresa(dados.get('veiculo_id'), empresa_id)
        if veiculo.motorista_id != motorista.id:
            raise ServiceError('Você só pode registrar ocorrências do veículo vinculado a você.', 403)
        motorista_id = motorista.id
    else:
        veiculo = posse.veiculo_da_empresa(dados.get('veiculo_id'), empresa_id)
        escolhido = posse.motorista_da_empresa(dados.get('motorista_id'), empresa_id)
        motorista_id = escolhido.id if escolhido else veiculo.motorista_id

    return {
        'veiculo_id': veiculo.id,
        'motorista_id': motorista_id,
        'tipo_veiculo': veiculo.tipo_veiculo,
        'tipo_problema': tipo_problema,
        'pane_total': 1 if v.booleano(dados.get('pane_total')) else 0,
        'descricao': descricao,
        'lat': None if lat is None else str(lat),
        'lon': None if lon is None else str(lon),
        'endereco': endereco or f'GPS: {lat:.6f}, {lon:.6f}',
    }
