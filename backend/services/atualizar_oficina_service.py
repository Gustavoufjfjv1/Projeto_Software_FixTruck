from models import Oficina
from repositories import OficinaRepository
from services.cadastrar_oficina_service import extrair_dados_oficina
from services.erros import ServiceError


def buscar_oficina_editavel(empresa_id, oficina_id):
    """Só a empresa que cadastrou a oficina pode alterá-la; a base do seed é somente leitura."""
    oficina = Oficina.buscar_por_id(oficina_id)
    if not oficina:
        raise ServiceError('Oficina não encontrada.', 404)
    if oficina.empresa_id != empresa_id:
        raise ServiceError('Você só pode alterar oficinas cadastradas pela sua empresa.', 403)
    return oficina


class AtualizarOficinaService:
    def executar(self, empresa_id, oficina_id, dados):
        oficina = buscar_oficina_editavel(empresa_id, oficina_id)
        campos = extrair_dados_oficina(dados)
        if OficinaRepository.buscar_duplicada(campos['nome'], campos['endereco'], ignorar_id=oficina.id):
            raise ServiceError('Já existe uma oficina com este nome neste endereço.', 409)
        for campo, valor in campos.items():
            setattr(oficina, campo, valor)
        oficina.atualizar()
        return {'mensagem': 'Oficina atualizada.', 'oficina': oficina.to_dict()}


class AlterarStatusOficinaService:
    def executar(self, empresa_id, oficina_id, dados):
        oficina = buscar_oficina_editavel(empresa_id, oficina_id)
        if 'ativa' not in dados or not isinstance(dados.get('ativa'), (bool, int)):
            raise ServiceError('Informe "ativa": true ou false.', 422)
        oficina.ativa = 1 if dados['ativa'] else 0
        oficina.atualizar()
        return {
            'mensagem': 'Oficina ativada.' if oficina.ativa else 'Oficina desativada.',
            'oficina': oficina.to_dict(),
        }


class ListarMinhasOficinasService:
    def executar(self, empresa_id):
        return {
            'oficinas': [o.to_dict() for o in OficinaRepository.listar_da_empresa(empresa_id)],
            'total_base_ativa': OficinaRepository.contar_ativas(),
        }
