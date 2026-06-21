# Dicionario de Dados

Arquivo principal: `operacoes_ecommerce_tratado.csv`

| Coluna | Descricao |
| --- | --- |
| `id_pedido` | Identificador unico do pedido. |
| `data_pedido` | Data em que o pedido foi registrado. |
| `ano`, `mes`, `nome_mes`, `ano_mes`, `dia_semana` | Campos derivados da data para analise temporal. |
| `status_original` | Status do pedido conforme veio no dataset bruto. |
| `status_pedido` | Status agrupado para dashboard: `Cancelado`, `Entregue`, `Enviado`, `Devolucao`, `Pendente` ou `Outro`. |
| `status_entrega_original` | Status original informado pela transportadora. |
| `fulfillment` | Responsavel operacional original pelo atendimento do pedido. |
| `tipo_fulfillment` | Agrupamento corporativo do fulfillment: `Amazon` ou `Seller`. |
| `canal_venda` | Canal onde o pedido foi registrado. |
| `nivel_servico_envio` | Nivel de servico original do envio. |
| `tipo_servico` | Classificacao do envio: `Padrao`, `Expresso` ou `Nao informado`. |
| `categoria` | Categoria do item vendido. |
| `tamanho` | Tamanho do item, quando aplicavel. |
| `quantidade` | Quantidade vendida no pedido. |
| `moeda` | Moeda do valor original. |
| `valor_bruto` | Valor original do pedido. |
| `receita_liquida` | Valor considerado como receita valida; pedidos cancelados recebem 0. |
| `valor_cancelado` | Valor associado a pedidos cancelados. |
| `preco_unitario_estimado` | Valor unitario estimado a partir de `valor_bruto / quantidade`. |
| `faixa_valor_pedido` | Segmentacao por valor: `Sem receita`, `Baixo valor`, `Medio valor`, `Alto valor` ou `Valor premium`. |
| `cidade_envio`, `estado_envio`, `cep_envio`, `pais_envio` | Dados geograficos do destino. |
| `regiao_operacional` | Agrupamento regional criado a partir do estado. |
| `tipo_cliente` | Segmentacao do pedido entre `B2B` e `B2C`. |
| `pedido_b2b` | Campo booleano indicando se o pedido e B2B. |
| `pedido_cancelado`, `pedido_entregue`, `pedido_enviado`, `pedido_sucesso` | Indicadores booleanos derivados do status. |
| `responsavel_entrega` | Campo original de responsavel pela entrega, quando disponivel. |
| `contador_pedidos` | Contador fixo igual a 1 para facilitar medidas no Power BI. |
