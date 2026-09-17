"""
Módulo de Gráficos de Distribuição (Plotly) - Comercial Saavedra.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from app.config.settings import COLORS


def plot_donut_distribution(
    df: pd.DataFrame,
    values_col: str,
    names_col: str,
    title: str,
    hole: float = 0.55
) -> go.Figure:
    """
    Renderiza um gráfico de rosca elegante para distribuição de categorias.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados disponíveis")
        return fig

    fig = px.pie(
        df,
        values=values_col,
        names=names_col,
        title=f"<b>{title}</b>",
        hole=hole,
        color_discrete_sequence=COLORS["palette_plotly"]
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#FFFFFF", width=2))
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig


def plot_heatmap_activity(matrix: pd.DataFrame) -> go.Figure:
    """
    Renderiza um mapa de calor (Heatmap) de dia da semana vs. hora do dia.
    """
    if matrix.empty:
        fig = go.Figure()
        return fig

    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=[f"{h:02d}h" for h in matrix.columns],
        y=matrix.index,
        colorscale="Teal",
        colorbar=dict(title="Tarefas"),
        hoverongaps=False
    ))

    fig.update_layout(
        title="<b>Mapa de Calor de Atividades (Dia da Semana × Horário do Dia)</b>",
        template="plotly_white",
        xaxis=dict(title="Horário de Início da Atividade", showgrid=False),
        yaxis=dict(title="Dia da Semana", showgrid=False),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig
