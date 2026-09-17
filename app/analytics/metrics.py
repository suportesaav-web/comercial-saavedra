"""
Módulo de Métricas e KPIs - Comercial Saavedra.
Funções puras para cálculo de indicadores comerciais e operacionais alinhadas às demandas dos gestores:
- Total de tarefas realizadas por vendedor
- Total de tarefas finalizadas por vendedor
- Top clientes com mais tarefas
- Tarefas em atraso
- Médias de tarefas diárias
- Tempo sem tarefas na semana (dias úteis sem atividade)
- Duração das tarefas e visitas (tempo dedicado)
- Conformidade de preenchimento de Contatos
- Sincronização com o Google Calendar
- Tipos de tarefas e Negócios
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


def compute_overview_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula os KPIs macro da base de tarefas filtrada com foco na visão gerencial.

    Args:
        df: DataFrame de tarefas filtrado.

    Returns:
        Dict com os valores calculados formatados e brutos.
    """
    total = len(df)
    if total == 0:
        return {
            "total_tarefas": 0,
            "finalizadas": 0,
            "pendentes": 0,
            "atrasadas": 0,
            "agendadas": 0,
            "taxa_conclusao_pct": 0.0,
            "visitas_presenciais": 0,
            "pct_visitas": 0.0,
            "clientes_unicos": 0,
            "negocios_unicos": 0,
            "horas_totais": 0.0,
            "duracao_media_visita_min": 0.0,
            "tarefas_com_contato": 0,
            "taxa_contato_atualizado_pct": 0.0,
            "tarefas_sincronizadas_google": 0,
            "taxa_sincronizacao_google_pct": 0.0,
            "dias_distintos_com_tarefa": 0,
            "media_diaria_geral": 0.0,
            "lead_time_medio_dias": 0.0,
            "tarefas_conjuntas": 0,
            "pct_tarefas_conjuntas": 0.0
        }

    finalizadas = int(df["finalizada"].sum())
    pendentes = total - finalizadas

    # Tarefas em atraso (Finalizada = False e Data < Hoje)
    if "status_operacional" in df.columns:
        atrasadas = int((df["status_operacional"] == "Atrasada").sum())
        agendadas = int((df["status_operacional"] == "Agendada").sum())
    else:
        atrasadas = pendentes
        agendadas = 0

    taxa_conclusao = round((finalizadas / total) * 100, 1)

    visitas = int((df["tipo_tarefa"] == "Visita").sum())
    pct_visitas = round((visitas / total) * 100, 1)

    clientes = int(df["nome_cliente"].nunique())
    negocios = int(df["titulo_negocio"].nunique())

    # Métrica de Duração e Tempo
    if "duracao_horas" in df.columns:
        horas_totais = round(float(df["duracao_horas"].sum()), 1)
    else:
        horas_totais = 0.0

    df_visitas = df[df["tipo_tarefa"] == "Visita"]
    if not df_visitas.empty and "duracao_minutos" in df_visitas.columns:
        dur_media_visita = round(float(df_visitas["duracao_minutos"].mean()), 1)
    else:
        dur_media_visita = 0.0

    # Conformidade de Contato Relacionado
    if "has_contato_preenchido" in df.columns:
        tarefas_com_contato = int(df["has_contato_preenchido"].sum())
        taxa_contato = round((tarefas_com_contato / total) * 100, 1)
    else:
        tarefas_com_contato = 0
        taxa_contato = 0.0

    # Sincronização Google Calendar
    if "is_sincronizado_google" in df.columns:
        sincronizadas_google = int(df["is_sincronizado_google"].sum())
        taxa_google = round((sincronizadas_google / total) * 100, 1)
    else:
        sincronizadas_google = 0
        taxa_google = 0.0

    # Média de tarefas diárias
    dias_distintos = int(df["data_evento"].nunique()) if "data_evento" in df.columns else 1
    media_diaria_geral = round(total / dias_distintos, 1) if dias_distintos > 0 else 0.0

    # Lead time médio
    valid_lead_times = df["lead_time_dias"].dropna()
    lead_time_medio = round(float(valid_lead_times.mean()), 1) if not valid_lead_times.empty else 0.0

    conjuntas = int(df["is_tarefa_conjunta"].sum()) if "is_tarefa_conjunta" in df.columns else 0
    pct_conjuntas = round((conjuntas / total) * 100, 1)

    return {
        "total_tarefas": total,
        "finalizadas": finalizadas,
        "pendentes": pendentes,
        "atrasadas": atrasadas,
        "agendadas": agendadas,
        "taxa_conclusao_pct": taxa_conclusao,
        "visitas_presenciais": visitas,
        "pct_visitas": pct_visitas,
        "clientes_unicos": clientes,
        "negocios_unicos": negocios,
        "horas_totais": horas_totais,
        "duracao_media_visita_min": dur_media_visita,
        "tarefas_com_contato": tarefas_com_contato,
        "taxa_contato_atualizado_pct": taxa_contato,
        "tarefas_sincronizadas_google": sincronizadas_google,
        "taxa_sincronizacao_google_pct": taxa_google,
        "dias_distintos_com_tarefa": dias_distintos,
        "media_diaria_geral": media_diaria_geral,
        "lead_time_medio_dias": lead_time_medio,
        "tarefas_conjuntas": conjuntas,
        "pct_tarefas_conjuntas": pct_conjuntas
    }


