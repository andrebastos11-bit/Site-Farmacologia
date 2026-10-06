import os
import json
import re
from pypdf import PdfReader

# Caminho para a pasta onde tens os PDFs dos RCMs guardados
PASTA_PDFS = "./rcms"  # Altera para o nome real da tua pasta se necessário

def extrair_texto_pdf(caminho_pdf):
    try:
        leitor = PdfReader(caminho_pdf)
        texto_total = ""
        for pagina in leitor.pages:
            texto_total += pagina.extract_text() + "\n"
        return texto_total
    except Exception as e:
        print(f"Erro ao ler o PDF {caminho_pdf}: {e}")
        return ""

def extrair_subtopicos(texto_seccao):
    if not texto_seccao or texto_seccao == "Não especificado":
        return texto_seccao
    
    # Divide o texto com base no padrão de sub-tópicos iniciados por '-'
    partes = re.split(r'\n-\s*', "\n" + texto_seccao)
    if len(partes) <= 1:
        return texto_seccao.strip()
        
    subtopicos = {}
    for parte in partes[1:]:
        linhas = parte.strip().split('\n', 1)
        if len(linhas) == 2:
            sub_titulo, sub_conteudo = linhas
            chave = sub_titulo.replace(":", "").strip()
            subtopicos[chave] = sub_conteudo.strip()
        elif len(linhas) == 1 and ":" in linhas[0]:
            elementos = linhas[0].split(":", 1)
            subtopicos[elementos[0].strip()] = elementos[1].strip()
            
    return subtopicos if subtopicos else texto_seccao.strip()

def processar_texto_rcm(texto, nome_ficheiro):
    def extrair_seccao(titulo_inicio, titulo_fim):
        # Torna o padrão mais flexível para apanhar variações de formatação
        padrao = rf"{titulo_inicio}(.*?)(?={titulo_fim}|$)"
        match = re.search(padrao, texto, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else "Não especificado"

    # Tentar extrair o código ATC do texto
    match_atc = re.search(r"\b([A-Z]\d{2}[A-Z]{2}\d{2}|[A-Z]\d{2}[A-Z]{2}|[A-Z]\d{2}[A-Z]|\b[A-Z]\d{2})\b", texto)
    codigo_atc = match_atc.group(1).upper() if match_atc else "A01AA01"
    
    # Extração das secções principais do RCM
    nome_med = extrair_seccao(r"1\.\s*NOME\s*DO\s*MEDICAMENTO", r"2\.\s*COMPOSIÇÃO")
    if nome_med == "Não especificado":
        nome_med = nome_ficheiro.replace(".pdf", "")

    indicacoes = extrair_seccao(r"4\.1\s*Indicações\s*terapêuticas", r"4\.2\s*Posologia")
    posologia = extrair_seccao(r"4\.2\s*Posologia\s*e\s*modo\s*de\s*administração", r"4\.3\s*Contra-indicações")
    contra_indicacoes = extrair_seccao(r"4\.3\s*Contra-indicações", r"4\.4\s*Advertências")
    advertencias = extrair_seccao(r"4\.4\s*Advertências\s*e\s*precauções", r"4\.5\s*Interacções")
    interaccoes = extrair_seccao(r"4\.5\s*Interacções\s*medicamentosas", r"4\.6\s*Gravidez")
    gravidez = extrair_seccao(r"4\.6\s*Gravidez\s*e\s*aleitamento", r"4\.7\s*Efeitos\s*sobre")
    efeitos_indesejaveis = extrair_seccao(r"4\.8\s*Efeitos\s*indesejáveis", r"4\.9\s*Sobredosagem")
    
    texto_sobredosagem = extrair_seccao(r"4\.9\s*Sobredosagem", r"5\.\s*PROPRIEDADES")
    sobredosagem_estruturada = extrair_subtopicos(texto_sobredosagem)

    mecanismo = extrair_seccao(r"5\.1\s*Propriedades\s*farmacodinâmicas", r"5\.2\s*Propriedades\s*farmacocinéticas")
    cinetica = extrair_seccao(r"5\.2\s*Propriedades\s*farmacocinéticas", r"5\.3\s*Dados\s*de\s*segurança")

    primeira_linha_nome = nome_med.split("\n")[0] if nome_med else nome_ficheiro

    medicamento = {
        "id": nome_ficheiro.replace(".pdf", "").lower().replace(" ", "_"),
        "nome": primeira_linha_nome,
        "atc": codigo_atc,
        "grupo": codigo_atc[0] if codigo_atc else "A",
        "classe": "Medicamento Humano",
        "alvoPrincipal": "Consultar RCM",
        "produtos": [
            {
                "nome": primeira_linha_nome,
                "apresentacao": "Apresentação padrão",
                "cnp": ""
            }
        ],
        "aba_clinica": {
            "indicacoes": [indicacoes] if indicacoes != "Não especificado" else [],
            "posologia": posologia,
            "contra_indicacoes": contra_indicacoes,
            "advertencias": advertencias,
            "interaccoes": interaccoes,
            "gravidez": gravidez,
            "efeitos_indesejaveis": efeitos_indesejaveis,
            "sobredosagem": sobredosagem_estruturada
        },
        "aba_farmacologia": {
            "mecanismo": mecanismo,
            "cinetica": cinetica
        },
        "videos": {
            "dinamica": "",
            "cinetica": ""
        }
    }
    return medicamento

lista_medicamentos = []

if os.path.exists(PASTA_PDFS):
    for ficheiro in os.listdir(PASTA_PDFS):
        if ficheiro.endswith(".pdf"):
            caminho_completo = os.path.join(PASTA_PDFS, ficheiro)
            print(f"A processar: {ficheiro}...")
            texto_pdf = extrair_texto_pdf(caminho_completo)
            dados_med = processar_texto_rcm(texto_pdf, ficheiro)
            lista_medicamentos.append(dados_med)

    with open("medicamentos.json", "w", encoding="utf-8") as f:
        json.dump(lista_medicamentos, f, ensure_ascii=False, indent=4)
        
    print(f"\nSucesso! {len(lista_medicamentos)} PDFs processados e convertidos para medicamentos.json.")
else:
    print(f"A pasta '{PASTA_PDFS}' não foi encontrada.")