from database import db
from models.base import ModeloBase


class Ocorrencia(ModeloBase):
    __tablename__ = 'ocorrencias'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'))
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'))
    tipo_veiculo = db.Column(db.String, nullable=False)
    tipo_problema = db.Column(db.String, nullable=False)
    pane_total = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    lat = db.Column(db.String)
    lon = db.Column(db.String)
    endereco = db.Column(db.String)
    status = db.Column(db.String, nullable=False, default='aberta', server_default='aberta')
    oficina_id = db.Column(db.Integer, db.ForeignKey('oficinas.id'))
    motivo_resolucao = db.Column(db.String)
    observacoes = db.Column(db.String)
    data_abertura = db.Column(db.String)
    data_encerramento = db.Column(db.String)
    data_vinculacao = db.Column(db.String)
