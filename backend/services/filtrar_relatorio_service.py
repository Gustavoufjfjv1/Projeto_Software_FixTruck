from services.erros import ServiceError
from services.gerar_relatorio_service import GerarRelatorioService


class FiltrarRelatorioService:
    STATUS_VALIDOS = {'', 'aberta', 'em_atendimento', 'resolvido'}

    def executar(self, empresa_id, periodo='', status=''):
        if periodo not in {'', '7d', '30d', '90d'}:
            raise ServiceError('Período de relatório inválido.', 400)
        if status not in self.STATUS_VALIDOS:
            raise ServiceError('Status de ocorrência inválido.', 400)
        return GerarRelatorioService().executar(empresa_id, {'periodo': periodo, 'status': status})
