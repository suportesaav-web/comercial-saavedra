"""
Página 1: Visão Geral Executiva - Comercial Saavedra.
"""

import sys
import os
from pathlib import Path

_current_file = Path(__file__).resolve()
_app_dir_norm = os.path.normcase(str(_current_file.parent.parent))
_project_root = str(_current_file.parent.parent.parent)

sys.path = [p for p in sys.path if os.path.normcase(os.path.abspath(p)) != _app_dir_norm]
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st
from app.config.settings import PAGE_CONFIG
from app.data.loader import load_data
from app.filters.sidebar_filters import render_sidebar_filters
from app.components.ui import render_header, render_filter_badge
from app.components.kpi_cards import render_overview_kpis
from app.components.insights import render_smart_insights
from app.analytics.metrics import compute_overview_kpis
from app.analytics.aggregations import aggregate_timeline, aggregate_by_type, aggregate_lead_time_bins
from app.charts.temporal import plot_monthly_timeline, plot_lead_time_chart
from app.charts.distribution import plot_donut_distribution

st.set_page_config(**PAGE_CONFIG)

df_fato, df_ponte, df_mensal = load_data()
df_filtered, df_ponte_filtered = render_sidebar_filters(df_fato, df_ponte)

render_header(
    title="Visão Geral — Produtividade e Eficiência Comercial",
    subtitle="Acompanhamento consolidado de atividades, metas operacionais e canais de relacionamento",
    icon="📈"
)

render_filter_badge(len(df_filtered), len(df_fato))
st.write("")

kpis = compute_overview_kpis(df_filtered)
render_overview_kpis(kpis)

st.write("")
render_smart_insights(df_filtered, df_ponte_filtered)

st.write("")
st.write("")

col1, col2 = st.columns([3, 2])

with col1:
    df_timeline = aggregate_timeline(df_filtered, freq="M")
    fig_timeline = plot_monthly_timeline(df_timeline)
    st.plotly_chart(fig_timeline, use_container_width=True)

with col2:
    df_tipo = aggregate_by_type(df_filtered)
    fig_donut = plot_donut_distribution(
        df_tipo,
        values_col="total_tarefas",
        names_col="tipo_tarefa",
        title="Mix de Atendimento por Canal"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.write("")

col3, col4 = st.columns([2, 3])

with col3:
    # Distribuição de Status Operacional
    df_status = df_filtered["status_operacional"].value_counts().reset_index()
    df_status.columns = ["status_operacional", "quantidade"]
    fig_status = plot_donut_distribution(
        df_status,
        values_col="quantidade",
        names_col="status_operacional",
        title="Distribuição por Status de Conclusão",
        hole=0.6
    )
    st.plotly_chart(fig_status, use_container_width=True)

with col4:
    # Lead Time de Agendamento
    df_lead = aggregate_lead_time_bins(df_filtered)
    fig_lead = plot_lead_time_chart(df_lead)
    st.plotly_chart(fig_lead, use_container_width=True)
