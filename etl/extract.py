"""
Módulo de Extração de Dados - Comercial Saavedra.
Responsável por carregar os dados brutos a partir de dados/bruto/Tarefas Power BI.xlsx.
"""

import os
from pathlib import Path
import pandas as pd


def get_project_root() -> Path:
    """Retorna a raiz do projeto."""
    return Path(__file__).resolve().parent.parent


def extract_raw_tasks(file_path: Path | str | None = None, sheet_name: str = "Ploomes") -> pd.DataFrame:
    """
    Extrai os dados da aba especificada da planilha bruta do Excel.

    Args:
        file_path: Caminho para o arquivo Excel. Se None, usa o caminho padrão dados/bruto/Tarefas Power BI.xlsx.
        sheet_name: Nome da aba a ser lida. Padrão 'Ploomes'.

    Returns:
        pd.DataFrame: DataFrame com os dados brutos extraídos.
    """
    if file_path is None:
        root = get_project_root()
        file_path = root / "dados" / "bruto" / "Tarefas Power BI.xlsx"
    else:
        file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo bruto não encontrado no caminho especificado: {file_path}")

    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
    return df_raw


if __name__ == "__main__":
    df = extract_raw_tasks()
    print(f"Extração concluída com sucesso: {df.shape[0]} linhas e {df.shape[1]} colunas.")
