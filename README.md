# A Corrida dos Bairros: dados abertos

Este repositório guarda os **dados mensais** publicados em [acorridadosbairros.com.br](https://acorridadosbairros.com.br): a mediana do preço pedido por m² em cada bairro de 109 cidades brasileiras. Junto vão a metodologia, o registro de erratas e a nota técnica. É um projeto do Minuto Jaraguá.

Cada edição fica guardada como foi publicada. Assim, qualquer pessoa pode citar um número e conferir depois de onde ele veio.

## O que está aqui

| Caminho | Conteúdo |
|---|---|
| `dados/mensal/AAAA-MM/` | Medianas publicadas em cada edição, uma planilha por cidade. |
| `dados/atual/dados-brasil.csv` | A edição corrente, todas as cidades num arquivo só. |
| `METODOLOGIA.md` | A metodologia publicada no site, com versão e data. |
| `ERRATAS.md` | O registro público de erratas e retiradas. |
| `nota-tecnica.pdf` | A nota técnica para citar e arquivar. |

Cada linha traz cidade, bairro, tipo de imóvel, modo (venda ou aluguel), mediana em R$/m², P25, P75, número de anúncios, rendimento bruto do aluguel e o mês da coleta.

## Como citar

> A Corrida dos Bairros, Minuto Jaraguá. Medianas do preço pedido por m² por bairro, edição de setembro/2026. Disponível em https://acorridadosbairros.com.br

Cada edição mensal, a partir de outubro/2026, recebe um DOI no Zenodo. O arquivo `CITATION.cff` traz os metadados para gerenciadores de referência.

**Versões com DOI são imutáveis.** Uma correção nunca altera a edição já arquivada: sai uma versão nova, com a errata registrada em `ERRATAS.md`, e a versão anterior continua acessível.

## Licença

Os dados estão sob **Creative Commons Atribuição 4.0 (CC BY 4.0)**, descrita em `LICENSE-DADOS.md`. Use, cruze e republique, inclusive comercialmente, citando "A Corrida dos Bairros, Minuto Jaraguá". A licença cobre os números, não o texto, o desenho e as marcas do site.

## Limitações

Os valores são **preços pedidos em anúncios**, não preços de transação. Não são avaliação de imóvel nem recomendação de investimento. A série começa em agosto/2026 e ainda é curta. Os anúncios individuais e os programas de coleta não são publicados.

## Retirada de fonte

Portal ou imobiliária que não queira ter os anúncios públicos lidos escreve para minutojaragua@gmail.com e sai na rodada seguinte, com registro em `ERRATAS.md`.
