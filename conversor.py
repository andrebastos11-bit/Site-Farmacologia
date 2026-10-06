import pandas as pd
import json
import os

def converter_excel_para_json(excel_path='medicamentos.xlsx', json_path='medicamentos.json'):
    if not os.path.exists(excel_path):
        print(f"Erro: O ficheiro '{excel_path}' não foi encontrado.")
        return

    print("A ler o ficheiro Excel...")
    # header=0 ignora a primeira linha como cabeçalho
    df = pd.read_excel(excel_path, header=0)

    # Forçar a leitura apenas das primeiras 22 colunas (A até V) e ignorar o resto
    df = df.iloc[:, :22]

    # As 22 chaves exatas correspondentes de A a V
    chaves_base = [
        'nome_medicamento', 'substancia_ativa', 'forma_farmaceutica', 'dosagem',
        'indicacao_terapeutica', 'posologia', 'contra_indicacoes', 'advertencias',
        'interacoes', 'gravidez_aleitamento', 'conducao_maquinas', 'efeitos_indesejaveis',
        'sobredosagem', 'grupo_farmacoterapeutico', 'grupo_atc', 'propriedades_farmacodinamicas',
        'alvo_terapeutico', 'propriedades_farmacocineticas', 'excipientes', 'incompatibilidades',
        'conservacao', 'instrucoes_utilizacao'
    ]

    # Atribuir as chaves por ordem estricta às colunas do Excel
    colunas_mapeadas = {}
    for i, col_name in enumerate(df.columns):
        if i < len(chaves_base):
            colunas_mapeadas[col_name] = chaves_base[i]

    df = df.rename(columns=colunas_mapeadas)
    
    # Substituir valores nulos/NaN por strings vazias
    df = df.fillna("")

    # Converter para dicionário e guardar em JSON
    dados = df.to_dict(orient='records')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {len(dados)} medicamentos exportados para '{json_path}' sem colunas extras.")

if __name__ == '__main__':
    converter_excel_parser = converter_excel_para_json()