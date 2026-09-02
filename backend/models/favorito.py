from database import db
from models.base import ModeloBase


class Favorito(ModeloBase):
    __tablename__ = 'favoritos'

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    oficina_id = db.Column(db.Integer, db.ForeignKey('oficinas.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('empresa_id', 'oficina_id', name='uq_favorito_empresa_oficina'),
    )
