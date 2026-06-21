from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "amazon_sale_report_raw.csv"
PROCESSED_DIR = ROOT / "data" / "processed"


MONTH_NAMES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

WEEKDAYS_PT = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terca-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sabado",
    "Sunday": "Domingo",
}

REGION_BY_STATE = {
    "Andhra Pradesh": "Sul",
    "Karnataka": "Sul",
    "Kerala": "Sul",
    "Tamil Nadu": "Sul",
    "Telangana": "Sul",
    "Puducherry": "Sul",
    "Maharashtra": "Oeste",
    "Goa": "Oeste",
    "Gujarat": "Oeste",
    "Rajasthan": "Oeste",
    "Madhya Pradesh": "Centro",
    "Chhattisgarh": "Centro",
    "Delhi": "Norte",
    "Haryana": "Norte",
    "Himachal Pradesh": "Norte",
    "Jammu & Kashmir": "Norte",
    "Punjab": "Norte",
    "Uttar Pradesh": "Norte",
    "Uttarakhand": "Norte",
    "Bihar": "Leste",
    "Jharkhand": "Leste",
    "Odisha": "Leste",
    "West Bengal": "Leste",
    "Assam": "Nordeste",
    "Arunachal Pradesh": "Nordeste",
    "Manipur": "Nordeste",
    "Meghalaya": "Nordeste",
    "Mizoram": "Nordeste",
    "Nagaland": "Nordeste",
    "Sikkim": "Nordeste",
    "Tripura": "Nordeste",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace("-", "_", regex=False)
        .str.replace(" ", "_", regex=False)
    )
    return df


def clean_text(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


def classify_status(status: str) -> str:
    value = str(status).lower()
    if "cancelled" in value:
        return "Cancelado"
    if "delivered" in value:
        return "Entregue"
    if "returned" in value or "returning" in value:
        return "Devolucao"
    if "shipped" in value:
        return "Enviado"
    if "pending" in value:
        return "Pendente"
    return "Outro"


def classify_order_value(value: float) -> str:
    if value <= 0:
        return "Sem receita"
    if value < 300:
        return "Baixo valor"
    if value < 700:
        return "Medio valor"
    if value < 1200:
        return "Alto valor"
    return "Valor premium"


def classify_service_level(service_level: str) -> str:
    value = str(service_level).lower()
    if "expedited" in value:
        return "Expresso"
    if "standard" in value:
        return "Padrao"
    return "Nao informado"


def build_clean_dataset() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH, low_memory=False)
    df = normalize_columns(df)

    drop_columns = ["index", "new", "pendings"]
    df = df.drop(columns=[column for column in drop_columns if column in df.columns])

    rename_map = {
        "order_id": "id_pedido",
        "date": "data_pedido",
        "status": "status_original",
        "fulfilment": "fulfillment",
        "sales_channel": "canal_venda",
        "ship_service_level": "nivel_servico_envio",
        "category": "categoria",
        "size": "tamanho",
        "courier_status": "status_entrega_original",
        "qty": "quantidade",
        "currency": "moeda",
        "amount": "valor_bruto",
        "ship_city": "cidade_envio",
        "ship_state": "estado_envio",
        "ship_postal_code": "cep_envio",
        "ship_country": "pais_envio",
        "b2b": "pedido_b2b",
        "fulfilled_by": "responsavel_entrega",
    }
    df = df.rename(columns=rename_map)

    text_columns = [
        "id_pedido",
        "status_original",
        "fulfillment",
        "canal_venda",
        "nivel_servico_envio",
        "categoria",
        "tamanho",
        "status_entrega_original",
        "moeda",
        "cidade_envio",
        "estado_envio",
        "cep_envio",
        "pais_envio",
        "responsavel_entrega",
    ]
    for column in text_columns:
        if column in df.columns:
            df[column] = clean_text(df[column])

    df["data_pedido"] = pd.to_datetime(df["data_pedido"], format="mixed", errors="coerce")
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0).astype("int64")
    df["valor_bruto"] = pd.to_numeric(df["valor_bruto"], errors="coerce").fillna(0).round(2)
    df["pedido_b2b"] = df["pedido_b2b"].astype("bool")

    df["cidade_envio"] = df["cidade_envio"].str.title()
    df["estado_envio"] = df["estado_envio"].str.title()
    df["cep_envio"] = df["cep_envio"].str.replace(r"\.0$", "", regex=True)
    df["categoria"] = df["categoria"].replace({"Blazzer": "Blazer"})

    df["status_pedido"] = df["status_original"].map(classify_status)
    df["pedido_cancelado"] = df["status_pedido"].eq("Cancelado")
    df["pedido_entregue"] = df["status_pedido"].eq("Entregue")
    df["pedido_enviado"] = df["status_pedido"].isin(["Enviado", "Entregue"])
    df["pedido_sucesso"] = df["status_pedido"].isin(["Enviado", "Entregue"])

    df["ano"] = df["data_pedido"].dt.year.astype("Int64")
    df["mes"] = df["data_pedido"].dt.month.astype("Int64")
    df["nome_mes"] = df["mes"].map(MONTH_NAMES_PT)
    df["ano_mes"] = df["data_pedido"].dt.to_period("M").astype("string")
    df["dia_semana"] = df["data_pedido"].dt.day_name().map(WEEKDAYS_PT)

    df["contador_pedidos"] = 1
    df["receita_liquida"] = df["valor_bruto"].where(~df["pedido_cancelado"], 0).round(2)
    df["valor_cancelado"] = df["valor_bruto"].where(df["pedido_cancelado"], 0).round(2)
    df["preco_unitario_estimado"] = (
        df["valor_bruto"] / df["quantidade"].where(df["quantidade"] > 0)
    ).round(2)

    df["tipo_cliente"] = df["pedido_b2b"].map({True: "B2B", False: "B2C"})
    df["tipo_fulfillment"] = df["fulfillment"].replace({"Amazon": "Amazon", "Merchant": "Seller"})
    df["tipo_servico"] = df["nivel_servico_envio"].map(classify_service_level)
    df["faixa_valor_pedido"] = df["receita_liquida"].map(classify_order_value)
    df["regiao_operacional"] = df["estado_envio"].map(REGION_BY_STATE).fillna("Nao mapeada")

    ordered_columns = [
        "id_pedido",
        "data_pedido",
        "ano",
        "mes",
        "nome_mes",
        "ano_mes",
        "dia_semana",
        "status_original",
        "status_pedido",
        "status_entrega_original",
        "fulfillment",
        "tipo_fulfillment",
        "canal_venda",
        "nivel_servico_envio",
        "tipo_servico",
        "categoria",
        "tamanho",
        "quantidade",
        "moeda",
        "valor_bruto",
        "receita_liquida",
        "valor_cancelado",
        "preco_unitario_estimado",
        "faixa_valor_pedido",
        "cidade_envio",
        "estado_envio",
        "regiao_operacional",
        "cep_envio",
        "pais_envio",
        "tipo_cliente",
        "pedido_b2b",
        "pedido_cancelado",
        "pedido_entregue",
        "pedido_enviado",
        "pedido_sucesso",
        "responsavel_entrega",
        "contador_pedidos",
    ]
    return df[ordered_columns]


