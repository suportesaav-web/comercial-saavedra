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


from typing import Callable, Optional
from etl.api_client import PloomesClient


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


def extract_tasks_from_api(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> pd.DataFrame:
    """
    Extrai todas as tarefas diretamente da API Ploomes CRM paginada via OData.

    Args:
        api_key: User-Key do Ploomes (se None, lê de settings / .env).
        base_url: URL base da API (se None, usa https://api2.ploomes.com).
        progress_callback: Função para reportar progresso da busca.

    Returns:
        pd.DataFrame: DataFrame com os dados normalizados.
    """
    client = PloomesClient(api_key=api_key, base_url=base_url)
    return client.fetch_tasks_dataframe(progress_callback=progress_callback)


def extract_tasks(
    source: str = "api",
    file_path_or_buffer=None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> pd.DataFrame:
    """
    Função unificada de extração.

    Args:
        source: 'api' para buscar diretamente do CRM Ploomes, ou 'excel' para carregar planilha.
        file_path_or_buffer: Buffer ou caminho de arquivo Excel (usado se source='excel' ou como fallback).
        progress_callback: Callback de progresso opcional.
    """
    if source.lower() == "api":
        return extract_tasks_from_api(progress_callback=progress_callback)
    elif source.lower() == "excel":
        return extract_raw_tasks(file_path_or_buffer=file_path_or_buffer)
    else:
        raise ValueError(f"Fonte de dados inválida: '{source}'. Utilize 'api' ou 'excel'.")


if __name__ == "__main__":
    print("Testando extração via API Ploomes...")
    df = extract_tasks(source="api")
    print(f"Extração API concluída: {df.shape[0]} linhas e {df.shape[1]} colunas.")
