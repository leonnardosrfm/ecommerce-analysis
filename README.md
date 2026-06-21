# Dashboard de Operações de E-commerce

Projeto criado para praticar análise de dados com Python, Pandas e Power BI. A ideia foi simular uma análise corporativa simples de uma operação de e-commerce, olhando para pedidos, receita, cancelamentos, regiões, categorias e fulfillment.

## Ferramentas usadas

- Python
- Pandas
- Power BI
- CSV

## Dados usados

Usei uma base pública de pedidos da Amazon India:

- Fonte: https://github.com/shivamverma26/Amazon_Sales_Analysis
- Arquivo bruto: `data/raw/amazon_sale_report_raw.csv`
- Arquivo tratado para o Power BI: `data/processed/Operacoes.csv`

Os dados são públicos e anonimizados. O objetivo do projeto não é representar a operação real da Amazon, mas usar uma base realista para treinar limpeza, organização e visualização de dados.

## O que o tratamento faz

O script `scripts/clean_data.py`:

- Padroniza os nomes das colunas.
- Converte datas e valores numéricos.
- Traduz e agrupa alguns campos para facilitar a análise.
- Cria a coluna `receita_liquida`, considerando pedidos cancelados como receita 0.
- Cria indicadores como `pedido_cancelado`, `pedido_entregue` e `pedido_sucesso`.
- Cria campos de apoio como `tipo_cliente`, `tipo_fulfillment`, `tipo_servico`, `faixa_valor_pedido` e `regiao_operacional`.

Para gerar a base tratada:

```powershell
cd C:\Users\leopi\Documents\Codex\amazon-sales-operations-dashboard
.\.venv\Scripts\python.exe scripts\clean_data.py
```

## CLI interativo

Também criei um script interativo para escolher quais colunas manter em um novo CSV. Com ele, posso selecionar um arquivo bruto, escolher as colunas, aplicar tratamentos básicos e exportar um arquivo menor para análises específicas:

```powershell
.\.venv\Scripts\python.exe scripts\interactive_data_prep.py
```

## Arquivos principais

- `data/raw/amazon_sale_report_raw.csv`: base original usada no projeto.
- `data/processed/Operacoes.csv`: base tratada usada no Power BI.
- `data/processed/resumo_kpis.csv`: resumo com os principais indicadores.
- `dashboard/powerbi_measures.md`: medidas DAX usadas no dashboard.
- `scripts/clean_data.py`: script principal de tratamento.
- `scripts/interactive_data_prep.py`: CLI interativo para criar recortes personalizados.

## Como usar no Power BI

1. Abra o Power BI Desktop.
2. Vá em `Obter dados` > `Texto/CSV`.
3. Selecione `data/processed/Operacoes.csv`.
4. Confira os tipos das colunas em `Transformar Dados`.
5. Clique em `Fechar e Aplicar`.
6. Renomeie a tabela para `Operacoes`.
7. Crie as medidas do arquivo `dashboard/powerbi_measures.md`.

## Gráficos sugeridos

- Cards: receita líquida, total de pedidos, unidades vendidas, ticket médio e taxa de cancelamento.
- Linha: receita líquida por mês.
- Barras: receita por região operacional.
- Barras: pedidos por status.
- Barras: receita por categoria.
- Segmentadores: mês, região, fulfillment e tipo de cliente.

## Indicadores encontrados

Com a base tratada atual:

- Total de pedidos: 128.976
- Receita líquida: 71.671.747 INR
- Unidades vendidas: 116.646
- Ticket médio: 663,20 INR
- Taxa de cancelamento: 14,22%

## Observação

Este projeto foi feito para estudo e portfólio. A base é pública e anônima, e a análise foi tratada como uma simulação de ambiente corporativo de e-commerce.
