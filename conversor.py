import json
import re
import sys

import pandas as pd

EXCEL = 'medicamentos.xlsx'
SAIDA = 'medicamentos.json'

MAPEAMENTO = {
    'Nome do medicamento': 'nome_medicamento',
    'Substância ativa': 'substancia_ativa',
    'Forma Farmacêutica': 'forma_farmaceutica',
    'Dosagem': 'dosagem',
    'Indicação terapêutica': 'indicacao_terapeutica',
    'Posologia e modo de administração': 'posologia',
    'Contra-indicações': 'contra_indicacoes',
    'Advertências e precauções especiais de utilização': 'advertencias',
    'Interacções medicamentosas e outras formas de interacção': 'interacoes',
    'Gravidez e aleitamento': 'gravidez_aleitamento',
    'Efeitos sobre a capacidade de conduzir e utilizar máquinas': 'conducao_maquinas',
    'Efeitos indesejáveis': 'efeitos_indesejaveis',
    'Sobredosagem': 'sobredosagem',
    'Grupo Farmacoteraêutico': 'grupo_farmacoterapeutico',
    'ATC': 'atc',
    'Propriedades farmacodinâmicas': 'propriedades_farmacodinamicas',
    'Alvo terapêutico': 'alvo_terapeutico',
    'Propriedades farmacocinéticas': 'propriedades_farmacocineticas',
    'Lista dos excipientes': 'excipientes',
    'Incompatibilidades': 'incompatibilidades',
    'Precauções especiais de conservação': 'conservacao',
    'Instruções de utilização e manipulação': 'instrucoes_utilizacao',
}

COLUNAS_NIVEIS = ['1º Nível', '2º Nível', '3º Nível', '4º Nível', '5º Nível']

# aceita "A02A - Antiácidos" e também "N02: Analgésicos"
PADRAO_NIVEL = re.compile(r'^([A-Z][0-9A-Z]*)\s*[-–:]\s*(.+)$')


def limpar(valor):
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ''
    return str(valor).replace('\xa0', ' ').strip()


def analisar_nivel(texto):
    """Devolve {'codigo','nome'} ou None se o nível não existir / for um marcador."""
    texto = limpar(texto)
    if not texto:
        return None
    if texto.startswith(('Sem ', 'A confirmar')):
        return None
    m = PADRAO_NIVEL.match(texto)
    if not m:
        return None
    return {'codigo': m.group(1), 'nome': m.group(2).strip()}


def converter():
    df = pd.read_excel(EXCEL, header=0)
    df.columns = [str(c).strip() for c in df.columns]

    em_falta = [c for c in COLUNAS_NIVEIS + ['ATC'] if c not in df.columns]
    if em_falta:
        sys.exit(f'Colunas em falta no Excel: {em_falta}')

    registos, avisos = [], []
    for i, linha in df.iterrows():
        reg = {}
        for original, novo in MAPEAMENTO.items():
            reg[novo] = limpar(linha.get(original, ''))

        niveis = [analisar_nivel(linha[c]) for c in COLUNAS_NIVEIS]
        # um nível só é válido se todos os anteriores existirem
        for k in range(1, 5):
            if niveis[k - 1] is None:
                niveis[k] = None
        reg['atc_niveis'] = niveis

        # coerência: o código de cada nível deve ser prefixo do código ATC
        atc = reg['atc']
        for k, n in enumerate(niveis):
            if n and atc and not atc.startswith(n['codigo']):
                avisos.append(f"Linha {i + 2} ({reg['nome_medicamento']}): nível {k + 1} "
                              f"'{n['codigo']}' não é prefixo de ATC '{atc}'")
        if not reg['nome_medicamento']:
            avisos.append(f'Linha {i + 2}: sem nome de medicamento')
        registos.append(reg)

    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(registos, f, ensure_ascii=False, indent=2)

    print(f"Convertidos {len(registos)} medicamentos para '{SAIDA}'.")
    if avisos:
        print(f'\n{len(avisos)} aviso(s):')
        for a in avisos:
            print(' -', a)


if __name__ == '__main__':
    converter()