import pandas as pd
import json
import os

def converter_excel_para_json(excel_path='medicamentos.xlsx', json_path='medicamentos.json'):
    if not os.path.exists(excel_path):
        print(f"Erro: O ficheiro '{excel_path}' não foi encontrado na pasta.")
        return

    print("A ler o ficheiro Excel...")
    # Ler o Excel usando a primeira linha como cabeçalho (header=0)
    df = pd.read_excel(excel_path, header=0)

    # Remover espaços em branco à volta dos nomes das colunas originais do Excel
    df.columns = [str(c).strip() for c in df.columns]

    # Mapeamento estrito das 22 colunas do seu Excel para chaves limpas em minúsculas
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

    # Renomear as colunas
    df = df.rename(columns=mapeamento)
    
    # Substituir valores nulos/NaN por strings vazias
    df = df.fillna("")

    # Converter para dicionário de registos
    dados = df.to_dict(orient='records')
    
    # Guardar no ficheiro JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {len(dados)} medicamentos convertidos e guardados em '{json_path}'.")

if __name__ == '__main__':
    converter_excel_para_json()