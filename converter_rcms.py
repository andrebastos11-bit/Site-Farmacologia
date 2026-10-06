import pandas as pd
import json
import os

FICHEIRO_EXCEL = "medicamentos.xlsx.xlsx"  # Ajusta se o nome no teu PC for apenas medicamentos.xlsx

if os.path.exists(FICHEIRO_EXCEL):
    df = pd.read_excel(FICHEIRO_EXCEL)
    lista_medicamentos = []
    
    # Ignora a primeira linha se for o cabeçalho descritivo
    for _, row in df.iloc[1:].iterrows():
        nome_med = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else "Desconhecido"
        if nome_med == "Desconhecido" or nome_med == "Nome do medicamento":
            continue
            
        # Gera o ID automaticamente a partir do nome
        id_gerado = nome_med.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_").replace("+", "_")
        
        medicamento = {
            "id": id_gerado,
            "nome": nome_med,
            "atc": str(row.iloc[21]).strip().upper() if pd.notna(row.iloc[21]) else "",
            "grupo": str(row.iloc[20]).strip().upper() if pd.notna(row.iloc[20]) else "",
            "classe": str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else "",
            "alvoPrincipal": str(row.iloc[23]).strip() if pd.len > 23 and pd.notna(row.iloc[23]) else "",
            "produtos": [
                {
                    "nome": nome_med,
                    "apresentacao": f"{str(row.iloc[3])} - {str(row.iloc[4])}" if pd.notna(row.iloc[4]) else str(row.iloc[3]),
                    "cnp": ""
                }
            ],
            "aba_clinica": {
                "indicacoes": [str(row.iloc[5])] if pd.notna(row.iloc[5]) else [],
                "posologia": str(row.iloc[6]) if pd.notna(row.iloc[6]) else "",
                "contra_indicacoes": str(row.iloc[7]) if pd.notna(row.iloc[7]) else "",
                "advertencias": str(row.iloc[8]) if pd.notna(row.iloc[8]) else "",
                "interaccoes": str(row.iloc[9]) if pd.notna(row.iloc[9]) else "",
                "gravidez": str(row.iloc[10]) if pd.notna(row.iloc[10]) else "",
                "efeitos_indesejaveis": str(row.iloc[12]) if pd.notna(row.iloc[12]) else "",
                "sobredosagem": str(row.iloc[13]) if pd.notna(row.iloc[13]) else ""
            },
            "aba_farmacologia": {
                "mecanismo": str(row.iloc[22]) if pd.notna(row.iloc[22]) else "",
                "cinetica": str(row.iloc[24]) if pd.notna(row.iloc[24]) else ""
            },
            "videos": {
                "dinamica": "",
                "cinetica": ""
            }
        }
        lista_medicamentos.append(medicamento)

    with open("medicamentos.json", "w", encoding="utf-8") as f:
        json.dump(lista_medicamentos, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {len(lista_medicamentos)} medicamentos convertidos para o site.")
else:
    print(f"Ficheiro '{FICHEIRO_EXCEL}' não encontrado.")