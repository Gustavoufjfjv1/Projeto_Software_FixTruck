from database import db
from models.base import ModeloBase


class Orcamento(ModeloBase):
    __tablename__ = 'orcamentos'

    id = db.Column(db.Integer, primary_key=True)
    ocorrencia_id = db.Column(db.Integer, db.ForeignKey('ocorrencias.id'), nullable=False)
    oficina_id = db.Column(db.Integer, db.ForeignKey('oficinas.id'), nullable=False)
    valor_pecas = db.Column(db.Float, nullable=False, default=0)
    valor_mao_obra = db.Column(db.Float, nullable=False, default=0)
    descricao = db.Column(db.String)
    status = db.Column(db.String, default='pendente')
    data_envio = db.Column(db.String, server_default=db.func.current_timestamp())
    data_resposta = db.Column(db.String)
