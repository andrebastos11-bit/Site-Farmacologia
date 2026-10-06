import pandas as pd
import json
import os

FICHEIRO_EXCEL = "medicamentos.xlsx"

if os.path.exists(FICHEIRO_EXCEL):
    df = pd.read_excel(FICHEIRO_EXCEL)
    lista_medicamentos = []
    
    for _, row in df.iloc[1:].iterrows():
        nome_med = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else "Desconhecido"
        if nome_med == "Desconhecido" or nome_med == "Nome do medicamento" or nome_med == "nan":
            continue
            
        id_gerado = nome_med.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_").replace("+", "_").replace(",", "")
        
        def get_val(idx):
            try:
                val = row.iloc[idx]
                return str(val).strip() if pd.notna(val) else ""
            except:
                return ""

        medicamento = {
            "id": id_gerado,
            "nome": nome_med,
            "atc": get_val(21).upper(),
            "grupo": get_val(20).upper(),
            "classe": get_val(3),
            "alvoPrincipal": get_val(23),
            "produtos": [
                {
                    "nome": nome_med,
                    "apresentacao": f"{get_val(3)} - {get_val(4)}" if get_val(4) else get_val(3),
                    "cnp": ""
                }
            ],
            "aba_clinica": {
                "indicacoes": [get_val(5)] if get_val(5) else [],
                "posologia": get_val(6),
                "contra_indicacoes": get_val(7),
                "advertencias": get_val(8),
                "interaccoes": get_val(9),
                "gravidez": get_val(10),
                "efeitos_indesejaveis": get_val(12),
                "sobredosagem": get_val(13)
            },
            "aba_farmacologia": {
                "mecanismo": get_val(22),
                "cinetica": get_val(24)
            },
            "videos": {
                "dinamica": "",
                "cinetica": ""
            }
        }
        lista_medicamentos.append(medicamento)

    with open("medicamentos.json", "w", encoding="utf-8") as f:
        json.dump(lista_medicamentos, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {len(lista_medicamentos)} medicamentos convertidos do Excel.")
else:
    print(f"Ficheiro '{FICHEIRO_EXCEL}' não encontrado.")