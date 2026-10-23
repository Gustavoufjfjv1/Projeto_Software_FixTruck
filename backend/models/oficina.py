from database import db
from models.base import ModeloBase
from horarios import carregar_horarios, resumo_horarios


class Oficina(ModeloBase):
    __tablename__ = 'oficinas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    endereco = db.Column(db.String)
    cidade = db.Column(db.String)
    uf = db.Column(db.String)
    telefone = db.Column(db.String)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    especialidades = db.Column(db.String, nullable=False, default='', server_default='')
    tipos_veiculo = db.Column(db.String, nullable=False, default='', server_default='')
    tem_guincho = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    aberta_24h = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    horarios = db.Column(db.String)
    ativa = db.Column(db.Integer, nullable=False, default=1, server_default='1')
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    criado_em = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def lista_especialidades(self):
        return [e.strip().lower() for e in (self.especialidades or '').split(',') if e.strip()]

    def lista_tipos_veiculo(self):
        return [t.strip().lower() for t in (self.tipos_veiculo or '').split(',') if t.strip()]

    def horarios_dict(self):
        return carregar_horarios(self.horarios)

    def to_dict(self, extras=None):
        data = super().to_dict()
        data['horarios'] = self.horarios_dict()
        data['horario_resumo'] = resumo_horarios(data['horarios'], bool(self.aberta_24h))
        data['ativa'] = bool(self.ativa)
        data['tem_guincho'] = bool(self.tem_guincho)
        data['aberta_24h'] = bool(self.aberta_24h)
        if extras:
            data.update(extras)
        return data
