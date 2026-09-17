"""
Módulo de Gráficos de Ranking (Plotly) - Comercial Saavedra.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from app.config.settings import COLORS


def plot_ranking_horizontal(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    x_label: str = "Total",
    y_label: str = "",
    color_col: str | None = None
) -> go.Figure:
    """
    Renderiza um gráfico de barras horizontais ordenado com rótulos de dados.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Sem dados disponíveis")
        return fig

    # Ordena ascendente para a barra maior ficar no topo
    df_sorted = df.sort_values(by=x_col, ascending=True).copy()

    if color_col and color_col in df_sorted.columns:
        fig = px.bar(
            df_sorted,
            x=x_col,
            y=y_col,
            orientation="h",
            color=color_col,
            title=f"<b>{title}</b>",
            labels={x_col: x_label, y_col: y_label},
            color_continuous_scale="Blues",
            text=x_col
        )
    else:
        fig = px.bar(
            df_sorted,
            x=x_col,
            y=y_col,
            orientation="h",
            title=f"<b>{title}</b>",
            labels={x_col: x_label, y_col: y_label},
            color_discrete_sequence=[COLORS["primary"]],
            text=x_col
        )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=40, t=50, b=20),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=False)
    )
    return fig


def plot_users_comparison(df_user_kpis: pd.DataFrame) -> go.Figure:
    """
    Renderiza comparativo de produtividade dos consultores:
    Participações Totais vs. Titular Principal e Taxa de Conclusão.
    """
    if df_user_kpis.empty:
        return go.Figure()

    df_sorted = df_user_kpis.sort_values(by="participacoes_totais", ascending=True)

    fig = go.Figure()

    # Barra 1: Participações Totais
    fig.add_trace(go.Bar(
        y=df_sorted["nome_usuario"],
        x=df_sorted["participacoes_totais"],
        name="Participações Totais",
        orientation="h",
        marker=dict(color=COLORS["primary"]),
        text=df_sorted["participacoes_totais"],
        textposition="inside"
    ))

    # Barra 2: Como Titular / Principal
    fig.add_trace(go.Bar(
        y=df_sorted["nome_usuario"],
        x=df_sorted["como_titular"],
        name="Como Titular",
        orientation="h",
        marker=dict(color=COLORS["secondary"]),
        text=df_sorted["como_titular"],
        textposition="inside"
    ))

    fig.update_layout(
        barmode="group",
        title="<b>Volume de Tarefas por Consultor (Total vs. Titular)</b>",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Quantidade de Tarefas", showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(title="")
    )
    return fig
