"""Models package - Entidades e mapeamento com banco de dados"""

from .usuario import Usuario
from .empresa_transporte import EmpresaTransporte
from .gestor import Gestor
from .motorista import Motorista
from .veiculo import Veiculo
from .oficina import Oficina
from .ocorrencia import Ocorrencia
from .orcamento import Orcamento
from .mensagem_chat import MensagemChat
from .oficina_favorita import OficinaFavorita

__all__ = [
    'Usuario',
    'EmpresaTransporte',
    'Gestor',
    'Motorista',
    'Veiculo',
    'Oficina',
    'Ocorrencia',
    'Orcamento',
    'MensagemChat',
    'OficinaFavorita'
]
