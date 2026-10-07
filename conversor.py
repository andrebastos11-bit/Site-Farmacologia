import json
import re
import sys
import pandas as pd


EXCEL = "medicamentos.xlsx"
SAIDA = "medicamentos.json"


# =========================================================
# MAPEAMENTO EXCEL -> JSON
# =========================================================

MAPEAMENTO = {
    "numero_registo": "numero_registo",
    "Nome do medicamento": "nome_medicamento",
    "Substância ativa": "substancia_ativa",
    "Forma Farmacêutica": "forma_farmaceutica",
    "Dosagem": "dosagem",
    "Indicação terapêutica": "indicacao_terapeutica",
    "Posologia e modo de administração": "posologia",
    "Contra-indicações": "contra_indicacoes",
    "Advertências e precauções especiais de utilização": "advertencias",
    "Interacções medicamentosas e outras formas de interacção": "interacoes",
    "Gravidez e aleitamento": "gravidez_aleitamento",
    "Efeitos sobre a capacidade de conduzir e utilizar máquinas": "conducao_maquinas",
    "Efeitos indesejáveis": "efeitos_indesejaveis",
    "Sobredosagem": "sobredosagem",
    "Grupo Farmacoteraêutico": "grupo_farmacoterapeutico",
    "ATC": "atc",
    "Propriedades farmacodinâmicas": "propriedades_farmacodinamicas",
    "Alvo terapêutico": "alvo_terapeutico",
    "Propriedades farmacocinéticas": "propriedades_farmacocineticas",
    "Lista dos excipientes": "excipientes",
    "Incompatibilidades": "incompatibilidades",
    "Precauções especiais de conservação": "conservacao",
    "Instruções de utilização e manipulação": "instrucoes_utilizacao",

    # Imagem
    "foto": "foto",

    # Vídeos
    "video_farmacodinamica": "video_farmacodinamica",
    "video_farmacocinetica": "video_farmacocinetica",

    # Resumo do Trading Card
    "indicacao_resumida": "indicacao_resumida",
    "idade_minima": "idade_minima",

    # Informação farmacêutica adicional
    "composicao": "composicao",
    "descricao_forma_farmaceutica": "descricao_forma_farmaceutica",
}


# =========================================================
# COLUNAS DOS NÍVEIS ATC
# =========================================================

COLUNAS_NIVEIS = [
    "1º Nível",
    "2º Nível",
    "3º Nível",
    "4º Nível",
    "5º Nível"
]


PADRAO_NIVEL = re.compile(
    r"^([A-Z][0-9A-Z]*)\s*[-–:]\s*(.+)$"
)


# =========================================================
# LIMPEZA
# =========================================================

def limpar(valor):

    if valor is None:
        return ""

    if isinstance(valor, float) and pd.isna(valor):
        return ""

    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))

    valor = str(valor).replace("\xa0", " ").strip()

    if valor.endswith(".0") and valor[:-2].isdigit():
        valor = valor[:-2]

    return valor


# =========================================================
# ANALISAR NÍVEL ATC
# =========================================================

def analisar_nivel(texto):

    texto = limpar(texto)

    if not texto:
        return None

    if texto.startswith(("Sem ", "A confirmar")):
        return None

    resultado = PADRAO_NIVEL.match(texto)

    if not resultado:
        return None

    return {
        "codigo": resultado.group(1),
        "nome": resultado.group(2).strip()
    }


# =========================================================
# CONVERTER
# =========================================================

