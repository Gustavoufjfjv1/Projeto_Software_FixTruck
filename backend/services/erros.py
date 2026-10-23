class ServiceError(Exception):
    """Erro de regra de negócio com código HTTP associado."""

    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def agora_local():
    from horarios import agora_sao_paulo
    return agora_sao_paulo().strftime('%Y-%m-%d %H:%M:%S')
