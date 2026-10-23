"""Dados fictícios de demonstração usados por seed.py.

Todas as oficinas, telefones e endereços são FICTÍCIOS (coordenadas aproximadas das cidades/rodovias
citadas). A chave de idempotência de uma oficina é (nome, endereco).
"""

COMERCIAL = {
    'seg': '08:00-18:00', 'ter': '08:00-18:00', 'qua': '08:00-18:00', 'qui': '08:00-18:00',
    'sex': '08:00-18:00', 'sab': '08:00-12:00', 'dom': None,
}
ESTENDIDO = {
    'seg': '06:00-22:00', 'ter': '06:00-22:00', 'qua': '06:00-22:00', 'qui': '06:00-22:00',
    'sex': '06:00-22:00', 'sab': '06:00-22:00', 'dom': '08:00-14:00',
}
DIAS_UTEIS = {
    'seg': '07:30-17:30', 'ter': '07:30-17:30', 'qua': '07:30-17:30', 'qui': '07:30-17:30',
    'sex': '07:30-17:30', 'sab': None, 'dom': None,
}
NOTURNO = {dia: '18:00-06:00' for dia in ('seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom')}
H24 = None  # aberta_24h = 1

TODOS = ['leve', 'médio', 'pesado']
MP = ['médio', 'pesado']
LM = ['leve', 'médio']
P = ['pesado']

MEC = 'mecânica'
ELE = 'elétrica'
HID = 'hidráulica'
BOR = 'borracharia'


def _of(nome, endereco, cidade, uf, telefone, lat, lon, especialidades, tipos, guincho, horarios):
    return {
        'nome': nome, 'endereco': endereco, 'cidade': cidade, 'uf': uf, 'telefone': telefone,
        'lat': lat, 'lon': lon, 'especialidades': especialidades, 'tipos_veiculo': tipos,
        'tem_guincho': 1 if guincho else 0,
        'aberta_24h': 1 if horarios is H24 else 0,
        'horarios': horarios,
    }


