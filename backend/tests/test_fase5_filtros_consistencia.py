import re
import sqlite3
import unittest
from datetime import timedelta

from tests.base import FixTruckTestCase
import constantes
import migracoes
from horarios import agora_sao_paulo
from models import Empresa, Motorista, Veiculo, Oficina, Ocorrencia, Favorito


class FiltroDatasTestCase(FixTruckTestCase):
    def setUp(self):
        super().setUp()
        self.h = self.login_empresa()
        self.empresa_id = self.sql("SELECT id FROM empresas WHERE email='demo@fixtruck.com'")[0][0]
        self.sql('DELETE FROM ocorrencias WHERE empresa_id=?', (self.empresa_id,))
        self.v1 = self.sql("SELECT id FROM veiculos WHERE placa='ABC1D23'")[0][0]
        self.v2 = self.sql("SELECT id FROM veiculos WHERE placa='DEF4G56'")[0][0]

    def inserir(self, data_abertura, tipo='mecânica', veiculo=None, status='aberta'):
        return self.sql(
            """INSERT INTO ocorrencias (empresa_id, veiculo_id, tipo_veiculo, tipo_problema, status, data_abertura, endereco)
               VALUES (?,?,?,?,?,?,?) RETURNING id""",
            (self.empresa_id, veiculo or self.v1, 'pesado', tipo, status, data_abertura, 'X'),
        )[0][0]

    def ids(self, query):
        r = self.get('/api/ocorrencias' + query, self.h)
        self.assertEqual(r.status_code, 200, r.get_json())
        return {oc['id'] for oc in r.get_json()['ocorrencias']}


