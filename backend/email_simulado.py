"""Envio de e-mail simulado: o projeto acadêmico não tem servidor SMTP.

A mensagem é escrita no console do backend (terminal onde roda `python app.py`)
e guardada em memória (CAIXA_DE_SAIDA) para os testes automatizados.
Nada disso é devolvido na resposta HTTP, para não revelar se o e-mail existe.
"""
from collections import deque

CAIXA_DE_SAIDA = deque(maxlen=50)


def enviar(destinatario, assunto, corpo):
    CAIXA_DE_SAIDA.append({'para': destinatario, 'assunto': assunto, 'corpo': corpo})
    print(f'\n===== E-MAIL SIMULADO =====\nPara: {destinatario}\nAssunto: {assunto}\n\n{corpo}\n===========================\n',
          flush=True)
