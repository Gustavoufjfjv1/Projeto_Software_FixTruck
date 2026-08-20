class ServiceError(Exception):
    """Erro de regra de negócio com código HTTP associado."""

    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


def agora_local():
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
