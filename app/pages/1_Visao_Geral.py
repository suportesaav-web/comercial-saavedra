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
from app.components.ui import render_header, render_filter_badge, render_anomaly_alert
from app.components.kpi_cards import render_overview_kpis
from app.components.insights import render_smart_insights
from app.analytics.metrics import compute_overview_kpis, compute_user_kpis, get_overdue_tasks
from app.analytics.aggregations import aggregate_timeline, aggregate_by_type, aggregate_by_client, aggregate_by_deal, aggregate_lead_time_bins
from app.charts.temporal import plot_monthly_timeline, plot_lead_time_chart
from app.charts.distribution import plot_donut_distribution
from app.charts.ranking import plot_ranking_horizontal, plot_users_comparison

st.set_page_config(**PAGE_CONFIG)

df_fato, df_ponte, df_mensal = load_data()
df_filtered, df_ponte_filtered = render_sidebar_filters(df_fato, df_ponte)

render_header(
    title="Visão Geral — Produtividade e Eficiência Comercial",
    subtitle="Acompanhamento consolidado de atividades, metas operacionais e canais de relacionamento",
    icon="📈"
)

# Badges e Alertas
col_badge, col_info = st.columns([2, 3])
with col_badge:
    render_filter_badge(len(df_filtered), len(df_fato))
with col_info:
    qtd_anomalas = int(df_fato["is_data_futura_anomala"].sum())
    render_anomaly_alert(qtd_anomalas)

st.write("")

kpis = compute_overview_kpis(df_filtered)
render_overview_kpis(kpis)

st.write("")
render_smart_insights(df_filtered, df_ponte_filtered)
st.write("")

# Alerta Rápido de Tarefas em Atraso
if kpis["atrasadas"] > 0:
    with st.expander(f"🚨 Atenção: Existem {kpis['atrasadas']} Tarefas em Atraso (Clique para visualizar detalhes)", expanded=False):
        df_overdue = get_overdue_tasks(df_filtered)
        if not df_overdue.empty:
            st.dataframe(
                df_overdue.rename(columns={
                    "data_evento_str": "Data Agendada",
                    "dias_de_atraso": "Dias de Atraso",
                    "titulo": "Título",
                    "nome_cliente": "Cliente",
                    "titulo_negocio": "Negócio",
                    "usuario_principal": "Responsável",
                    "tipo_tarefa": "Tipo"
                })[["Data Agendada", "Dias de Atraso", "Título", "Cliente", "Negócio", "Responsável", "Tipo"]],
                use_container_width=True,
                hide_index=True
            )

st.write("")
st.write("")

st.markdown("### 📈 Tendência Temporal e Mix de Atendimento")
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

st.write("")

# Seção de Vendedores: Realizadas, Finalizadas e Médias
st.markdown("### 👥 Produtividade por Vendedor (Realizadas, Finalizadas e Média Diária)")
df_users = compute_user_kpis(df_ponte_filtered)

if not df_users.empty:
    col_v1, col_v2 = st.columns([3, 2])
    with col_v1:
        fig_users = plot_users_comparison(df_users)
        st.plotly_chart(fig_users, use_container_width=True)
    with col_v2:
        fig_media_v = plot_ranking_horizontal(
            df_users,
            x_col="media_tarefas_diarias",
            y_col="nome_usuario",
            title="Média de Tarefas Diárias por Vendedor",
            x_label="Tarefas / Dia Ativo"
        )
        st.plotly_chart(fig_media_v, use_container_width=True)

    # Tabela Resumida da Equipe
    st.dataframe(
        df_users[[
            "nome_usuario",
            "participacoes_totais",
            "tarefas_finalizadas",
            "tarefas_pendentes",
            "taxa_conclusao_pct",
            "media_tarefas_diarias",
            "media_dias_sem_tarefa_semana"
        ]].rename(columns={
            "nome_usuario": "Vendedor",
            "participacoes_totais": "Total Realizadas",
            "tarefas_finalizadas": "Finalizadas",
            "tarefas_pendentes": "Pendentes / Atrasadas",
            "taxa_conclusao_pct": "% Conclusão",
            "media_tarefas_diarias": "Média Diária",
            "media_dias_sem_tarefa_semana": "Dias s/ Tarefa (Semana)"
        }),
        use_container_width=True,
        hide_index=True
    )

st.write("")

# Top Clientes com Mais Tarefas & Principais Negócios
st.markdown("### 🏥 Top Clientes com Mais Tarefas e Principais Negócios")
col_cli, col_deal = st.columns(2)

with col_cli:
    df_top_clients = aggregate_by_client(df_filtered, top_n=10)
    fig_top_cli = plot_ranking_horizontal(
        df_top_clients,
        x_col="total_tarefas",
        y_col="nome_cliente",
        title="Top 10 Clientes com Mais Tarefas",
        x_label="Total de Tarefas"
    )
    st.plotly_chart(fig_top_cli, use_container_width=True)

with col_deal:
    df_top_deals = aggregate_by_deal(df_filtered, top_n=10)
    fig_top_deals = plot_ranking_horizontal(
        df_top_deals,
        x_col="total_tarefas",
        y_col="titulo_negocio",
        title="Top 10 Negócios Trabalhados",
        x_label="Total de Tarefas"
    )
    st.plotly_chart(fig_top_deals, use_container_width=True)

st.divider()

# Links para Páginas Detalhadas
st.markdown("### 🧭 Detalhe as Análises pelas Páginas Específicas:")
lcol1, lcol2, lcol3, lcol4 = st.columns(4)

with lcol1:
    st.info("👥 **Vendedores & Equipe:** Análise de ociosidade semanal, taxas de conclusão e criadores.")
with lcol2:
    st.info("🏥 **Clientes & Negócios:** Cobertura de carteira e detalhamento por hospital.")
with lcol3:
    st.info("📅 **Análise Temporal:** Mapa de calor de horários de pico e dias da semana.")
with lcol4:
    st.info("📋 **Detalhamento Operacional:** Busca textual de tarefas e download em CSV/Excel.")
