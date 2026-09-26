# ferramentas/

## gera_datapackage.py

Gera o `datapackage.json` da raiz (padrão [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/))
a partir do que está em `dados/`: um resource para `dados/atual/dados-brasil.csv`
e um resource por arquivo de `dados/mensal/AAAA-MM/<cidade>.csv`. Usa só a
biblioteca padrão do Python (nenhuma dependência externa).

Roda a cada edição mensal, depois que os CSVs novos entram em `dados/`:

```
python3.12 ferramentas/gera_datapackage.py
```

Isso regrava `datapackage.json` e `ferramentas/schemas/esquema-mensal.json`
(o esquema compartilhado pelos 115+ arquivos de `dados/mensal/`, referenciado
por cada resource mensal em vez de repetido em cada um).

Para checar em CI ou antes de commitar, sem regravar nada:

```
python3.12 ferramentas/gera_datapackage.py --checa
```

Sai com código 1 e uma mensagem no stderr se o `datapackage.json` (ou o
esquema mensal) commitado estiver desatualizado em relação a `dados/`; sai
com código 0 e "está atualizado" se não houver diferença.

O script só lê `dados/`; nunca escreve nada ali.

Depois de rodar, valide com o [frictionless-py](https://framework.frictionlessdata.io/):

```
pip install --break-system-packages frictionless
frictionless validate datapackage.json
```
