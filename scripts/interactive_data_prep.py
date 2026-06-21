import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = ROOT / "data" / "raw"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "processed"


DATE_HINTS = ("date", "data", "dt_", "_dt")
NUMERIC_HINTS = (
    "amount",
    "value",
    "valor",
    "price",
    "preco",
    "cost",
    "custo",
    "revenue",
    "receita",
    "profit",
    "lucro",
    "qty",
    "quantity",
    "quantidade",
    "units",
    "unit",
    "total",
)


def normalize_column_name(name: str) -> str:
    normalized = name.strip().lower()
    normalized = re.sub(r"[^a-z0-9_]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_")


def list_csv_files(raw_dir: Path) -> list[Path]:
    return sorted(raw_dir.glob("*.csv"))


def prompt_choice(prompt: str, min_value: int, max_value: int) -> int:
    while True:
        value = input(prompt).strip()
        if value.isdigit() and min_value <= int(value) <= max_value:
            return int(value)
        print(f"Digite um numero entre {min_value} e {max_value}.")


def prompt_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = "S/n" if default else "s/N"
    while True:
        value = input(f"{prompt} ({suffix}): ").strip().lower()
        if not value:
            return default
        if value in {"s", "sim", "y", "yes"}:
            return True
        if value in {"n", "nao", "no"}:
            return False
        print("Responda com s ou n.")


def parse_column_selection(selection: str, columns: list[str]) -> list[str]:
    selection = selection.strip()
    if selection.lower() in {"all", "todos", "*"}:
        return columns

    selected: list[str] = []
    parts = [part.strip() for part in selection.split(",") if part.strip()]

    for part in parts:
        if "-" in part and all(piece.strip().isdigit() for piece in part.split("-", 1)):
            start, end = [int(piece.strip()) for piece in part.split("-", 1)]
            if start > end:
                start, end = end, start
            for index in range(start, end + 1):
                if 1 <= index <= len(columns):
                    selected.append(columns[index - 1])
            continue

        if part.isdigit():
            index = int(part)
            if 1 <= index <= len(columns):
                selected.append(columns[index - 1])
            continue

        matches = [column for column in columns if column.lower() == part.lower()]
        if matches:
            selected.append(matches[0])
            continue

        print(f"Coluna ignorada por nao existir: {part}")

    return list(dict.fromkeys(selected))


def coerce_numeric(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype("string")
        .str.strip()
        .str.replace(r"[^\d,.\-]", "", regex=True)
    )

    has_comma_decimal = cleaned.str.contains(",", regex=False).fillna(False)
    has_dot_decimal = cleaned.str.contains(".", regex=False).fillna(False)

    if has_comma_decimal.sum() > has_dot_decimal.sum():
        cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    else:
        cleaned = cleaned.str.replace(",", "", regex=False)

    return pd.to_numeric(cleaned, errors="coerce")


def should_parse_as_date(column: str) -> bool:
    lowered = column.lower()
    return any(hint in lowered for hint in DATE_HINTS)


def should_parse_as_numeric(column: str) -> bool:
    lowered = column.lower()
    return any(hint in lowered for hint in NUMERIC_HINTS)


def clean_selected_dataframe(
    df: pd.DataFrame,
    selected_columns: list[str],
    normalize_columns: bool,
    drop_empty_rows: bool,
) -> tuple[pd.DataFrame, dict]:
    original_rows = len(df)
    original_columns = df.columns.tolist()
    column_map = {}

    if normalize_columns:
        column_map = {column: normalize_column_name(column) for column in df.columns}
        df = df.rename(columns=column_map)
        selected_columns = [column_map[column] for column in selected_columns]

    output = df[selected_columns].copy()
    transformations: dict[str, list[str]] = {}

    for column in output.columns:
        transformations[column] = []

        if pd.api.types.is_object_dtype(output[column]) or pd.api.types.is_string_dtype(output[column]):
            output[column] = (
                output[column]
                .astype("string")
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )
            transformations[column].append("trim_text")

        if should_parse_as_date(column):
            parsed = pd.to_datetime(output[column], format="mixed", errors="coerce")
            if parsed.notna().sum() > 0:
                output[column] = parsed.dt.date
                transformations[column].append("parse_date")
            continue

        if should_parse_as_numeric(column):
            parsed = coerce_numeric(output[column])
            if parsed.notna().sum() > 0:
                output[column] = parsed
                transformations[column].append("parse_numeric")

    if drop_empty_rows:
        output = output.dropna(how="all")

    report = {
        "source_rows": original_rows,
        "source_columns_count": len(original_columns),
        "source_columns": original_columns,
        "output_rows": len(output),
        "output_columns_count": len(output.columns),
        "output_columns": output.columns.tolist(),
        "normalized_columns": normalize_columns,
        "column_map": column_map,
        "drop_empty_rows": drop_empty_rows,
        "transformations": transformations,
    }
    return output, report


