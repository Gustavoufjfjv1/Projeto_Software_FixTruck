"""Modelo de Orçamento"""

from app import db
from datetime import datetime


class Orcamento(db.Model):
    """Representa um orçamento enviado por uma oficina"""
    
    __tablename__ = 'orcamentos'
    
    id_orcamento = db.Column(db.Integer, primary_key=True)
    id_ocorrencia = db.Column(db.Integer, db.ForeignKey('ocorrencias.id_ocorrencia'), nullable=False)
    id_oficina = db.Column(db.Integer, db.ForeignKey('oficinas.id_oficina'), nullable=False)
    valor_pecas = db.Column(db.Float, nullable=False, default=0)
    valor_mao_obra = db.Column(db.Float, nullable=False, default=0)
    status_aprovacao = db.Column(
        db.Enum('pendente', 'aprovado', 'rejeitado'),
        default='pendente',
        nullable=False,
        index=True
    )
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_resposta = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    
    def __init__(self, id_ocorrencia, id_oficina, valor_pecas, valor_mao_obra, **kwargs):
        self.id_ocorrencia = id_ocorrencia
        self.id_oficina = id_oficina
        self.valor_pecas = valor_pecas
        self.valor_mao_obra = valor_mao_obra
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calcular_total(self):
        """Calcula o valor total do orçamento"""
        return self.valor_pecas + self.valor_mao_obra
    
    def alterar_status_aprovacao(self, novo_status):
        """Altera o status de aprovação do orçamento"""
        if novo_status in ['pendente', 'aprovado', 'rejeitado']:
            self.status_aprovacao = novo_status
            self.data_resposta = datetime.utcnow()
            return True
        return False
    
    def to_dict(self, include_detalhes=False):
        """Converte o orçamento para dicionário"""
        data = {
            'id_orcamento': self.id_orcamento,
            'valor_pecas': self.valor_pecas,
            'valor_mao_obra': self.valor_mao_obra,
            'valor_total': self.calcular_total(),
            'status_aprovacao': self.status_aprovacao,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_resposta': self.data_resposta.isoformat() if self.data_resposta else None
        }
        
        if include_detalhes:
            data['id_ocorrencia'] = self.id_ocorrencia
            data['id_oficina'] = self.id_oficina
            data['observacoes'] = self.observacoes
            data['oficina'] = self.oficina.to_dict() if self.oficina else None
        
        return data
    
    def __repr__(self):
        return f'<Orcamento {self.id_orcamento}>'
