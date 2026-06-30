from . import db
from .base_usuario import Usuario


class Gestor(Usuario):
    __tablename__ = "gestores"

    telefone = db.Column(db.String(20), nullable=True)

class Motorista(Usuario):
    __tablename__ = "motoristas"

    cnh = db.Column(db.String(11), nullable=True)
    veiculos = db.relationship("Veiculo", back_populates="motorista", cascade="all, delete-orphan")

class Oficina(Usuario):
    __tablename__ = "oficinas"

    nome_fantasia = db.Column(db.String(100), nullable=True)
    cnpj = db.Column(db.String(14), nullable=True)
    especialidades = db.Column(db.String(200), nullable=True)
    horario_funcionamento = db.Column(db.String(100), nullable=True)
    possui_guincho = db.Column(db.Boolean, default=False, nullable=False)
    atende_pesado = db.Column(db.Boolean, default=False, nullable=False)