from flask import current_app

from repositories import OcorrenciaRepository, OficinaRepository
from services.erros import ServiceError
from services.workshop_matcher import CriteriosBusca, WorkshopMatcher

JANELA_MAXIMA_MINUTOS = 12 * 60


def _float_ou_none(valor):
    try:
        return float(valor) if valor not in (None, '') else None
    except (TypeError, ValueError):
        return None


def buscar_oficinas_compativeis(empresa_id, oc, raio=None, janela=None, quando=None):
    """Aplica o WorkshopMatcher a uma ocorrência (usado pela empresa e pelo motorista)."""
    if raio is not None and raio <= 0:
        raise ServiceError('O raio deve ser maior que zero.', 422)
    if janela is None:
        janela = current_app.config.get('JANELA_ABERTURA_MINUTOS', 0)
    if janela < 0 or janela > JANELA_MAXIMA_MINUTOS:
        raise ServiceError(f'A janela de abertura deve estar entre 0 e {JANELA_MAXIMA_MINUTOS} minutos.', 422)

    criterios = CriteriosBusca(
        tipo_problema=oc.tipo_problema,
        tipo_veiculo=oc.tipo_veiculo,
        pane_total=bool(oc.pane_total),
        lat=_float_ou_none(oc.lat),
        lon=_float_ou_none(oc.lon),
        raio_km=raio,
        quando=quando,
        janela_minutos=int(janela),
        favoritos=OficinaRepository.ids_favoritos(empresa_id),
    )
    oficinas = [o.to_dict() for o in OficinaRepository.listar_ativas()]
    resultado = WorkshopMatcher().recomendar(oficinas, criterios)
    resultado.update({
        'ocorrencia': oc.to_dict(),
        'raio': raio,
        'janela_minutos': int(janela),
        'sem_localizacao': not criterios.tem_localizacao,
    })
    return resultado


class BuscarOficinasParaOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id, raio=None, janela=None, quando=None):
        oc = OcorrenciaRepository.buscar_da_empresa(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)
        return buscar_oficinas_compativeis(empresa_id, oc, raio=raio, janela=janela, quando=quando)
