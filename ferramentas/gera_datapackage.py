#!/usr/bin/env python3.12
"""Gera datapackage.json (Frictionless Data Package) a partir da pasta dados/.

Uso:
    python3.12 ferramentas/gera_datapackage.py            # regrava datapackage.json
    python3.12 ferramentas/gera_datapackage.py --checa    # só compara, sai com erro se estiver desatualizado

Roda a cada edição mensal, depois que os CSVs novos entram em dados/.
Não lê nem altera nada em dados/; só lista os arquivos e olha o cabeçalho e a
primeira linha de cada um para montar o título/descrição de cada resource.
"""
import csv
import glob
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATAPACKAGE_PATH = os.path.join(REPO_ROOT, "datapackage.json")
SCHEMA_MENSAL_PATH = os.path.join(REPO_ROOT, "ferramentas", "schemas", "esquema-mensal.json")
SCHEMA_MENSAL_REL = "ferramentas/schemas/esquema-mensal.json"

MESES_PT = {
    "janeiro": "01", "fevereiro": "02", "marco": "03", "março": "03", "abril": "04",
    "maio": "05", "junho": "06", "julho": "07", "agosto": "08", "setembro": "09",
    "outubro": "10", "novembro": "11", "dezembro": "12",
}


def campos_comuns():
    """Campos presentes em todo CSV de dados/ (mensal e atual), na ordem do cabeçalho."""
    return [
        {
            "name": "cidade",
            "type": "string",
            "description": "Nome do município.",
            "constraints": {"required": True},
        },
        {
            "name": "bairro",
            "type": "string",
            "description": (
                "Nome do bairro, como publicado no site. Pode conter vírgula, "
                "parênteses ou variações de grafia (ver ERRATAS.md para unificações)."
            ),
            "constraints": {"required": True},
        },
        {
            "name": "tipo",
            "type": "string",
            "description": "Tipo de imóvel.",
            "constraints": {
                "required": True,
                "enum": ["apartamento", "casa", "terreno", "sala", "galpao"],
            },
        },
        {
            "name": "modo",
            "type": "string",
            "description": "Modo do anúncio.",
            "constraints": {"required": True, "enum": ["venda", "aluguel"]},
        },
        {
            "name": "mediana_rs_m2",
            "type": "number",
            "decimalChar": ".",
            "description": (
                "Mediana do preço pedido por m² (R$), sobre os anúncios válidos do "
                "bairro/tipo/modo na edição. Preço pedido em anúncio, não preço de transação."
            ),
            "constraints": {"required": True, "minimum": 0},
        },
        {
            "name": "p25",
            "type": "number",
            "decimalChar": ".",
            "description": "Percentil 25 do preço pedido por m² (R$): 25% dos anúncios pedem menos que esse valor.",
            "constraints": {"required": True, "minimum": 0},
        },
        {
            "name": "p75",
            "type": "number",
            "decimalChar": ".",
            "description": "Percentil 75 do preço pedido por m² (R$): 75% dos anúncios pedem menos que esse valor.",
            "constraints": {"required": True, "minimum": 0},
        },
        {
            "name": "n_anuncios",
            "type": "integer",
            "description": (
                "Número de anúncios válidos usados no cálculo. Bairros com menos de 5 "
                "anúncios não recebem mediana e não aparecem no arquivo (corte mínimo da metodologia)."
            ),
            "constraints": {"required": True, "minimum": 5},
        },
        {
            "name": "yield_anual_pct",
            "type": "number",
            "decimalChar": ".",
            "description": (
                "Rendimento bruto anual do aluguel (%): aluguel mediano anualizado dividido pelo "
                "preço mediano de venda do mesmo bairro/tipo, sem descontar condomínio, IPTU, "
                "vacância, manutenção ou imposto de renda. Vazio quando não há par venda/aluguel "
                "suficiente para o cálculo (critério mínimo exato não documentado na metodologia — a confirmar)."
            ),
            "constraints": {"minimum": 0},
        },
        {
            "name": "coleta",
            "type": "string",
            "description": (
                "Mês da edição/coleta, em português, no formato 'mês/ano' (ex.: 'setembro/2026'). "
                "Modelado como string, não como yearmonth, porque o mês vem por extenso em "
                "português e não em formato ISO."
            ),
            "constraints": {"required": True},
        },
    ]


def campo_cidade_id():
    return {
        "name": "cidade_id",
        "type": "string",
        "description": (
            "Identificador da cidade (slug), igual ao nome do arquivo em dados/mensal/ "
            "(ex.: 'sao-jose-do-rio-preto.csv' -> 'sao-jose-do-rio-preto'). Campo inferido "
            "dos dados, não documentado explicitamente na metodologia."
        ),
        "constraints": {"required": True},
    }


def esquema_mensal():
    return {
        "fields": campos_comuns(),
        "primaryKey": ["bairro", "tipo", "modo"],
        "missingValues": [""],
    }


def esquema_atual():
    return {
        "fields": [campo_cidade_id()] + campos_comuns(),
        "primaryKey": ["cidade_id", "bairro", "tipo", "modo"],
        "missingValues": [""],
    }


def dialeto():
    return {
        "delimiter": ",",
        "quoteChar": '"',
        "doubleQuote": True,
        "lineTerminator": "\r\n",
        "header": True,
    }


