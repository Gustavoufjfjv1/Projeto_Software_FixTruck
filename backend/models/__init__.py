from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .base import ModeloBase
from .base_usuario import  Usuario
from .empresa import Empresa
from .usuario import Gestor, Motorista, Oficina
from .veiculo import Veiculo
from .ocorrencia import Ocorrencia
from .orcamento import Orcamento
from .mensagem_chat import MensagemChat
