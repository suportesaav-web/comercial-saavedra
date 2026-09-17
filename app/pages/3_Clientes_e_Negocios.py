"""
Página 3: Clientes & Negócios - Comercial Saavedra.
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
import pandas as pd
from app.config.settings import PAGE_CONFIG
from app.data.loader import load_data
from app.filters.sidebar_filters import render_sidebar_filters
from app.components.ui import render_header, render_filter_badge
from app.analytics.aggregations import aggregate_by_client, aggregate_by_deal
from app.charts.ranking import plot_ranking_horizontal

st.set_page_config(**PAGE_CONFIG)

df_fato, df_ponte, df_mensal = load_data()
df_filtered, df_ponte_filtered = render_sidebar_filters(df_fato, df_ponte)

render_header(
    title="Clientes & Oportunidades de Negócio",
    subtitle="Cobertura de contas hospitalares, intensidade de relacionamento e carteira de negócios",
    icon="🏥"
)

render_filter_badge(len(df_filtered), len(df_fato))
st.write("")

# Agregações por Cliente e por Negócio
df_clientes = aggregate_by_client(df_filtered, top_n=15)
df_negocios = aggregate_by_deal(df_filtered, top_n=15)

col1, col2 = st.columns(2)

with col1:
    fig_cli = plot_ranking_horizontal(
        df_clientes,
        x_col="total_tarefas",
        y_col="nome_cliente",
        title="Top 15 Clientes por Volume de Atividades",
        x_label="Total de Tarefas"
    )
    st.plotly_chart(fig_cli, use_container_width=True)

with col2:
    fig_deals = plot_ranking_horizontal(
        df_negocios,
        x_col="total_tarefas",
        y_col="titulo_negocio",
        title="Top 15 Negócios / Demandas Comerciais",
        x_label="Total de Tarefas"
    )
    st.plotly_chart(fig_deals, use_container_width=True)

st.write("")

# Tabela Detalhada de Contas Hospitalares
st.markdown("### 📋 Cobertura e Eficiência por Conta Hospitalar")

if not df_clientes.empty:
    df_cli_display = df_clientes.rename(columns={
        "nome_cliente": "Cliente / Hospital",
        "total_tarefas": "Total Atividades",
        "visitas": "Visitas Presenciais",
        "finalizadas": "Finalizadas",
        "pendentes": "Pendentes",
        "negocios": "Negócios Distintos",
        "taxa_conclusao": "Taxa Conclusão (%)"
    })

    st.dataframe(
        df_cli_display,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nenhum cliente atende aos filtros atuais.")
