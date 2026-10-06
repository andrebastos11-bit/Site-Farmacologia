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
        
        # Função inteligente para procurar valores por nome de coluna ou índice seguro
        def get_val_by_name(col_name):
            try:
                for col in df.columns:
                    val_header = str(df.loc[0, col]).strip().lower()
                    if col_name.lower() in val_header:
                        val = row[col]
                        return str(val).strip() if pd.notna(val) else ""
                return ""
            except:
                return ""

        atc_val = get_val_by_name("Grupo ATC")
        grupo_val = get_val_by_name("Grupo Farmacoteraêutico")
        classe_val = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ""
        forma_val = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ""

        def get_val(idx):
            try:
                val = row.iloc[idx]
                return str(val).strip() if pd.notna(val) else ""
            except:
                return ""

        medicamento = {
            "id": id_gerado,
            "nome": nome_med,
            "atc": atc_val.upper(),
            "grupo": grupo_val.upper(),
            "classe": classe_val,
            "alvoPrincipal": get_val_by_name("Alvo terapêutico"),
            "produtos": [
                {
                    "nome": nome_med,
                    "apresentacao": f"{classe_val} - {forma_val}" if forma_val else classe_val,
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
                "mecanismo": get_val_by_name("farmacodinâmicas"),
                "cinetica": get_val_by_name("farmacocinéticas")
            },
            "videos": {
                "dinamica": "",
                "cinetica": ""
            }
        }
        lista_medicamentos.append(medicamento)

    with open("medicamentos.json", "w", encoding="utf-8") as f:
        json.dump(lista_medicamentos, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {len(lista_medicamentos)} medicamentos convertidos com ATC detetado.")
else:
    print(f"Ficheiro '{FICHEIRO_EXCEL}' não encontrado.")