from database import db
from models.base import ModeloBase


class Oficina(ModeloBase):
    __tablename__ = 'oficinas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    endereco = db.Column(db.String)
    telefone = db.Column(db.String)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    cnae = db.Column(db.String(80))
    especialidades = db.Column(db.String)
    tipos_veiculo = db.Column(db.String)
    tem_guincho = db.Column(db.Integer, default=0)
    hora_abertura = db.Column(db.String, default='08:00')
    hora_fechamento = db.Column(db.String, default='18:00')
    ativa = db.Column(db.Integer, default=1)
