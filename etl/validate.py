"""
Módulo de Validação de Dados - Comercial Saavedra.
Valida schemas, tipos de dados, limites e anomalias da extração bruta.
"""

from typing import Dict, Any, List
import pandas as pd

import unicodedata

try:
    from app.config.settings import ANOMALOUS_FUTURE_YEAR_THRESHOLD
except Exception:
    ANOMALOUS_FUTURE_YEAR_THRESHOLD = 2026


def normalize_col(col_name: object) -> str:
    """Normaliza nome de coluna removendo acentos, espaços extras e convertendo para minúsculas."""
    col_clean = unicodedata.normalize("NFKD", str(col_name)).encode("ASCII", "ignore").decode("utf-8")
    return " ".join(col_clean.lower().strip().split())


# Mapeamento de grupos de colunas obrigatórias com sinônimos aceitos
COLUMN_ALIASES = [
    ("Título", ["Título", "Titulo"]),
    ("Descrição", ["Descrição", "Descricao"]),
    ("Finalizada", ["Finalizada"]),
    ("Data", ["Data", "Data do Evento"]),
    ("Nome do Cliente", ["Nome do Cliente", "Cliente"]),
    ("Título do Negócio", ["Título do Negócio", "Negócio", "Titulo do Negocio"]),
    ("Usuários", ["Usuários", "Usuarios"]),
    ("Marcadores", ["Marcadores"]),
    ("Data de criação", ["Data de criação", "Data de criacao", "Data de Criação", "Data Criação"]),
    ("Tipo", ["Tipo"]),
    ("Criador", ["Criador"])
]


def validate_raw_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executa testes de validação no DataFrame bruto.
    Aceita sinônimos frequentes de colunas exportadas do Ploomes CRM independente de maiúsculas/minúsculas e acentuação.

    Args:
        df: DataFrame extraído do arquivo bruto.

    Returns:
        Dict contendo o relatório de conformidade.
    """
    if df.empty:
        raise ValueError("O DataFrame bruto está vazio.")

    cols_normalized = {normalize_col(c): c for c in df.columns}
    missing_groups = []

    for canonical, aliases in COLUMN_ALIASES:
        found = any(normalize_col(alias) in cols_normalized for alias in aliases)
        if not found:
            missing_groups.append(f"{canonical} (ou {'/'.join(aliases[1:])})")

    if missing_groups:
        raise ValueError(f"Colunas obrigatórias ausentes no arquivo bruto: {missing_groups}")


    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns_present": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "is_valid": True,
        "warnings": []
    }

    # Verificações de anomalias
    cli_col = "Nome do Cliente" if "Nome do Cliente" in df.columns else ("Cliente" if "Cliente" in df.columns else None)
    if cli_col and df[cli_col].isnull().any():
        report["warnings"].append(f"Existem registros com '{cli_col}' nulo que receberão fallback no transform.")

    tit_col = "Título" if "Título" in df.columns else ("Titulo" if "Titulo" in df.columns else None)
    if tit_col and df[tit_col].isnull().any():
        report["warnings"].append(f"Existem registros com '{tit_col}' nulo que receberão fallback no transform.")

    # Verificação de datas futuras (> ANOMALOUS_FUTURE_YEAR_THRESHOLD)
    date_col = "Data" if "Data" in df.columns else ("Data do Evento" if "Data do Evento" in df.columns else None)
    if date_col:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        future_mask = dates.dt.year > ANOMALOUS_FUTURE_YEAR_THRESHOLD
        future_count = int(future_mask.sum())
        if future_count > 0:
            report["warnings"].append(f"Detectadas {future_count} datas agendadas no futuro distante (>{ANOMALOUS_FUTURE_YEAR_THRESHOLD}).")

    return report


if __name__ == "__main__":
    from etl.extract import extract_raw_tasks
    df = extract_raw_tasks()
    validation = validate_raw_schema(df)
    print("Relatório de Validação:")
    for k, v in validation.items():
        print(f"  {k}: {v}")
