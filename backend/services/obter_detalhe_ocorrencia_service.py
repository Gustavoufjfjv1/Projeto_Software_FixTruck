from repositories import OcorrenciaRepository, FavoritoRepository, OficinaRepository
from services.erros import ServiceError
from utils import minutos_entre


class ObterDetalheOcorrenciaService:
    def executar(self, empresa_id, ocorrencia_id):
        oc = OcorrenciaRepository.buscar_detalhe(ocorrencia_id, empresa_id)
        if not oc:
            raise ServiceError('Ocorrência não encontrada.', 404)

        oc['tempo_ate_oficina_min'] = minutos_entre(oc.get('data_abertura'), oc.get('data_vinculacao'))
        oc['tempo_total_min'] = minutos_entre(oc.get('data_abertura'), oc.get('data_encerramento'))
        oc['oficina_favoritada'] = (
            FavoritoRepository.buscar_par(empresa_id, oc['oficina_id']) is not None
            if oc.get('oficina_id') else None
        )
        return {
            'ocorrencia': oc,
            'oficinas': [o.to_dict() for o in OficinaRepository.listar_ativas()],
        }
