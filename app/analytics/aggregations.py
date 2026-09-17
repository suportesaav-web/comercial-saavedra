"""
Módulo de Agregações Analíticas - Comercial Saavedra.
Prepara DataFrames agregados para renderização em gráficos e tabelas.
"""

import pandas as pd
import numpy as np


def aggregate_by_client(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Agrega tarefas por cliente."""
    if df.empty:
        return pd.DataFrame()

    grp = df.groupby("nome_cliente", as_index=False).agg(
        total_tarefas=("sk_tarefa", "count"),
        finalizadas=("finalizada", lambda x: int(x.sum())),
        visitas=("tipo_tarefa", lambda x: int((x == "Visita").sum())),
        negocios=("titulo_negocio", "nunique")
    )
    grp["pendentes"] = grp["total_tarefas"] - grp["finalizadas"]
    grp["taxa_conclusao"] = ((grp["finalizadas"] / grp["total_tarefas"]) * 100).round(1)
    grp = grp.sort_values(by="total_tarefas", ascending=False).head(top_n)
    return grp


def aggregate_by_deal(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Agrega tarefas por título de negócio."""
    if df.empty:
        return pd.DataFrame()

    grp = df.groupby("titulo_negocio", as_index=False).agg(
        total_tarefas=("sk_tarefa", "count"),
        clientes_distintos=("nome_cliente", "nunique"),
        finalizadas=("finalizada", lambda x: int(x.sum()))
    )
    grp = grp.sort_values(by="total_tarefas", ascending=False).head(top_n)
    return grp


def aggregate_by_type(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega tarefas por modalidade de contato / tipo."""
    if df.empty:
        return pd.DataFrame()

    grp = df.groupby("tipo_tarefa", as_index=False).agg(
        total_tarefas=("sk_tarefa", "count"),
        finalizadas=("finalizada", lambda x: int(x.sum()))
    )
    grp["percentual"] = ((grp["total_tarefas"] / len(df)) * 100).round(1)
    grp = grp.sort_values(by="total_tarefas", ascending=False)
    return grp


def aggregate_timeline(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """
    Agrega evolução temporal das tarefas por mês ou semana.

    Args:
        df: DataFrame filtrado.
        freq: 'M' para mensal, 'W' para semanal.
    """
    if df.empty or "data_hora_evento" not in df.columns:
        return pd.DataFrame()

    df_temp = df.dropna(subset=["data_hora_evento"]).copy()
    if freq == "M":
        df_temp["periodo"] = df_temp["data_hora_evento"].dt.strftime("%Y-%m")
    else:
        df_temp["periodo"] = df_temp["data_hora_evento"].dt.to_period("W").astype(str)

    grp = df_temp.groupby(["periodo", "tipo_tarefa"], as_index=False).agg(
        total=("sk_tarefa", "count"),
        finalizadas=("finalizada", lambda x: int(x.sum()))
    )
    return grp


def aggregate_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria a matriz de tarefas por Dia da Semana vs Hora do Dia.
    """
    if df.empty:
        return pd.DataFrame()

    ordem_dias = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
        "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
    ]
    # Mapeamento para nomes padronizados em português
    map_dias = {
        "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
        "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo",
        "Segunda-feira": "Segunda", "Terça-feira": "Terça", "Quarta-feira": "Quarta",
        "Quinta-feira": "Quinta", "Sexta-feira": "Sexta", "Sábado": "Sábado", "Domingo": "Domingo"
    }

    df_temp = df.copy()
    df_temp["dia_nome"] = df_temp["dia_semana_nome"].map(map_dias).fillna(df_temp["dia_semana_nome"])

    # Filtra horas comerciais normais (07h às 19h)
    df_temp = df_temp[(df_temp["hora_do_dia"] >= 7) & (df_temp["hora_do_dia"] <= 19)]

    matrix = pd.pivot_table(
        df_temp,
        index="dia_nome",
        columns="hora_do_dia",
        values="sk_tarefa",
        aggfunc="count",
        fill_value=0
    )

    dias_ordenados = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    matrix = matrix.reindex([d for d in dias_ordenados if d in matrix.index])
    return matrix


def aggregate_lead_time_bins(df: pd.DataFrame) -> pd.DataFrame:
    """Classifica o Lead Time em faixas operacionais."""
    if df.empty or "lead_time_dias" not in df.columns:
        return pd.DataFrame()

    s = df["lead_time_dias"].dropna()
    bins = [-np.inf, -0.01, 0.5, 3.0, 7.0, 15.0, np.inf]
    labels = [
        "Retroativo (< 0 dias)",
        "Mesmo Dia (0 dias)",
        "Curto Prazo (1 a 3 dias)",
        "1 Semana (4 a 7 dias)",
        "2 Semanas (8 a 15 dias)",
        "Longo Prazo (> 15 dias)"
    ]
    categorized = pd.cut(s, bins=bins, labels=labels)
    df_bins = categorized.value_counts().reindex(labels).reset_index()
    df_bins.columns = ["faixa_lead_time", "quantidade"]
    df_bins["percentual"] = ((df_bins["quantidade"] / len(s)) * 100).round(1)
    return df_bins
