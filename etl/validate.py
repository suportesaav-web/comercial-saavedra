"""
Módulo de Validação de Dados - Comercial Saavedra.
Valida schemas, tipos de dados, limites e anomalias da extração bruta.
"""

from typing import Dict, Any, List
import pandas as pd

EXPECTED_COLUMNS: List[str] = [
    "Título",
    "Descrição",
    "Finalizada",
    "Data",
    "Nome do Cliente",
    "Título do Negócio",
    "Usuários",
    "Marcadores",
    "Data de criação",
    "Tipo",
    "Criador"
]


def validate_raw_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executa testes de validação no DataFrame bruto.

    Args:
        df: DataFrame extraído do arquivo bruto.

    Returns:
        Dict contendo o relatório de conformidade.
    """
    if df.empty:
        raise ValueError("O DataFrame bruto está vazio.")

    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias ausentes no arquivo bruto: {missing_cols}")

    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns_present": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "is_valid": True,
        "warnings": []
    }

    # Verificações de anomalias
    if df["Nome do Cliente"].isnull().any():
        report["warnings"].append("Existem registros com 'Nome do Cliente' nulo que precisarão de tratamento.")

    if df["Título"].isnull().any():
        report["warnings"].append("Existem registros com 'Título' nulo que receberão fallback no transform.")

    # Verificação de datas futuras (> 2026)
    if "Data" in df.columns:
        dates = pd.to_datetime(df["Data"], errors="coerce")
        future_mask = dates.dt.year > 2026
        future_count = int(future_mask.sum())
        if future_count > 0:
            report["warnings"].append(f"Detectadas {future_count} datas agendadas no futuro distante (>2026).")

    return report


if __name__ == "__main__":
    from etl.extract import extract_raw_tasks
    df = extract_raw_tasks()
    validation = validate_raw_schema(df)
    print("Relatório de Validação:")
    for k, v in validation.items():
        print(f"  {k}: {v}")