def converter():

    print(f"A ler '{EXCEL}'...")

    try:

        df = pd.read_excel(
            EXCEL,
            header=0,
            dtype=object
        )

    except FileNotFoundError:

        sys.exit(
            f"ERRO: Não foi encontrado '{EXCEL}'."
        )


    # Limpar nomes das colunas
    df.columns = [
        str(coluna).strip()
        for coluna in df.columns
    ]


    # =====================================================
    # COLUNAS OBRIGATÓRIAS
    # =====================================================

    colunas_obrigatorias = (
        [
            "numero_registo",
            "Nome do medicamento",
            "foto",
            "ATC"
        ]
        + COLUNAS_NIVEIS
    )


    em_falta = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]


    if em_falta:

        sys.exit(
            "ERRO - Colunas em falta no Excel: "
            + ", ".join(em_falta)
        )


    # =====================================================
    # COLUNAS OPCIONAIS
    # =====================================================

    colunas_opcionais = [
        "video_farmacodinamica",
        "video_farmacocinetica",
        "indicacao_resumida",
        "idade_minima",
        "composicao",
        "descricao_forma_farmaceutica"
    ]


    for coluna in colunas_opcionais:

        if coluna not in df.columns:

            print(
                f"AVISO: A coluna opcional "
                f"'{coluna}' não existe no Excel."
            )


    # =====================================================
    # REGISTOS
    # =====================================================

    registos = []
    avisos = []


    for indice, linha in df.iterrows():

        registo = {}


        # Dados principais
        for coluna_excel, campo_json in MAPEAMENTO.items():

            registo[campo_json] = limpar(
                linha.get(coluna_excel, "")
            )


        # =================================================
        # NÍVEIS ATC
        # =================================================

        niveis = [
            analisar_nivel(
                linha.get(coluna, "")
            )
            for coluna in COLUNAS_NIVEIS
        ]


        for k in range(1, 5):

            if niveis[k - 1] is None:
                niveis[k] = None


        registo["atc_niveis"] = niveis


        # =================================================
        # VERIFICAÇÃO ATC
        # =================================================

        atc = registo.get("atc", "")


        for k, nivel in enumerate(niveis):

            if (
                nivel
                and atc
                and not atc.startswith(
                    nivel["codigo"]
                )
            ):

                avisos.append(
                    f"Linha {indice + 2} "
                    f"({registo.get('nome_medicamento', '')}): "
                    f"nível {k + 1} '{nivel['codigo']}' "
                    f"não corresponde ao ATC '{atc}'"
                )


        # =================================================
        # VERIFICAÇÕES
        # =================================================

        if not registo.get("nome_medicamento"):

            avisos.append(
                f"Linha {indice + 2}: "
                "sem nome de medicamento"
            )


        if not registo.get("numero_registo"):

            avisos.append(
                f"Linha {indice + 2} "
                f"({registo.get('nome_medicamento', '')}): "
                "sem número de registo"
            )


        if not registo.get("foto"):

            avisos.append(
                f"Linha {indice + 2} "
                f"({registo.get('nome_medicamento', '')}): "
                "sem imagem"
            )


        # =================================================
        # VALIDAÇÃO DA IDADE MÍNIMA
        # =================================================

        idade = registo.get(
            "idade_minima",
            ""
        )


        if idade:

            if not idade.isdigit():

                avisos.append(
                    f"Linha {indice + 2} "
                    f"({registo.get('nome_medicamento', '')}): "
                    f"idade_minima '{idade}' não é um número inteiro."
                )


        registos.append(registo)


    # =====================================================
    # CRIAR JSON
    # =====================================================

    with open(
        SAIDA,
        "w",
        encoding="utf-8"
    ) as ficheiro:

        json.dump(
            registos,
            ficheiro,
            ensure_ascii=False,
            indent=2
        )


    # =====================================================
    # ESTATÍSTICAS
    # =====================================================

    total_farmacodinamica = sum(
        1
        for registo in registos
        if registo.get("video_farmacodinamica")
    )


    total_farmacocinetica = sum(
        1
        for registo in registos
        if registo.get("video_farmacocinetica")
    )


    total_indicacoes_resumidas = sum(
        1
        for registo in registos
        if registo.get("indicacao_resumida")
    )


    total_idades = sum(
        1
        for registo in registos
        if registo.get("idade_minima")
    )


    total_composicoes = sum(
        1
        for registo in registos
        if registo.get("composicao")
    )


    total_descricoes_forma = sum(
        1
        for registo in registos
        if registo.get("descricao_forma_farmaceutica")
    )


    print()

    print(
        f"SUCESSO: {len(registos)} medicamentos "
        f"convertidos para '{SAIDA}'."
    )

    print()

    print(
        f"Vídeos de farmacodinâmica: "
        f"{total_farmacodinamica}"
    )

    print(
        f"Vídeos de farmacocinética: "
        f"{total_farmacocinetica}"
    )

    print(
        f"Indicações resumidas: "
        f"{total_indicacoes_resumidas}"
    )

    print(
        f"Medicamentos com idade mínima: "
        f"{total_idades}"
    )

    print(
        f"Medicamentos com composição: "
        f"{total_composicoes}"
    )

    print(
        f"Medicamentos com descrição da forma farmacêutica: "
        f"{total_descricoes_forma}"
    )


    if avisos:

        print()
        print(f"{len(avisos)} aviso(s):")

        for aviso in avisos:
            print(" -", aviso)

    else:

        print()
        print(
            "Conversão concluída sem avisos."
        )


if __name__ == "__main__":
    converter()