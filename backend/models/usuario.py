from . import db
from .base_usuario import Usuario


class Gestor(Usuario):
    __tablename__ = "gestores"

    telefone = db.Column(db.String(20), nullable=True)

class Motorista(Usuario):
    __tablename__ = "motoristas"

    cnh = db.Column(db.String(11), nullable=True)
    veiculos = db.relationship("Veiculo", back_populates="motorista")
    ocorrencias = db.relationship("Ocorrencia", back_populates="motorista")


class Oficina(Usuario):
    __tablename__ = "oficinas"

    nome_fantasia = db.Column(db.String(100), nullable=True)
    cnpj = db.Column(db.String(14), nullable=True)
    especialidades = db.Column(db.String(200), nullable=True)
    horario_funcionamento = db.Column(db.String(100), nullable=True)
    possui_guincho = db.Column(db.Boolean, default=False, nullable=False)
    atende_pesado = db.Column(db.Boolean, default=False, nullable=False)
    orcamentos = db.relationship("Orcamento", back_populates="oficina")

    def esta_aberta_agora(self):
        """Indica se a oficina está aberta no momento da consulta."""
        from datetime import datetime
        if not self.horario_funcionamento or "-" not in self.horario_funcionamento:
            return None
        try:
            abertura, fechamento = [p.strip() for p in self.horario_funcionamento.split("-", 1)]
            agora = datetime.now()
            h_ab, m_ab = map(int, abertura.split(":")[:2])
            h_fe, m_fe = map(int, fechamento.split(":")[:2])
            minutos_agora = agora.hour * 60 + agora.minute
            minutos_ab = h_ab * 60 + m_ab
            minutos_fe = h_fe * 60 + m_fe
            if minutos_ab <= minutos_fe:
                return minutos_ab <= minutos_agora < minutos_fe
            return minutos_agora >= minutos_ab or minutos_agora < minutos_fe
        except (ValueError, AttributeError):
            return None
