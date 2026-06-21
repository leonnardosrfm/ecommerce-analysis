# Medidas DAX sugeridas

Use `operacoes_ecommerce_tratado.csv` como tabela principal no Power BI. Nome sugerido da tabela: `Operacoes`.

```DAX
Total Pedidos = SUM(Operacoes[contador_pedidos])
```

```DAX
Receita Liquida = SUM(Operacoes[receita_liquida])
```

```DAX
Unidades Vendidas = SUM(Operacoes[quantidade])
```

```DAX
Ticket Medio = DIVIDE([Receita Liquida], [Total Pedidos])
```

```DAX
Pedidos Cancelados =
CALCULATE(
    [Total Pedidos],
    Operacoes[pedido_cancelado] = TRUE()
)
```

```DAX
Taxa Cancelamento = DIVIDE([Pedidos Cancelados], [Total Pedidos])
```

```DAX
Pedidos Entregues =
CALCULATE(
    [Total Pedidos],
    Operacoes[pedido_entregue] = TRUE()
)
```

```DAX
Taxa Entrega = DIVIDE([Pedidos Entregues], [Total Pedidos])
```

```DAX
Pedidos com Sucesso =
CALCULATE(
    [Total Pedidos],
    Operacoes[pedido_sucesso] = TRUE()
)
```

```DAX
Taxa Sucesso Operacional = DIVIDE([Pedidos com Sucesso], [Total Pedidos])
```

```DAX
Receita B2B =
CALCULATE(
    [Receita Liquida],
    Operacoes[tipo_cliente] = "B2B"
)
```

```DAX
Participacao B2B = DIVIDE([Receita B2B], [Receita Liquida])
```

```DAX
Valor Cancelado = SUM(Operacoes[valor_cancelado])
```

## Visuais recomendados

- Cards: receita liquida, pedidos, unidades vendidas, ticket medio, taxa de cancelamento e taxa de sucesso operacional.
- Linha: receita liquida por `ano_mes`.
- Barras: receita liquida por `regiao_operacional` e `estado_envio`.
- Barras: pedidos cancelados por `categoria`.
- Barras empilhadas: pedidos por `tipo_fulfillment` e `status_pedido`.
- Rosca ou barras: receita por `tipo_cliente`.
- Segmentadores: `ano_mes`, `categoria`, `regiao_operacional`, `tipo_fulfillment`, `tipo_cliente`, `status_pedido`.
