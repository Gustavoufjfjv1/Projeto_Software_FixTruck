"""Verificação de existência e posse de registros referenciados no corpo da requisição.

Convenção: id inválido ou inexistente -> 422; existe mas é de outra empresa -> 403.
O recurso da URL (ex.: /ocorrencias/<id>) de outra empresa responde 404 nos próprios Services.
"""
import validacoes as v
from models import Motorista, Oficina, Veiculo
from services.erros import ServiceError


def _da_empresa(modelo, valor, empresa_id, rotulo, obrigatorio):
    registro_id = v.identificador(valor, rotulo, obrigatorio=obrigatorio)
    if registro_id is None:
        return None
    registro = modelo.buscar_por_id(registro_id)
    if not registro:
        raise v.erro(f'{rotulo} não encontrado.')
    if registro.empresa_id != empresa_id:
        raise ServiceError(f'{rotulo} pertence a outra empresa.', 403)
    return registro


def veiculo_da_empresa(valor, empresa_id, obrigatorio=True):
    return _da_empresa(Veiculo, valor, empresa_id, 'Veículo', obrigatorio)


def motorista_da_empresa(valor, empresa_id, obrigatorio=False):
    return _da_empresa(Motorista, valor, empresa_id, 'Motorista', obrigatorio)


def oficina_disponivel(valor, permitir_id=None):
    """Oficinas formam um catálogo compartilhado: basta existir e estar ativa
    (uma desativada só é aceita se já estiver vinculada à ocorrência, `permitir_id`)."""
    oficina_id = v.identificador(valor, 'Oficina', obrigatorio=True)
    oficina = Oficina.buscar_por_id(oficina_id)
    if not oficina or (not oficina.ativa and oficina_id != permitir_id):
        raise v.erro('Oficina não encontrada ou desativada.')
    return oficina