def compute_user_kpis(df_ponte_filtered: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula os indicadores detalhados por vendedor a partir da tabela ponte:
    - total de tarefas realizadas por vendedor
    - total de tarefas finalizadas por vendedor
    - tarefas em atraso
    - média de tarefas diárias
    - tempo sem tarefas na semana (dias úteis sem atividade comercial por semana)
    - horas totais e duração média
    - conformidade de preenchimento de contato
    - taxa de sincronização com o Google Calendar
    """
    if df_ponte_filtered.empty:
        return pd.DataFrame()

    df_temp = df_ponte_filtered.copy()
    df_temp["data_dt"] = pd.to_datetime(df_temp["data_evento"])
    df_temp["dia_semana_num"] = df_temp["data_dt"].dt.dayofweek  # 0=Segunda, 4=Sexta
    df_temp["ano_semana"] = df_temp["data_dt"].dt.strftime("%Y-W%W")

    # 1. Agrupamento por usuário
    user_grp = df_temp.groupby("nome_usuario", as_index=False).agg(
        participacoes_totais=("sk_tarefa", "count"),
        como_titular=("is_usuario_principal", lambda x: int(x.sum())),
        tarefas_finalizadas=("finalizada", lambda x: int(x.sum())),
        visitas_presenciais=("tipo_tarefa", lambda x: int((x == "Visita").sum())),
        horas_totais=("duracao_horas", lambda x: round(float(x.sum()), 1)) if "duracao_horas" in df_temp.columns else ("sk_tarefa", lambda x: 0.0),
        duracao_media_min=("duracao_minutos", lambda x: round(float(x.mean()), 1)) if "duracao_minutos" in df_temp.columns else ("sk_tarefa", lambda x: 0.0),
        contatos_preenchidos=("has_contato_preenchido", lambda x: int(x.sum())) if "has_contato_preenchido" in df_temp.columns else ("sk_tarefa", lambda x: 0),
        sincronizadas_google=("is_sincronizado_google", lambda x: int(x.sum())) if "is_sincronizado_google" in df_temp.columns else ("sk_tarefa", lambda x: 0),
        clientes_atendidos=("nome_cliente", "nunique"),
        dias_ativos=("data_evento", "nunique")
    )

    user_grp["tarefas_pendentes"] = user_grp["participacoes_totais"] - user_grp["tarefas_finalizadas"]
    user_grp["taxa_conclusao_pct"] = (
        (user_grp["tarefas_finalizadas"] / user_grp["participacoes_totais"]) * 100
    ).round(1)

    user_grp["taxa_contato_atualizado_pct"] = (
        (user_grp["contatos_preenchidos"] / user_grp["participacoes_totais"]) * 100
    ).round(1)

    user_grp["taxa_sincronizacao_google_pct"] = (
        (user_grp["sincronizadas_google"] / user_grp["participacoes_totais"]) * 100
    ).round(1)

    # 2. Média de tarefas diárias por dia ativo do vendedor
    user_grp["media_tarefas_diarias"] = (
        user_grp["participacoes_totais"] / user_grp["dias_ativos"]
    ).round(1)

    # 3. Tempo sem tarefas na semana
    dias_uteis_com_tarefa = (
        df_temp[df_temp["dia_semana_num"] <= 4]
        .groupby(["nome_usuario", "ano_semana"])["dia_semana_num"]
        .nunique()
        .reset_index()
    )
    dias_uteis_com_tarefa["dias_sem_tarefa"] = 5 - dias_uteis_com_tarefa["dia_semana_num"]
    media_ociosa = (
        dias_uteis_com_tarefa.groupby("nome_usuario")["dias_sem_tarefa"]
        .mean()
        .round(1)
        .reset_index()
        .rename(columns={"dias_sem_tarefa": "media_dias_sem_tarefa_semana"})
    )

    media_dias_com_tarefa = (
        dias_uteis_com_tarefa.groupby("nome_usuario")["dia_semana_num"]
        .mean()
        .round(1)
        .reset_index()
        .rename(columns={"dia_semana_num": "media_dias_com_tarefa_semana"})
    )

    user_grp = user_grp.merge(media_dias_com_tarefa, on="nome_usuario", how="left")
    user_grp = user_grp.merge(media_ociosa, on="nome_usuario", how="left")
    user_grp["media_dias_sem_tarefa_semana"] = user_grp["media_dias_sem_tarefa_semana"].fillna(5.0)
    user_grp["media_dias_com_tarefa_semana"] = user_grp["media_dias_com_tarefa_semana"].fillna(0.0)

    user_grp = user_grp.sort_values(by="participacoes_totais", ascending=False).reset_index(drop=True)
    return user_grp


def get_overdue_tasks(df_fato: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna as tarefas que estão em atraso com dados de auditoria e cálculo de dias de atraso.
    """
    if df_fato.empty or "status_operacional" not in df_fato.columns:
        return pd.DataFrame()

    df_atrasadas = df_fato[df_fato["status_operacional"] == "Atrasada"].copy()
    if df_atrasadas.empty:
        return pd.DataFrame()

    hoje = pd.Timestamp.now()
    df_atrasadas["dias_de_atraso"] = (hoje - df_atrasadas["data_hora_evento"]).dt.days
    cols = [
        "sk_tarefa",
        "data_evento_str",
        "dias_de_atraso",
        "titulo",
        "duracao_minutos",
        "nome_cliente",
        "titulo_negocio",
        "usuario_principal",
        "tipo_tarefa",
        "contatos_relacionados",
        "is_sincronizado_google",
        "marcadores"
    ]
    cols_exist = [c for c in cols if c in df_atrasadas.columns]
    return df_atrasadas[cols_exist].sort_values(by="dias_de_atraso", ascending=False).reset_index(drop=True)
