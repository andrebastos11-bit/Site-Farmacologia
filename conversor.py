import pandas as pd
import json
import os

def converter():
    df = pd.read_excel('medicamentos.xlsx', header=0)
    df.columns = [str(c).strip() for c in df.columns]
    
    mapeamento = {
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
        'Grupo ATC': 'grupo_atc',
        'Propriedades farmacodinâmicas': 'propriedades_farmacodinamicas',
        'Alvo terapêutico': 'alvo_terapeutico',
        'Propriedades farmacocinéticas': 'propriedades_farmacocineticas',
        'Lista dos excipientes': 'excipientes',
        'Incompatibilidades': 'incompatibilidades',
        'Precauções especiais de conservação': 'conservacao',
        'Instruções de utilização e manipulação': 'instrucoes_utilizacao'
    }
    
    df = df.rename(columns=mapeamento)
    df = df.fillna("")
    dados = df.to_dict(orient='records')
    
    with open('medicamentos.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    print(f"Convertidos {len(dados)} medicamentos com sucesso para 'medicamentos.json'!")

if __name__ == '__main__':
    converter()