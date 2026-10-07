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


# =========================================================
# PADRÃO DOS NÍVEIS ATC
# =========================================================

PADRAO_NIVEL = re.compile(
    r"^([A-Z][0-9A-Z]*)\s*[-–:]\s*(.+)$"
)


# =========================================================
# LIMPEZA DE VALORES
# =========================================================

def limpar(valor):
    """
    Limpa valores importados do Excel.

    - Converte células vazias em ""
    - Remove espaços desnecessários
    - Impede que números inteiros apareçam como 123456.0
    """

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
    """
    Exemplo:

    A01 - PREPARAÇÕES PARA USO ESTOMATOLÓGICO

    passa para:

    {
        "codigo": "A01",
        "nome": "PREPARAÇÕES PARA USO ESTOMATOLÓGICO"
    }
    """

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
# CONVERSÃO
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


    # =====================================================
    # LIMPAR NOMES DAS COLUNAS
    # =====================================================

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
    # VERIFICAR COLUNAS DE VÍDEO
    # =====================================================

    colunas_video = [
        "video_farmacodinamica",
        "video_farmacocinetica"
    ]


    for coluna in colunas_video:

        if coluna not in df.columns:

            print(
                f"AVISO: A coluna '{coluna}' "
                f"não existe no Excel."
            )


    # =====================================================
    # CRIAR REGISTOS
    # =====================================================

    registos = []
    avisos = []


    for indice, linha in df.iterrows():

        registo = {}


        # =================================================
        # DADOS PRINCIPAIS
        # =================================================

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


        # Um nível só pode existir
        # se o nível anterior existir

        for k in range(1, 5):

            if niveis[k - 1] is None:
                niveis[k] = None


        registo["atc_niveis"] = niveis


        # =================================================
        # VERIFICAÇÃO DO ATC
        # =================================================

        atc = registo.get(
            "atc",
            ""
        )


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
        # VERIFICAÇÃO DO NOME
        # =================================================

        if not registo.get(
            "nome_medicamento"
        ):

            avisos.append(
                f"Linha {indice + 2}: "
                f"sem nome de medicamento"
            )


        # =================================================
        # VERIFICAÇÃO DO NÚMERO DE REGISTO
        # =================================================

        if not registo.get(
            "numero_registo"
        ):

            avisos.append(
                f"Linha {indice + 2} "
                f"({registo.get('nome_medicamento', '')}): "
                f"sem número de registo"
            )


        # =================================================
        # VERIFICAÇÃO DA IMAGEM
        # =================================================

        if not registo.get(
            "foto"
        ):

            avisos.append(
                f"Linha {indice + 2} "
                f"({registo.get('nome_medicamento', '')}): "
                f"sem imagem"
            )


        # =================================================
        # ADICIONAR REGISTO
        # =================================================

        registos.append(
            registo
        )


    # =====================================================
    # CRIAR medicamentos.json
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
    # RESULTADO
    # =====================================================

    print()

    print(
        f"SUCESSO: {len(registos)} medicamentos "
        f"convertidos para '{SAIDA}'."
    )


    # =====================================================
    # ESTATÍSTICAS DOS VÍDEOS
    # =====================================================

    total_farmacodinamica = sum(
        1
        for registo in registos
        if registo.get(
            "video_farmacodinamica"
        )
    )


    total_farmacocinetica = sum(
        1
        for registo in registos
        if registo.get(
            "video_farmacocinetica"
        )
    )


    print()

    print(
        "Vídeos de farmacodinâmica: "
        f"{total_farmacodinamica}"
    )

    print(
        "Vídeos de farmacocinética: "
        f"{total_farmacocinetica}"
    )


    # =====================================================
    # AVISOS
    # =====================================================

    if avisos:

        print()

        print(
            f"{len(avisos)} aviso(s):"
        )

        for aviso in avisos:
            print(" -", aviso)

    else:

        print()

        print(
            "Todos os medicamentos têm "
            "número de registo e imagem definidos."
        )


# =========================================================
# EXECUTAR
# =========================================================

if __name__ == "__main__":
    converter()