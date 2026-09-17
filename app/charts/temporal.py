"""
Módulo de Gráficos Temporais (Plotly) - Comercial Saavedra.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from app.config.settings import COLORS


def plot_monthly_timeline(df_timeline: pd.DataFrame) -> go.Figure:
    """
    Renderiza a evolução temporal de tarefas por mês e tipo.
    """
    if df_timeline.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados para o período selecionado")
        return fig

    # Gráfico de barras empilhadas por tipo de tarefa
    fig = px.bar(
        df_timeline,
        x="periodo",
        y="total",
        color="tipo_tarefa",
        title="<b>Evolução Mensal de Tarefas por Canal / Tipo</b>",
        labels={"periodo": "Mês do Evento", "total": "Volume de Tarefas", "tipo_tarefa": "Canal"},
        color_discrete_sequence=COLORS["palette_plotly"]
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickangle=-45, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
    )
    return fig


def plot_lead_time_chart(df_bins: pd.DataFrame) -> go.Figure:
    """
    Renderiza o gráfico de faixas de Lead Time (antecedência do agendamento).
    """
    if df_bins.empty:
        fig = go.Figure()
        return fig

    fig = px.bar(
        df_bins,
        x="faixa_lead_time",
        y="quantidade",
        text="percentual",
        title="<b>Distribuição de Lead Time (Dias entre Criação no CRM e Realização)</b>",
        labels={"faixa_lead_time": "Faixa de Antecedência", "quantidade": "Quantidade de Tarefas"},
        color_discrete_sequence=[COLORS["primary"]]
    )

    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
    )
    return fig
