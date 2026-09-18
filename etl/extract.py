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


def extract_raw_tasks(file_path_or_buffer=None, sheet_name: str | None = "Ploomes") -> pd.DataFrame:
    """
    Extrai os dados da aba especificada da planilha bruta do Excel ou de um buffer em memória.

    Args:
        file_path_or_buffer: Caminho (Path/str) ou buffer (BytesIO/UploadedFile). Se None, usa dados/bruto/Tarefas Power BI.xlsx.
        sheet_name: Nome da aba a ser lida. Se 'Ploomes' não existir, seleciona a primeira aba disponível.

    Returns:
        pd.DataFrame: DataFrame com os dados brutos extraídos.
    """
    if file_path_or_buffer is None:
        root = get_project_root()
        file_path_or_buffer = root / "dados" / "bruto" / "Tarefas Power BI.xlsx"
        if not file_path_or_buffer.exists():
            raise FileNotFoundError(f"Arquivo bruto não encontrado no caminho padrão: {file_path_or_buffer}")

    # Garante início do buffer se aplicável
    if hasattr(file_path_or_buffer, "seek"):
        file_path_or_buffer.seek(0)

    # Inspeciona as abas do arquivo e efetua o parse direto sem releitura do arquivo físico/buffer
    excel_file = pd.ExcelFile(file_path_or_buffer, engine="openpyxl")
    available_sheets = excel_file.sheet_names

    target_sheet = sheet_name if (sheet_name and sheet_name in available_sheets) else available_sheets[0]
    df_raw = excel_file.parse(target_sheet)
    return df_raw



if __name__ == "__main__":
    df = extract_raw_tasks()
    print(f"Extração concluída com sucesso: {df.shape[0]} linhas e {df.shape[1]} colunas.")
