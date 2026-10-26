import csv
from io import StringIO

from services.filtrar_relatorio_service import FiltrarRelatorioService


class GerarRelatorioCsvService:
    def executar(self, empresa_id, periodo='', status=''):
        relatorio = FiltrarRelatorioService().executar(empresa_id, periodo, status)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Indicador', 'Valor'])
        for chave, rotulo in (
            ('total', 'Total de ocorrências'),
            ('abertas', 'Abertas'),
            ('em_atendimento', 'Em atendimento'),
            ('encerradas', 'Resolvidas'),
            ('tempo_medio', 'Tempo médio de resolução (minutos)'),
            ('tempo_medio_oficina', 'Tempo médio até encontrar oficina (minutos)'),
        ):
            writer.writerow([rotulo, relatorio[chave]])

        for chave, rotulo, campo in (
            ('por_tipo', 'Ocorrências por tipo de problema', 'tipo_problema'),
            ('por_veiculo', 'Ocorrências por veículo', 'veiculo'),
            ('por_mes', 'Ocorrências por mês', 'mes'),
            ('ranking_oficinas', 'Oficinas mais utilizadas', 'nome'),
        ):
            writer.writerow([])
            writer.writerow([rotulo, 'Quantidade'])
            for linha in relatorio[chave]:
                valor = str(linha.get(campo) or '')
                if valor.startswith(('=', '+', '-', '@')):
                    valor = "'" + valor
                writer.writerow([valor, linha.get('c', 0)])

        return '\ufeff' + output.getvalue()
