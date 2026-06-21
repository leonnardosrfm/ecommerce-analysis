# Dashboard de Operacoes de E-commerce

Projeto criado para praticar analise de dados com Python, Pandas e Power BI. A ideia foi simular uma analise corporativa simples de uma operacao de e-commerce, olhando para pedidos, receita, cancelamentos, regioes, categorias e fulfillment.

## Ferramentas usadas

- Python
- Pandas
- Power BI
- CSV

## Dados usados

Usei uma base publica de pedidos da Amazon India:

- Fonte: https://github.com/shivamverma26/Amazon_Sales_Analysis
- Arquivo bruto: `data/raw/amazon_sale_report_raw.csv`
- Arquivo tratado para o Power BI: `data/processed/Operacoes.csv`

Os dados sao publicos e anonimizados. O objetivo do projeto nao e representar a operacao real da Amazon, mas usar uma base realista para treinar limpeza, organizacao e visualizacao de dados.

## O que o tratamento faz

O script `scripts/clean_data.py`:

- Padroniza os nomes das colunas.
- Converte datas e valores numericos.
- Traduz e agrupa alguns campos para facilitar a analise.
- Cria `receita_liquida`, considerando pedidos cancelados como receita 0.
- Cria indicadores como `pedido_cancelado`, `pedido_entregue` e `pedido_sucesso`.
- Cria campos de apoio como `tipo_cliente`, `tipo_fulfillment`, `tipo_servico`, `faixa_valor_pedido` e `regiao_operacional`.

Para gerar a base tratada:

```powershell
cd C:\Users\leopi\Documents\Codex\amazon-sales-operations-dashboard
.\.venv\Scripts\python.exe scripts\clean_data.py
```

## CLI interativo

Tambem criei um script interativo para escolher quais colunas manter em um novo CSV:

```powershell
.\.venv\Scripts\python.exe scripts\interactive_data_prep.py
```

Com ele, posso selecionar um CSV bruto, escolher colunas, aplicar tratamentos basicos e exportar um arquivo menor para analises especificas.

## Arquivos principais

- `data/raw/amazon_sale_report_raw.csv`: base original usada no projeto.
- `data/processed/Operacoes.csv`: base tratada usada no Power BI.
- `data/processed/resumo_kpis.csv`: resumo com os principais indicadores.
- `dashboard/powerbi_measures.md`: medidas DAX usadas no dashboard.
- `scripts/clean_data.py`: script principal de tratamento.
- `scripts/interactive_data_prep.py`: CLI interativo para criar recortes personalizados.

## Como usar no Power BI

1. Abra o Power BI Desktop.
2. Va em `Obter dados` > `Texto/CSV`.
3. Selecione `data/processed/Operacoes.csv`.
4. Confira os tipos das colunas em `Transformar Dados`.
5. Clique em `Fechar e Aplicar`.
6. Renomeie a tabela para `Operacoes`.
7. Crie as medidas do arquivo `dashboard/powerbi_measures.md`.

## Graficos sugeridos

- Cards: receita liquida, total de pedidos, unidades vendidas, ticket medio e taxa de cancelamento.
- Linha: receita liquida por mes.
- Barras: receita por regiao operacional.
- Barras: pedidos por status.
- Barras: receita por categoria.
- Segmentadores: mes, regiao, fulfillment e tipo de cliente.

## Indicadores encontrados

Com a base tratada atual:

- Total de pedidos: 128.976
- Receita liquida: 71.671.747 INR
- Unidades vendidas: 116.646
- Ticket medio: 663,20 INR
- Taxa de cancelamento: 14,22%

## Observacao

Este projeto foi feito para estudo e portfolio. A base e publica e anonima, e a analise foi tratada como uma simulacao de ambiente corporativo de e-commerce.