def primeira_linha(caminho_csv):
    with open(caminho_csv, encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            return linha
    return None


def edicao_para_versao(edicao):
    """'2026-09' -> '2026.09'"""
    ano, mes = edicao.split("-")
    return f"{ano}.{mes}"


def resource_atual():
    caminho = os.path.join(REPO_ROOT, "dados", "atual", "dados-brasil.csv")
    linha = primeira_linha(caminho)
    coleta = linha["coleta"] if linha else "?"
    return {
        "name": "dados-atual-brasil",
        "title": f"Edição corrente — Brasil, todas as cidades ({coleta})",
        "description": (
            "A edição corrente (todas as 109 cidades num arquivo só), a mesma publicada no site."
        ),
        "path": "dados/atual/dados-brasil.csv",
        "profile": "tabular-data-resource",
        "format": "csv",
        "mediaType": "text/csv",
        "encoding": "utf-8",
        "dialect": dialeto(),
        "schema": esquema_atual(),
    }


def slug_do_arquivo(caminho):
    return os.path.splitext(os.path.basename(caminho))[0]


def resources_mensal():
    padrao = os.path.join(REPO_ROOT, "dados", "mensal", "*", "*.csv")
    recursos = []
    for caminho in sorted(glob.glob(padrao)):
        edicao = os.path.basename(os.path.dirname(caminho))  # AAAA-MM
        slug = slug_do_arquivo(caminho)
        linha = primeira_linha(caminho)
        cidade = linha["cidade"] if linha else slug
        coleta = linha["coleta"] if linha else edicao
        caminho_rel = os.path.relpath(caminho, REPO_ROOT).replace(os.sep, "/")
        recursos.append(
            {
                "name": f"mensal-{edicao}-{slug}",
                "title": f"{cidade} — edição {coleta}",
                "description": f"Medianas de preço pedido por m² por bairro em {cidade}, edição {coleta}.",
                "path": caminho_rel,
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediaType": "text/csv",
                "encoding": "utf-8",
                "dialect": dialeto(),
                "schema": SCHEMA_MENSAL_REL,
            }
        )
    return recursos


def edicao_corrente():
    edicoes = sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(REPO_ROOT, "dados", "mensal", "*"))
    )
    if not edicoes:
        raise RuntimeError("Nenhuma edição encontrada em dados/mensal/")
    return edicoes[-1]


def monta_datapackage():
    edicao = edicao_corrente()
    return {
        "profile": "tabular-data-package",
        "name": "corrida-dos-bairros-dados",
        "title": "A Corrida dos Bairros: mediana do preço pedido por m² por bairro",
        "description": (
            "Mediana do preço pedido por m² em cada bairro de 109 cidades brasileiras, calculada "
            "todo mês a partir de anúncios públicos de portais e sites de imobiliárias. Traz também "
            "o percentil 25, o percentil 75, o número de anúncios válidos e o rendimento bruto do "
            "aluguel por bairro, tipo de imóvel e modo (venda ou aluguel). São preços pedidos em "
            "anúncios, não preços de transação; não é avaliação de imóvel nem recomendação de "
            "investimento. Um projeto do Minuto Jaraguá."
        ),
        "version": edicao_para_versao(edicao),
        "created": f"{edicao}-01T00:00:00Z",
        "homepage": "https://acorridadosbairros.com.br",
        "licenses": [
            {
                "name": "CC-BY-4.0",
                "title": "Creative Commons Atribuição 4.0 Internacional",
                "path": "https://creativecommons.org/licenses/by/4.0/legalcode.pt",
            }
        ],
        "sources": [
            {
                "title": "A Corrida dos Bairros — Minuto Jaraguá",
                "path": "https://acorridadosbairros.com.br",
            }
        ],
        "contributors": [
            {
                "title": "Minuto Jaraguá",
                "role": "author",
                "email": "minutojaragua@gmail.com",
            }
        ],
        "keywords": [
            "mercado imobiliário",
            "preço do metro quadrado",
            "bairros",
            "brasil",
            "dados abertos",
            "real estate",
            "price per square meter",
            "neighborhoods",
            "brazil",
            "open data",
        ],
        "resources": [resource_atual()] + resources_mensal(),
    }


def escreve_json(caminho, dados):
    texto = json.dumps(dados, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    return texto


def le_texto(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as f:
        return f.read()


def main():
    checa = "--checa" in sys.argv[1:]

    os.makedirs(os.path.dirname(SCHEMA_MENSAL_PATH), exist_ok=True)
    esquema_mensal_txt = json.dumps(esquema_mensal(), ensure_ascii=False, indent=2) + "\n"
    datapackage_txt = json.dumps(monta_datapackage(), ensure_ascii=False, indent=2) + "\n"

    if checa:
        atual_dp = le_texto(DATAPACKAGE_PATH)
        atual_esquema = le_texto(SCHEMA_MENSAL_PATH)
        desatualizado = atual_dp != datapackage_txt or atual_esquema != esquema_mensal_txt
        if desatualizado:
            print(
                "datapackage.json (ou ferramentas/schemas/esquema-mensal.json) está "
                "desatualizado em relação a dados/. Rode sem --checa para regravar.",
                file=sys.stderr,
            )
            sys.exit(1)
        print("datapackage.json está atualizado.")
        return

    with open(SCHEMA_MENSAL_PATH, "w", encoding="utf-8") as f:
        f.write(esquema_mensal_txt)
    with open(DATAPACKAGE_PATH, "w", encoding="utf-8") as f:
        f.write(datapackage_txt)
    print(f"Gravado {DATAPACKAGE_PATH} e {SCHEMA_MENSAL_PATH}.")


if __name__ == "__main__":
    main()
