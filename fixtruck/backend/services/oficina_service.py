"""Serviço de Oficinas"""

from models.oficina import Oficina
from repositories.oficina_repository import OficinaRepository
from math import radians, cos, sin, asin, sqrt


class OficinaService:
    """Gerencia operações relacionadas a oficinas"""
    
    def __init__(self):
        self.oficina_repo = OficinaRepository()
    
    def criar_oficina(self, dados):
        """Cria uma nova oficina"""
        
        oficina = Oficina(
            nome_fantasia=dados['nome_fantasia'],
            latitude=dados['latitude'],
            longitude=dados['longitude'],
            cnpj=dados.get('cnpj'),
            especialidades=dados.get('especialidades'),
            horario_funcionamento=dados.get('horario_funcionamento'),
            possui_guincho=dados.get('possui_guincho', False),
            atende_pesado=dados.get('atende_pesado', False),
            endereco=dados.get('endereco'),
            bairro=dados.get('bairro'),
            numero_imovel=dados.get('numero_imovel'),
            cnae_principal=dados.get('cnae_principal')
        )
        
        oficina_criada = self.oficina_repo.criar(oficina)
        
        return oficina_criada.to_dict(include_endereco_completo=True)
    
    def obter_oficina(self, id_oficina):
        """Obtém informações de uma oficina"""
        oficina = self.oficina_repo.obter_por_id(id_oficina)
        
        if oficina:
            return oficina.to_dict(include_endereco_completo=True)
        
        return None
    
    def buscar_por_raio(self, latitude, longitude, raio_km, especialidade=None, possui_guincho=False):
        """Busca oficinas em um raio de distância"""
        
        # Obter todas as oficinas ativas
        oficinas = self.oficina_repo.listar_ativas()
        
        resultado = []
        
        for oficina in oficinas:
            # Calcular distância
            distancia = self._calcular_distancia(
                latitude, longitude,
                oficina.latitude, oficina.longitude
            )
            
            # Filtrar por raio
            if distancia <= raio_km:
                # Filtrar por especialidade se fornecido
                if especialidade and oficina.especialidades:
                    if especialidade.lower() not in oficina.especialidades.lower():
                        continue
                
                # Filtrar por guincho se necessário
                if possui_guincho and not oficina.possui_guincho:
                    continue
                
                dados_oficina = oficina.to_dict()
                dados_oficina['distancia_km'] = round(distancia, 2)
                resultado.append(dados_oficina)
        
        # Ordenar por distância
        resultado.sort(key=lambda x: x['distancia_km'])
        
        return resultado
    
    def listar_oficinas(self, ativo=True, especialidade=None):
        """Lista todas as oficinas com filtros opcionais"""
        oficinas = self.oficina_repo.listar_todos(ativo=ativo)
        
        resultado = []
        for oficina in oficinas:
            # Filtrar por especialidade se fornecido
            if especialidade and oficina.especialidades:
                if especialidade.lower() not in oficina.especialidades.lower():
                    continue
            
            resultado.append(oficina.to_dict())
        
        return resultado
    
    def atualizar_oficina(self, id_oficina, dados):
        """Atualiza informações de uma oficina"""
        oficina = self.oficina_repo.obter_por_id(id_oficina)
        
        if not oficina:
            return None
        
        campos_permitidos = [
            'nome_fantasia', 'especialidades', 'horario_funcionamento',
            'possui_guincho', 'atende_pesado', 'endereco', 'bairro',
            'numero_imovel', 'ativo'
        ]
        
        for campo in campos_permitidos:
            if campo in dados:
                setattr(oficina, campo, dados[campo])
        
        self.oficina_repo.atualizar(oficina)
        
        return oficina.to_dict(include_endereco_completo=True)
    
    def atualizar_status_atendimento(self, id_oficina, status):
        """Atualiza o status de atendimento de uma oficina"""
        oficina = self.oficina_repo.obter_por_id(id_oficina)
        
        if not oficina:
            return False
        
        if status in ['ativa', 'inativa', 'mantencao']:
            oficina.ativo = status in ['ativa']
            self.oficina_repo.atualizar(oficina)
            return True
        
        return False
    
    @staticmethod
    def _calcular_distancia(lat1, lon1, lat2, lon2):
        """
        Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine
        Retorna a distância em quilômetros
        """
        # Converter para radianos
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Raio da Terra em km
        r = 6371
        
        return c * r
