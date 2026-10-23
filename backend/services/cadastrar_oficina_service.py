import json

import validacoes as v
from constantes import ESPECIALIDADES_OFICINA, TIPOS_VEICULO, UFS
from horarios import normalizar_horarios
from models import Oficina
from repositories import OficinaRepository
from services.erros import ServiceError


def extrair_dados_oficina(dados):
    """Valida o corpo de criação/edição de oficina e devolve os campos já normalizados."""
    aberta_24h = v.booleano(dados.get('aberta_24h'))
    horarios = None
    if not aberta_24h:
        try:
            horarios = normalizar_horarios(dados.get('horarios') or {})
        except ValueError as e:
            raise v.erro(str(e))
        if not any(horarios.values()):
            raise v.erro('Informe o horário de pelo menos um dia ou marque a oficina como 24 horas.')
    lat, lon = v.coordenadas(dados.get('lat'), dados.get('lon'))
    return {
        'nome': v.texto(dados.get('nome'), 'Nome', max_len=100, min_len=3),
        'endereco': v.texto(dados.get('endereco'), 'Endereço', max_len=160, min_len=5),
        'cidade': v.texto(dados.get('cidade'), 'Cidade', max_len=80, min_len=2),
        'uf': v.opcao(dados.get('uf'), [u.lower() for u in UFS], 'UF').upper(),
        'telefone': v.telefone(dados.get('telefone'), obrigatorio=True),
        'lat': lat,
        'lon': lon,
        'especialidades': ','.join(
            v.opcoes(dados.get('especialidades'), ESPECIALIDADES_OFICINA, 'Tipos de problema atendidos')
        ),
        'tipos_veiculo': ','.join(
            v.opcoes(dados.get('tipos_veiculo'), TIPOS_VEICULO, 'Tipos de veículo atendidos')
        ),
        'tem_guincho': 1 if v.booleano(dados.get('tem_guincho')) else 0,
        'aberta_24h': 1 if aberta_24h else 0,
        'horarios': json.dumps(horarios) if horarios else None,
    }


class CadastrarOficinaService:
    def executar(self, empresa_id, dados):
        campos = extrair_dados_oficina(dados)
        if OficinaRepository.buscar_duplicada(campos['nome'], campos['endereco']):
            raise ServiceError('Já existe uma oficina com este nome neste endereço.', 409)
        oficina = Oficina(empresa_id=empresa_id, ativa=1, **campos)
        oficina.salvar()
        return {'mensagem': 'Oficina cadastrada.', 'oficina': oficina.to_dict()}