def export_summary_tables(df: pd.DataFrame) -> None:
    resumo_kpis = pd.DataFrame(
        [
            {
                "total_pedidos": int(df["contador_pedidos"].sum()),
                "receita_liquida": round(float(df["receita_liquida"].sum()), 2),
                "total_unidades": int(df["quantidade"].sum()),
                "ticket_medio": round(float(df.loc[df["receita_liquida"] > 0, "receita_liquida"].mean()), 2),
                "pedidos_cancelados": int(df["pedido_cancelado"].sum()),
                "taxa_cancelamento": round(float(df["pedido_cancelado"].mean()), 4),
                "pedidos_entregues": int(df["pedido_entregue"].sum()),
                "pedidos_b2b": int(df["pedido_b2b"].sum()),
            }
        ]
    )
    resumo_kpis.to_csv(PROCESSED_DIR / "resumo_kpis.csv", index=False)

    vendas_por_mes = (
        df.groupby(["ano_mes"], dropna=False)
        .agg(
            pedidos=("contador_pedidos", "sum"),
            receita_liquida=("receita_liquida", "sum"),
            unidades=("quantidade", "sum"),
            pedidos_cancelados=("pedido_cancelado", "sum"),
        )
        .reset_index()
        .sort_values("ano_mes")
    )
    vendas_por_mes["receita_liquida"] = vendas_por_mes["receita_liquida"].round(2)
    vendas_por_mes.to_csv(PROCESSED_DIR / "vendas_por_mes.csv", index=False)

    resumo_categorias = (
        df.groupby("categoria", dropna=False)
        .agg(
            pedidos=("contador_pedidos", "sum"),
            receita_liquida=("receita_liquida", "sum"),
            unidades=("quantidade", "sum"),
            ticket_medio=("receita_liquida", "mean"),
            pedidos_cancelados=("pedido_cancelado", "sum"),
        )
        .reset_index()
        .sort_values("receita_liquida", ascending=False)
    )
    resumo_categorias["receita_liquida"] = resumo_categorias["receita_liquida"].round(2)
    resumo_categorias["ticket_medio"] = resumo_categorias["ticket_medio"].round(2)
    resumo_categorias.to_csv(PROCESSED_DIR / "resumo_categorias.csv", index=False)

    resumo_estados = (
        df.groupby(["regiao_operacional", "estado_envio"], dropna=False)
        .agg(
            pedidos=("contador_pedidos", "sum"),
            receita_liquida=("receita_liquida", "sum"),
            unidades=("quantidade", "sum"),
            pedidos_cancelados=("pedido_cancelado", "sum"),
        )
        .reset_index()
        .sort_values("receita_liquida", ascending=False)
    )
    resumo_estados["receita_liquida"] = resumo_estados["receita_liquida"].round(2)
    resumo_estados.to_csv(PROCESSED_DIR / "resumo_estados.csv", index=False)

    resumo_operacional = (
        df.groupby(["tipo_fulfillment", "tipo_servico", "status_pedido"], dropna=False)
        .agg(
            pedidos=("contador_pedidos", "sum"),
            receita_liquida=("receita_liquida", "sum"),
            unidades=("quantidade", "sum"),
        )
        .reset_index()
        .sort_values(["tipo_fulfillment", "tipo_servico", "pedidos"], ascending=[True, True, False])
    )
    resumo_operacional["receita_liquida"] = resumo_operacional["receita_liquida"].round(2)
    resumo_operacional.to_csv(PROCESSED_DIR / "resumo_operacional.csv", index=False)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    clean_df = build_clean_dataset()
    output_path = PROCESSED_DIR / "operacoes_ecommerce_tratado.csv"
    clean_df.to_csv(output_path, index=False)
    export_summary_tables(clean_df)
    print(f"Linhas exportadas: {len(clean_df):,}")
    print(f"Colunas exportadas: {len(clean_df.columns)}")
    print(f"Arquivo principal: {output_path}")


if __name__ == "__main__":
    main()