OFICINAS = [
    # --- Grande São Paulo (8 originais do projeto) ---
    _of('Auto Mecânica Silva', 'Av. Paulista, 1000 - SP', 'São Paulo', 'SP', '(11) 99001-1111',
        -23.5613, -46.6558, [MEC, ELE], TODOS, True, COMERCIAL),
    _of('Borracharia Rápida BR', 'Rod. Anhanguera KM 45', 'São Paulo', 'SP', '(11) 98002-2222',
        -23.5200, -46.6300, [BOR], TODOS, True, ESTENDIDO),
    _of('Elétrica Diesel Master', 'Av. dos Caminhoneiros, 500', 'São Paulo', 'SP', '(11) 97003-3333',
        -23.5900, -46.6100, [ELE, MEC], MP, False, DIAS_UTEIS),
    _of('Hidráulica & Freios SP', 'Rua das Indústrias, 200', 'São Paulo', 'SP', '(11) 96004-4444',
        -23.5500, -46.6800, [HID], P, True, COMERCIAL),
    _of('Oficina do Zé Mecânico', 'Estrada Velha, KM 12', 'São Paulo', 'SP', '(11) 95005-5555',
        -23.5750, -46.6400, [MEC], LM, False, COMERCIAL),
    _of('Truck Center Premium', 'Av. Industrial, 1500', 'São Paulo', 'SP', '(11) 94006-6666',
        -23.5450, -46.6650, [MEC, ELE, HID, BOR], TODOS, True, H24),
    _of('Mecânica Rodo Sul', 'Rod. Castelo Branco KM 30', 'São Paulo', 'SP', '(11) 93007-7777',
        -23.6000, -46.6200, [MEC, ELE], P, True, ESTENDIDO),
    _of('Auto Peças & Serviços', 'Rua das Oficinas, 88', 'São Paulo', 'SP', '(11) 92008-8888',
        -23.5350, -46.6900, [MEC, BOR], LM, False, COMERCIAL),

    # --- Grande São Paulo (novas) ---
    _of('Guarulhos Pesados', 'Rod. Presidente Dutra, Km 225 - Cumbica', 'Guarulhos', 'SP', '(11) 2400-1010',
        -23.4538, -46.5333, [MEC, ELE, HID], MP, True, H24),
    _of('Osasco Auto Elétrica', 'Av. dos Autonomistas, 3100 - Centro', 'Osasco', 'SP', '(11) 3600-2020',
        -23.5329, -46.7917, [ELE], TODOS, False, COMERCIAL),
    _of('Anchieta Truck Center', 'Via Anchieta, Km 18 - Rudge Ramos', 'São Bernardo do Campo', 'SP',
        '(11) 4300-3030', -23.6914, -46.5646, [MEC, HID, BOR], P, True, ESTENDIDO),
    _of('Castelo Diesel Barueri', 'Rod. Castelo Branco, Km 26 - Jardim Belval', 'Barueri', 'SP',
        '(11) 4100-4040', -23.5057, -46.8790, [MEC, ELE], MP, False, DIAS_UTEIS),
    _of('Cajamar Borracharia 24h', 'Rod. Anhanguera, Km 38 - Polvilho', 'Cajamar', 'SP', '(11) 4400-5050',
        -23.3550, -46.8770, [BOR], TODOS, True, H24),
    _of('Mauá Hidráulica Pesada', 'Av. Barão de Mauá, 4500 - Jardim Zaíra', 'Mauá', 'SP', '(11) 4500-6060',
        -23.6677, -46.4613, [HID, MEC], P, False, COMERCIAL),

    # --- Minas Gerais ---
    _of('Diesel Forte Juiz de Fora', 'BR-040, Km 768 - Benfica', 'Juiz de Fora', 'MG', '(32) 3200-0101',
        -21.6965, -43.4300, [MEC, ELE, HID], MP, True, H24),
    _of('Mecânica Mariano Procópio', 'Rua Bernardo Mascarenhas, 1200 - Fábrica', 'Juiz de Fora', 'MG',
        '(32) 3200-0202', -21.7480, -43.3570, [MEC], TODOS, False, COMERCIAL),
    _of('Borracharia Trevo BR-267', 'BR-267, Km 2 - Distrito Industrial', 'Juiz de Fora', 'MG',
        '(32) 3200-0303', -21.6800, -43.4100, [BOR], TODOS, True, ESTENDIDO),
    _of('Truck Service Anel BH', 'Anel Rodoviário, Km 15 - Califórnia', 'Belo Horizonte', 'MG',
        '(31) 3300-0404', -19.8700, -43.9900, [MEC, ELE, HID, BOR], TODOS, True, H24),
    _of('Elétrica Diesel Contagem', 'Av. das Américas, 800 - Cidade Industrial', 'Contagem', 'MG',
        '(31) 3300-0505', -19.9320, -44.0539, [ELE], MP, False, DIAS_UTEIS),
    _of('Betim Pesados Mecânica', 'Rod. Fernão Dias, Km 492 - Jardim Piemonte', 'Betim', 'MG',
        '(31) 3300-0606', -19.9678, -44.1983, [MEC, HID], P, True, COMERCIAL),
    _of('Triângulo Truck Center', 'BR-050, Km 72 - Distrito Industrial', 'Uberlândia', 'MG',
        '(34) 3400-0707', -18.9186, -48.2772, [MEC, ELE, BOR], MP, True, ESTENDIDO),
    _of('Norte de Minas Diesel', 'Av. Deputado Plínio Ribeiro, 2500', 'Montes Claros', 'MG',
        '(38) 3800-0808', -16.7350, -43.8617, [MEC, ELE], TODOS, False, COMERCIAL),
    _of('Vale do Rio Doce Borracharia', 'BR-116, Km 410 - Vila Isa', 'Governador Valadares', 'MG',
        '(33) 3300-0909', -18.8545, -41.9555, [BOR, MEC], TODOS, False, NOTURNO),

    # --- Rio de Janeiro ---
    _of('Oficina Av. Brasil Diesel', 'Av. Brasil, 22000 - Irajá', 'Rio de Janeiro', 'RJ', '(21) 2100-1111',
        -22.8580, -43.2700, [MEC, ELE, HID], MP, True, H24),
    _of('Caxias Truck Service', 'Rod. Washington Luiz, Km 104 - Jardim Primavera', 'Duque de Caxias', 'RJ',
        '(21) 2100-2222', -22.7700, -43.3000, [MEC, BOR], TODOS, True, ESTENDIDO),
    _of('Dutra Mecânica Pesada', 'Rod. Presidente Dutra, Km 177 - Posse', 'Nova Iguaçu', 'RJ',
        '(21) 2100-3333', -22.7592, -43.4511, [MEC, HID], P, False, COMERCIAL),
    _of('Resende Diesel Dutra', 'Rod. Presidente Dutra, Km 306 - Paraíso', 'Resende', 'RJ', '(24) 3300-4444',
        -22.4690, -44.4469, [MEC, ELE], MP, True, ESTENDIDO),
    _of('Elétrica Aço Volta Redonda', 'Av. dos Trabalhadores, 900 - Vila Santa Cecília', 'Volta Redonda',
        'RJ', '(24) 3300-5555', -22.5231, -44.1042, [ELE], TODOS, False, DIAS_UTEIS),
    _of('Serra Freios Petrópolis', 'BR-040, Km 70 - Bingen', 'Petrópolis', 'RJ', '(24) 2200-6666',
        -22.5050, -43.1780, [HID, MEC], MP, True, COMERCIAL),
    _of('Norte Fluminense Mecânica', 'BR-101, Km 65 - Parque Guarus', 'Campos dos Goytacazes', 'RJ',
        '(22) 2700-7777', -21.7545, -41.3244, [MEC, BOR], TODOS, False, COMERCIAL),

    # --- Sul ---
    _of('Contorno Sul Diesel', 'BR-116, Km 115 - Contorno Sul', 'Curitiba', 'PR', '(41) 3100-1212',
        -25.4950, -49.2300, [MEC, ELE, HID], P, True, H24),
    _of('SJP Elétrica Pesados', 'Av. Rui Barbosa, 5000 - Afonso Pena', 'São José dos Pinhais', 'PR',
        '(41) 3100-2323', -25.5350, -49.2060, [ELE], MP, False, COMERCIAL),
    _of('Campos Gerais Truck', 'BR-376, Km 500 - Uvaranas', 'Ponta Grossa', 'PR', '(42) 3200-3434',
        -25.0945, -50.1633, [MEC, BOR], TODOS, True, ESTENDIDO),
    _of('Joinville Mecânica Diesel', 'BR-101, Km 40 - Distrito Industrial', 'Joinville', 'SC',
        '(47) 3400-4545', -26.3045, -48.8487, [MEC, HID], MP, False, DIAS_UTEIS),
    _of('Porto Itajaí Borracharia', 'BR-101, Km 118 - Salseiros', 'Itajaí', 'SC', '(47) 3300-5656',
        -26.9078, -48.6619, [BOR], TODOS, True, H24),
    _of('Oeste Catarinense Pesados', 'BR-282, Km 540 - Efapi', 'Chapecó', 'SC', '(49) 3300-6767',
        -27.1004, -52.6152, [MEC, ELE], P, True, COMERCIAL),
    _of('Porto Alegre Diesel Service', 'BR-116, Km 270 - Sarandi', 'Porto Alegre', 'RS', '(51) 3300-7878',
        -29.9900, -51.1700, [MEC, ELE, HID, BOR], MP, True, ESTENDIDO),
    _of('Serra Gaúcha Freios', 'RS-122, Km 70 - Desvio Rizzo', 'Caxias do Sul', 'RS', '(54) 3200-8989',
        -29.1678, -51.1794, [HID], P, False, COMERCIAL),
    _of('Planalto Truck Passo Fundo', 'BR-285, Km 290 - São Cristóvão', 'Passo Fundo', 'RS',
        '(54) 3300-9090', -28.2620, -52.4064, [MEC, BOR], TODOS, False, DIAS_UTEIS),

    # --- Nordeste ---
    _of('Salvador 324 Diesel', 'BR-324, Km 618 - Porto Seco Pirajá', 'Salvador', 'BA', '(71) 3300-1313',
        -12.9200, -38.4400, [MEC, ELE], MP, True, ESTENDIDO),
    _of('Feira Truck Center', 'BR-116, Km 425 - Distrito de Humildes', 'Feira de Santana', 'BA',
        '(75) 3200-2424', -12.2664, -38.9663, [MEC, ELE, HID, BOR], TODOS, True, H24),
    _of('Conquista Pesados', 'BR-116, Km 830 - Jardim Valéria', 'Vitória da Conquista', 'BA',
        '(77) 3400-3535', -14.8615, -40.8442, [MEC, HID], P, False, COMERCIAL),
    _of('Recife Elétrica Diesel', 'BR-101, Km 70 - Curado', 'Recife', 'PE', '(81) 3300-4646',
        -8.1100, -34.9500, [ELE, MEC], MP, False, DIAS_UTEIS),
    _of('Jaboatão Borracharia', 'BR-232, Km 10 - Prazeres', 'Jaboatão dos Guararapes', 'PE',
        '(81) 3400-5757', -8.1803, -35.0016, [BOR], TODOS, True, NOTURNO),
    _of('Fortaleza Truck Service', 'BR-116, Km 8 - Messejana', 'Fortaleza', 'CE', '(85) 3200-6868',
        -3.7900, -38.5300, [MEC, ELE, BOR], TODOS, True, ESTENDIDO),
    _of('Vale do São Francisco Mecânica', 'BR-428, Km 2 - Areia Branca', 'Petrolina', 'PE',
        '(87) 3800-7979', -9.3891, -40.5030, [MEC], MP, False, COMERCIAL),
    _of('São Luís Diesel', 'BR-135, Km 5 - Tirirical', 'São Luís', 'MA', '(98) 3200-8080',
        -2.5307, -44.3068, [MEC, HID], P, True, COMERCIAL),

    # --- Centro-Oeste ---
    _of('Goiânia Pesados BR-153', 'BR-153, Km 3 - Jardim Guanabara', 'Goiânia', 'GO', '(62) 3200-1414',
        -16.6869, -49.2648, [MEC, ELE], MP, True, ESTENDIDO),
    _of('Anápolis Truck Center', 'BR-060, Km 95 - DAIA', 'Anápolis', 'GO', '(62) 3300-2525',
        -16.3281, -48.9530, [MEC, ELE, HID, BOR], TODOS, True, H24),
    _of('Brasília Diesel SIA', 'SIA Trecho 3, Lote 500', 'Brasília', 'DF', '(61) 3300-3636',
        -15.8000, -47.9500, [MEC, ELE], TODOS, False, COMERCIAL),
    _of('Cuiabá Mecânica Pesada', 'BR-364, Km 400 - Distrito Industrial', 'Cuiabá', 'MT', '(65) 3600-4747',
        -15.6014, -56.0979, [MEC, HID], P, True, COMERCIAL),
    _of('Rondonópolis Truck 24h', 'BR-163, Km 120 - Vila Operária', 'Rondonópolis', 'MT', '(66) 3400-5858',
        -16.4673, -54.6372, [MEC, ELE, BOR], MP, True, H24),
    _of('Campo Grande Elétrica Diesel', 'BR-163, Km 470 - Núcleo Industrial', 'Campo Grande', 'MS',
        '(67) 3300-6969', -20.4697, -54.6201, [ELE], MP, False, DIAS_UTEIS),
    _of('Dourados Borracharia', 'BR-163, Km 260 - Jardim Clímax', 'Dourados', 'MS', '(67) 3400-7070',
        -22.2211, -54.8056, [BOR, MEC], TODOS, False, ESTENDIDO),
]