def preview_dataframe(df: pd.DataFrame, rows: int = 5) -> None:
    with pd.option_context("display.max_columns", 12, "display.width", 160):
        print(df.head(rows).to_string(index=False))


def ask_output_path(output_dir: Path, default_stem: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    default_name = f"{default_stem}_custom.csv"
    name = input(f"Nome do arquivo de saida [{default_name}]: ").strip() or default_name
    if not name.lower().endswith(".csv"):
        name += ".csv"

    custom_dir = input(f"Pasta de saida [{output_dir}]: ").strip()
    target_dir = Path(custom_dir) if custom_dir else output_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / name


def main() -> None:
    parser = argparse.ArgumentParser(description="Data Prep CLI interativo para gerar recortes tratados de CSVs.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR, help="Pasta com CSVs brutos.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Pasta padrao de saida.")
    args = parser.parse_args()

    raw_dir = args.raw_dir
    output_dir = args.output_dir
    csv_files = list_csv_files(raw_dir)

    if not csv_files:
        raise SystemExit(f"Nenhum CSV encontrado em: {raw_dir}")

    print("\nArquivos CSV encontrados:\n")
    for index, file_path in enumerate(csv_files, start=1):
        print(f"[{index}] {file_path.name}")

    selected_file_index = prompt_choice("\nEscolha o arquivo: ", 1, len(csv_files))
    source_path = csv_files[selected_file_index - 1]

    print(f"\nCarregando: {source_path}")
    df = pd.read_csv(source_path, low_memory=False)

    print(f"\nLinhas: {len(df):,}")
    print(f"Colunas: {len(df.columns)}")
    print("\nPrevia dos dados:\n")
    preview_dataframe(df)

    print("\nColunas disponiveis:\n")
    for index, column in enumerate(df.columns, start=1):
        print(f"[{index}] {column}")

    selected_columns: list[str] = []
    while not selected_columns:
        selection = input(
            "\nEscolha as colunas por numero, intervalo ou nome. Ex: 3,8,14 ou 2-5 ou todos: "
        )
        selected_columns = parse_column_selection(selection, df.columns.tolist())
        if not selected_columns:
            print("Nenhuma coluna valida selecionada.")

    normalize_columns = prompt_yes_no("\nPadronizar nomes das colunas no output", default=True)
    drop_empty_rows = prompt_yes_no("Remover linhas totalmente vazias", default=True)

    output_df, report = clean_selected_dataframe(
        df=df,
        selected_columns=selected_columns,
        normalize_columns=normalize_columns,
        drop_empty_rows=drop_empty_rows,
    )

    print("\nPrevia do output tratado:\n")
    preview_dataframe(output_df)

    output_path = ask_output_path(output_dir, source_path.stem)
    report_path = output_path.with_suffix(".report.json")

    output_df.to_csv(output_path, index=False)

    report.update(
        {
            "source_file": str(source_path),
            "output_file": str(output_path),
            "report_file": str(report_path),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\nExportacao concluida.")
    print(f"CSV tratado: {output_path}")
    print(f"Relatorio: {report_path}")
    print(f"Linhas finais: {len(output_df):,}")
    print(f"Colunas finais: {len(output_df.columns)}")


if __name__ == "__main__":
    main()
