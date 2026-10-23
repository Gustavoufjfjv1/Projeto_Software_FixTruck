"""Listas de valores aceitos pelo sistema (fonte única para API, formulários, seed e filtros)."""

TIPOS_PROBLEMA = ['mecânica', 'elétrica', 'hidráulica', 'borracharia', 'não identificado']

ROTULOS_TIPO_PROBLEMA = {
    'mecânica': 'Mecânica',
    'elétrica': 'Elétrica',
    'hidráulica': 'Hidráulica / Freios',
    'borracharia': 'Borracharia / Pneu',
    'não identificado': 'Não identificado',
}

# Especialidades que uma oficina pode declarar (todo tipo de problema, exceto "não identificado").
ESPECIALIDADES_OFICINA = [t for t in TIPOS_PROBLEMA if t != 'não identificado']

# Problema "não identificado" exige diagnóstico: atendido por oficinas de mecânica geral.
ESPECIALIDADE_PARA_NAO_IDENTIFICADO = 'mecânica'

TIPOS_VEICULO = ['leve', 'médio', 'pesado']

ROTULOS_TIPO_VEICULO = {
    'leve': 'Leve',
    'médio': 'Médio',
    'pesado': 'Pesado',
}

# Índice = datetime.weekday() (0 = segunda-feira).
DIAS_SEMANA = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']

ROTULOS_DIA_SEMANA = {
    'seg': 'Segunda', 'ter': 'Terça', 'qua': 'Quarta', 'qui': 'Quinta',
    'sex': 'Sexta', 'sab': 'Sábado', 'dom': 'Domingo',
}

UFS = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA',
    'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
]


def opcoes_publicas():
    return {
        'tipos_problema': [
            {'valor': t, 'rotulo': ROTULOS_TIPO_PROBLEMA[t]} for t in TIPOS_PROBLEMA
        ],
        'especialidades_oficina': [
            {'valor': t, 'rotulo': ROTULOS_TIPO_PROBLEMA[t]} for t in ESPECIALIDADES_OFICINA
        ],
        'tipos_veiculo': [
            {'valor': t, 'rotulo': ROTULOS_TIPO_VEICULO[t]} for t in TIPOS_VEICULO
        ],
        'dias_semana': [
            {'valor': d, 'rotulo': ROTULOS_DIA_SEMANA[d]} for d in DIAS_SEMANA
        ],
        'ufs': UFS,
    }