EMPRESA_DEMO = {
    'nome': 'Transportadora Demo', 'email': 'demo@fixtruck.com', 'senha': '123456', 'qtd_caminhoes': 12,
}

# Acesso de demonstração: Carlos entra direto; José precisa trocar a senha no primeiro login.
MOTORISTAS_DEMO = [
    {'nome': 'Carlos Mendes', 'cnh': '12345678901', 'telefone': '(11) 99111-1111',
     'email': 'carlos@fixtruck.com', 'senha': 'motorista123', 'trocar_senha': 0},
    {'nome': 'José Ferreira', 'cnh': '98765432100', 'telefone': '(11) 99222-2222',
     'email': 'jose@fixtruck.com', 'senha': 'trocar123', 'trocar_senha': 1},
    {'nome': 'Ana Paula Souza', 'cnh': '45678912300', 'telefone': '(11) 99333-3333'},
]

# motorista = índice em MOTORISTAS_DEMO (ou None)
VEICULOS_DEMO = [
    {'placa': 'ABC1D23', 'modelo': 'Actros 2651', 'marca': 'Mercedes', 'tipo_veiculo': 'pesado', 'motorista': 0},
    {'placa': 'DEF4G56', 'modelo': 'FH 540', 'marca': 'Volvo', 'tipo_veiculo': 'pesado', 'motorista': 1},
    {'placa': 'GHI7J89', 'modelo': 'Delivery 9.170', 'marca': 'VW', 'tipo_veiculo': 'médio', 'motorista': 2},
    {'placa': 'JKL0M12', 'modelo': 'Daily 35S14', 'marca': 'Iveco', 'tipo_veiculo': 'leve', 'motorista': None},
]

