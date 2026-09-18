"""
Carregador de Dados com Cache e Invalidação Automática - Comercial Saavedra.
Lê os arquivos Parquet tratados utilizando @st.cache_data do Streamlit,
com invalidação automática sempre que o arquivo no disco for modificado.
"""

from typing import Tuple
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from app.config.settings import (
    PATH_FATO_PARQUET,
    PATH_PONTE_PARQUET,
    PATH_MENSAL_PARQUET
)
from etl.load import run_etl


def _get_files_mtime() -> float:
    """Retorna o timestamp mais recente de modificação dos arquivos Parquet."""
    mtime = 0.0
    for p in [PATH_FATO_PARQUET, PATH_PONTE_PARQUET, PATH_MENSAL_PARQUET]:
        if p.exists():
            mtime = max(mtime, os.path.getmtime(p))
    return mtime


@st.cache_data(show_spinner="Carregando base de dados tratada...", ttl=None)
def _load_data_cached(mtime: float) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carrega os DataFrames de Parquet. O parâmetro mtime garante invalidação
    automática do cache sempre que o arquivo for atualizado no disco pelo ETL.
    """
    if not PATH_FATO_PARQUET.exists() or not PATH_PONTE_PARQUET.exists() or not PATH_MENSAL_PARQUET.exists():
        st.info("Arquivos Parquet não encontrados. Executando o pipeline ETL inicial...")
        run_etl()

    df_fato = pd.read_parquet(PATH_FATO_PARQUET)
    df_ponte = pd.read_parquet(PATH_PONTE_PARQUET)
    df_mensal = pd.read_parquet(PATH_MENSAL_PARQUET)

    # 1. Conversão de segurança para formato date no Python
    if "data_evento" in df_fato.columns:
        df_fato["data_evento"] = pd.to_datetime(df_fato["data_evento"]).dt.date

    if "data_evento" in df_ponte.columns:
        df_ponte["data_evento"] = pd.to_datetime(df_ponte["data_evento"]).dt.date

    # 2. Formatação explícita para o padrão brasileiro DD/MM/AAAA
    if "data_hora_evento" in df_fato.columns:
        df_fato["data_evento_str"] = pd.to_datetime(df_fato["data_hora_evento"]).dt.strftime("%d/%m/%Y").fillna("")

    # 3. Dinamização do status operacional em tempo real relativo ao instante atual
    if "finalizada" in df_fato.columns and "data_hora_evento" in df_fato.columns:
        agora = pd.Timestamp.now()
        condicoes = [
            df_fato["finalizada"] == True,
            (df_fato["finalizada"] == False) & (df_fato["data_hora_evento"] < agora),
            (df_fato["finalizada"] == False) & (df_fato["data_hora_evento"] >= agora)
        ]
        import numpy as np
        df_fato["status_operacional"] = np.select(condicoes, ["Finalizada", "Atrasada", "Agendada"], default="Indefinido")

        # Reflete status atualizado na tabela-ponte
        status_map = dict(zip(df_fato["sk_tarefa"], df_fato["status_operacional"]))
        df_ponte["status_operacional"] = df_ponte["sk_tarefa"].map(status_map).fillna("Indefinido")

    return df_fato, df_ponte, df_mensal



def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Ponto de entrada público para carregar os dados.
    Verifica a data de modificação dos arquivos para invalidar o cache automaticamente.
    """
    mtime = _get_files_mtime()
    return _load_data_cached(mtime)


def clear_cache():
    """Limpa o cache do Streamlit manualmente."""
    st.cache_data.clear()


@st.cache_data(show_spinner=False)
def load_users() -> pd.DataFrame:
    """Carrega a dimensão cadastral de usuários do Ploomes CRM."""
    from app.config.settings import PATH_USUARIOS_PARQUET
    if PATH_USUARIOS_PARQUET.exists():
        return pd.read_parquet(PATH_USUARIOS_PARQUET)
    return pd.DataFrame()