class TestIntervaloDeDatas(FiltroDatasTestCase):
    def test_limites_incluem_dia_inicial_e_final_inteiros(self):
        antes = self.inserir('2026-03-09 23:59:59')
        inicio = self.inserir('2026-03-10 00:00:00')
        meio = self.inserir('2026-03-12 13:00:00')
        fim = self.inserir('2026-03-15 23:59:59')
        depois = self.inserir('2026-03-16 00:00:00')
        got = self.ids('?data_inicio=2026-03-10&data_fim=2026-03-15')
        self.assertEqual(got, {inicio, meio, fim})
        self.assertNotIn(antes, got)
        self.assertNotIn(depois, got)

    def test_mesmo_dia(self):
        a = self.inserir('2026-03-10 08:00:00')
        self.inserir('2026-03-11 08:00:00')
        self.assertEqual(self.ids('?data_inicio=2026-03-10&data_fim=2026-03-10'), {a})

    def test_apenas_inicio_ou_apenas_fim(self):
        a = self.inserir('2026-01-01 10:00:00')
        b = self.inserir('2026-06-01 10:00:00')
        self.assertEqual(self.ids('?data_inicio=2026-03-01'), {b})
        self.assertEqual(self.ids('?data_fim=2026-03-01'), {a})

    def test_inicio_maior_que_fim_422(self):
        r = self.get('/api/ocorrencias?data_inicio=2026-03-15&data_fim=2026-03-10', self.h)
        self.assertEqual(r.status_code, 422)
        self.assertIn('anterior ou igual', r.get_json()['erro'])

    def test_datas_invalidas_422(self):
        for valor in ['10/03/2026', '2026-02-30', '2026-3-1', 'ontem', "2026-03-01' OR 1=1 --"]:
            r = self.get(f'/api/ocorrencias?data_inicio={valor}', self.h)
            self.assertEqual(r.status_code, 422, valor)

    def test_combina_com_tipo_e_veiculo(self):
        alvo = self.inserir('2026-03-12 10:00:00', tipo='elétrica', veiculo=self.v2)
        self.inserir('2026-03-12 10:00:00', tipo='mecânica', veiculo=self.v2)
        self.inserir('2026-03-12 10:00:00', tipo='elétrica', veiculo=self.v1)
        self.inserir('2026-04-12 10:00:00', tipo='elétrica', veiculo=self.v2)
        q = f'?data_inicio=2026-03-01&data_fim=2026-03-31&tipo=elétrica&veiculo={self.v2}'
        self.assertEqual(self.ids(q), {alvo})

    def test_atalhos_7_30_90_no_fuso_de_sao_paulo(self):
        agora = agora_sao_paulo().replace(tzinfo=None, microsecond=0)
        fmt = '%Y-%m-%d %H:%M:%S'
        recente = self.inserir((agora - timedelta(days=6)).strftime(fmt))
        mes = self.inserir((agora - timedelta(days=20)).strftime(fmt))
        trimestre = self.inserir((agora - timedelta(days=80)).strftime(fmt))
        antiga = self.inserir((agora - timedelta(days=200)).strftime(fmt))
        self.assertEqual(self.ids('?periodo=7d'), {recente})
        self.assertEqual(self.ids('?periodo=30d'), {recente, mes})
        self.assertEqual(self.ids('?periodo=90d'), {recente, mes, trimestre})
        self.assertEqual(self.ids(''), {recente, mes, trimestre, antiga})

    def test_ocorrencia_de_ha_poucas_horas_entra_em_7d(self):
        agora = agora_sao_paulo().replace(tzinfo=None, microsecond=0)
        a = self.inserir((agora - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertIn(a, self.ids('?periodo=7d'))

    def test_intervalo_tem_prioridade_sobre_atalho(self):
        a = self.inserir('2020-05-05 10:00:00')
        r = self.get('/api/ocorrencias?periodo=7d&data_inicio=2020-05-01&data_fim=2020-05-31', self.h)
        self.assertEqual({oc['id'] for oc in r.get_json()['ocorrencias']}, {a})
        self.assertEqual(r.get_json()['filtros']['periodo'], '')


class TestRelatorioComDatas(FiltroDatasTestCase):
    def test_relatorio_respeita_intervalo(self):
        self.inserir('2026-03-10 10:00:00', tipo='elétrica')
        self.inserir('2026-03-11 10:00:00', tipo='elétrica', status='resolvido')
        self.inserir('2026-05-01 10:00:00', tipo='mecânica')
        r = self.get('/api/relatorios?data_inicio=2026-03-01&data_fim=2026-03-31', self.h)
        self.assertEqual(r.status_code, 200)
        d = r.get_json()
        self.assertEqual(d['total'], 2)
        self.assertEqual(d['abertas'], 1)
        self.assertEqual(d['encerradas'], 1)
        self.assertEqual({(x['tipo_problema'], x['c']) for x in d['por_tipo']}, {('elétrica', 2)})
        self.assertEqual(self.get('/api/relatorios', self.h).get_json()['total'], 3)

    def test_relatorio_valida_datas(self):
        self.assertEqual(self.get('/api/relatorios?data_inicio=2026-03-31&data_fim=2026-03-01', self.h).status_code, 422)
        self.assertEqual(self.get('/api/relatorios?periodo=1ano', self.h).status_code, 422)

    def test_por_mes_ordenado_do_mais_recente(self):
        for d in ['2026-01-10 10:00:00', '2026-03-10 10:00:00', '2026-02-10 10:00:00']:
            self.inserir(d)
        meses = [m['mes'] for m in self.get('/api/relatorios', self.h).get_json()['por_mes']]
        self.assertEqual(meses, ['03/2026', '02/2026', '01/2026'])


class TestConsistenciaSqlBancoCodigo(FixTruckTestCase):
    MODELOS = {'empresas': Empresa, 'motoristas': Motorista, 'veiculos': Veiculo,
               'oficinas': Oficina, 'ocorrencias': Ocorrencia, 'favoritos': Favorito}

    def colunas_banco(self, tabela):
        conn = sqlite3.connect(self.db_path)
        try:
            return {r[1]: {'notnull': bool(r[3]), 'pk': bool(r[5])}
                    for r in conn.execute(f'PRAGMA table_info({tabela})')}
        finally:
            conn.close()

    def test_models_tem_as_mesmas_colunas_do_banco(self):
        for tabela, modelo in self.MODELOS.items():
            self.assertEqual(modelo.__tablename__, tabela)
            no_model = {c.name for c in modelo.__table__.columns}
            self.assertEqual(no_model, set(self.colunas_banco(tabela)), tabela)

    def test_not_null_do_banco_refletido_nos_models(self):
        for tabela, modelo in self.MODELOS.items():
            banco = self.colunas_banco(tabela)
            for col in modelo.__table__.columns:
                if banco[col.name]['pk']:
                    continue
                self.assertEqual(not col.nullable, banco[col.name]['notnull'], f'{tabela}.{col.name}')

    def test_toda_tabela_do_script_existe_e_nada_sobra_alem_de_legado(self):
        conn = sqlite3.connect(self.db_path)
        existentes = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        conn.close()
        self.assertEqual(existentes, set(migracoes.tabelas_do_script()))

    def test_enums_do_sql_iguais_as_constantes(self):
        script = migracoes.ler_script()

        def valores_check(coluna):
            listas = re.findall(coluna + r" IN \(([^)]*)\)", script)
            return [set(re.findall(r"'([^']*)'", lista)) for lista in listas]

        for lista in valores_check('tipo_problema'):
            self.assertEqual(lista, set(constantes.TIPOS_PROBLEMA))
        for lista in valores_check('tipo_veiculo'):
            self.assertEqual(lista, set(constantes.TIPOS_VEICULO))
        self.assertEqual(len(valores_check('tipo_veiculo')), 2)

    def test_tipos_de_problema_do_seed_estao_no_enum(self):
        import seed_dados
        for oc in seed_dados.OCORRENCIAS_DEMO:
            self.assertIn(oc['tipo_problema'], constantes.TIPOS_PROBLEMA)
        for of in seed_dados.OFICINAS:
            for esp in of['especialidades']:
                self.assertIn(esp, constantes.ESPECIALIDADES_OFICINA, of['nome'])
            for tv in of['tipos_veiculo']:
                self.assertIn(tv, constantes.TIPOS_VEICULO, of['nome'])

    def test_placas_do_seed_validas(self):
        import seed_dados
        import validacoes
        for v in seed_dados.VEICULOS_DEMO:
            self.assertEqual(validacoes.placa(v['placa']), v['placa'])


if __name__ == '__main__':
    unittest.main()