# dias_atras: data de abertura relativa à data do seed; oficina = nome da oficina (ou None)
OCORRENCIAS_DEMO = [
    {'veiculo': 0, 'tipo_problema': 'mecânica', 'pane_total': 1, 'lat': '-23.5613', 'lon': '-46.6558',
     'endereco': 'Rodovia Anhanguera — KM 45 — São Paulo/SP', 'status': 'resolvido',
     'oficina': 'Truck Center Premium', 'dias_atras': 120, 'horas_ate_oficina': 1, 'horas_ate_fim': 5},
    {'veiculo': 1, 'tipo_problema': 'borracharia', 'pane_total': 0, 'lat': '-23.5200', 'lon': '-46.6300',
     'endereco': 'Av. Brasil, 500 — São Paulo/SP', 'status': 'resolvido',
     'oficina': 'Borracharia Rápida BR', 'dias_atras': 60, 'horas_ate_oficina': 1, 'horas_ate_fim': 2},
    {'veiculo': 2, 'tipo_problema': 'elétrica', 'pane_total': 0, 'lat': '-21.7480', 'lon': '-43.3570',
     'endereco': 'BR-040 — KM 773 — Juiz de Fora/MG', 'status': 'em_atendimento',
     'oficina': 'Diesel Forte Juiz de Fora', 'dias_atras': 20, 'horas_ate_oficina': 1, 'horas_ate_fim': None},
    {'veiculo': 0, 'tipo_problema': 'hidráulica', 'pane_total': 1, 'lat': '-22.8580', 'lon': '-43.2700',
     'endereco': 'Av. Brasil — Rio de Janeiro/RJ', 'status': 'aberta', 'registrada_por': 'motorista',
     'descricao': 'Vazamento de óleo no sistema de freio; caminhão parado no acostamento.',
     'oficina': None, 'dias_atras': 5, 'horas_ate_oficina': None, 'horas_ate_fim': None},
    {'veiculo': 3, 'tipo_problema': 'mecânica', 'pane_total': 0, 'lat': '-23.5500', 'lon': '-46.6800',
     'endereco': 'Centro — São Paulo/SP', 'status': 'aberta',
     'oficina': None, 'dias_atras': 1, 'horas_ate_oficina': None, 'horas_ate_fim': None},
]
