from models import Ocorrencia
from services.dados_ocorrencia import extrair_dados_ocorrencia
from services.erros import agora_local


class RegistrarOcorrenciaService:
    def executar(self, empresa_id, dados, motorista=None):
        """Registra uma ocorrência. Com `motorista`, só aceita veículo vinculado a ele."""
        campos = extrair_dados_ocorrencia(empresa_id, dados, motorista)
        ocorrencia = Ocorrencia(
            empresa_id=empresa_id,
            status='aberta',
            data_abertura=agora_local(),
            registrada_por='motorista' if motorista is not None else 'empresa',
            **campos,
        )
        ocorrencia.salvar()
        return {'mensagem': 'Ocorrência registrada.', 'id': ocorrencia.id}
