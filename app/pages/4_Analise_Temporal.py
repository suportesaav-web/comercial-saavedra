"""
Página 4: Análise Temporal & Sazonalidade - Comercial Saavedra.
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
from app.analytics.aggregations import aggregate_timeline, aggregate_heatmap, aggregate_lead_time_bins
from app.charts.temporal import plot_monthly_timeline, plot_lead_time_chart
from app.charts.distribution import plot_heatmap_activity

st.set_page_config(**PAGE_CONFIG)

df_fato, df_ponte, df_mensal = load_data()
df_filtered, df_ponte_filtered = render_sidebar_filters(df_fato, df_ponte)

render_header(
    title="Análise Temporal & Padrões de Agendamento",
    subtitle="Tendências cronológicas, sazonalidade semanal, horários de pico e antecedência de agendamento",
    icon="📅"
)

render_filter_badge(len(df_filtered), len(df_fato))
st.write("")

# Seletor de Frequência Temporal
freq_opcao = st.radio(
    "Periodicidade da Tendência:",
    options=["Mensal", "Semanal"],
    horizontal=True
)
freq_code = "M" if freq_opcao == "Mensal" else "W"

df_timeline = aggregate_timeline(df_filtered, freq=freq_code)
fig_time = plot_monthly_timeline(df_timeline)
st.plotly_chart(fig_time, use_container_width=True)

st.write("")

# Heatmap de Atividades (Dia da Semana x Horário)
st.markdown("### 🕒 Mapa de Calor: Dias da Semana × Horários de Agendamento")
st.caption("Identifica as faixas de horário e dias com maior concentração de interações com clientes.")

matrix_heat = aggregate_heatmap(df_filtered)
fig_heat = plot_heatmap_activity(matrix_heat)
st.plotly_chart(fig_heat, use_container_width=True)

st.write("")

# Análise de Lead Time
st.markdown("### ⏱️ Antecedência de Agendamento (Lead Time)")
st.caption("Diferença em dias entre o momento em que a tarefa foi cadastrada no CRM e o momento agendado para realização.")

df_lead = aggregate_lead_time_bins(df_filtered)
fig_lead = plot_lead_time_chart(df_lead)
st.plotly_chart(fig_lead, use_container_width=True)
