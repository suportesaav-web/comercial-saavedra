"""
Página 2: Vendedores & Equipe Comercial - Comercial Saavedra.
Foco nos indicadores demandados pela gestão:
- Total de tarefas realizadas por vendedor
- Total de tarefas finalizadas por vendedor
- Tarefas em atraso por vendedor
- Médias de tarefas diárias
- Tempo sem tarefas na semana (dias úteis sem atividade comercial)
- Horas dedicadas e duração média
- Conformidade de atualização de Contato
- Sincronização com Google Calendar
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
from app.config.settings import PAGE_CONFIG, COLORS, is_commercial_user
from app.data.loader import load_data
from app.filters.sidebar_filters import render_sidebar_filters
from app.components.ui import render_header, render_filter_badge
from app.analytics.metrics import compute_user_kpis, get_overdue_tasks
from app.charts.ranking import plot_users_comparison, plot_ranking_horizontal
from app.charts.distribution import plot_donut_distribution

st.set_page_config(**PAGE_CONFIG)

df_fato, df_ponte, df_mensal = load_data()
df_filtered, df_ponte_filtered = render_sidebar_filters(df_fato, df_ponte)

render_header(
    title="Desempenho da Força de Vendas e Consultores",
    subtitle="Acompanhamento detalhado de tarefas realizadas, finalizadas, atrasadas, médias diárias, ociosidade, horas e atualização de contatos",
    icon="👥"
)

render_filter_badge(len(df_filtered), len(df_fato))
st.write("")

# Métricas calculadas por vendedor
df_users = compute_user_kpis(df_ponte_filtered)

if not df_users.empty:
    df_users = df_users[df_users["nome_usuario"].apply(is_commercial_user)].copy()

if df_users.empty:
    st.info("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# 1. Cards de Resumo da Equipe
col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
total_realizadas = int(df_users["participacoes_totais"].sum())
total_finalizadas = int(df_users["tarefas_finalizadas"].sum())
total_pendentes = int(df_users["tarefas_pendentes"].sum())
media_diaria_equipe = round(float(df_users["media_tarefas_diarias"].mean()), 1)
tempo_sem_tarefa_medio = round(float(df_users["media_dias_sem_tarefa_semana"].mean()), 1)

with col_kpi1:
    st.metric("Total de Realizações", f"{total_realizadas:,}".replace(",", "."))
with col_kpi2:
    st.metric("Total de Finalizadas", f"{total_finalizadas:,}".replace(",", "."))
with col_kpi3:
    st.metric("Pendentes / Atrasadas", f"{total_pendentes:,}".replace(",", "."))
with col_kpi4:
    st.metric("Média Diária Equipe", f"{media_diaria_equipe} tarefas/dia")
with col_kpi5:
    st.metric("Tempo sem Tarefa na Semana", f"{tempo_sem_tarefa_medio} dias/sem", help="Média de dias úteis (Seg-Sex) sem tarefas registradas no CRM.")

st.write("")
st.write("")

# 2. Gráfico Principal: Volume Realizado vs. Como Titular
st.markdown("### 📊 1. Total de Tarefas Realizadas por Vendedor")
st.caption("Compara as participações totais de cada consultor com as tarefas em que ele foi cadastrado como titular principal.")
fig_comp = plot_users_comparison(df_users)
st.plotly_chart(fig_comp, use_container_width=True)

st.write("")

# 3. Gráficos de Média Diária e Tempo sem Tarefa na Semana
col_g1, col_g2 = st.columns(2)

with col_g1:
    fig_media = plot_ranking_horizontal(
        df_users,
        x_col="media_tarefas_diarias",
        y_col="nome_usuario",
        title="Média de Tarefas Diárias por Consultor (Dias Ativos)",
        x_label="Tarefas / Dia Ativo"
    )
    st.plotly_chart(fig_media, use_container_width=True)

with col_g2:
    fig_sem_tarefa = plot_ranking_horizontal(
        df_users,
        x_col="media_dias_sem_tarefa_semana",
        y_col="nome_usuario",
        title="Tempo Sem Tarefas na Semana (Dias Úteis Ociosos / Semana)",
        x_label="Dias sem Tarefa (0 a 5 dias)",
        color_col="media_dias_sem_tarefa_semana"
    )
    st.plotly_chart(fig_sem_tarefa, use_container_width=True)

st.write("")

# 4. Horas Dedicadas e Conformidade de Preenchimento de Contatos
st.markdown("### ⏱️ 2. Horas Dedicadas e Atualização de Contatos por Vendedor")
col_h1, col_h2 = st.columns(2)

with col_h1:
    fig_horas = plot_ranking_horizontal(
        df_users,
        x_col="horas_totais",
        y_col="nome_usuario",
        title="Horas Totais Dedicadas a Atendimentos (Horas)",
        x_label="Horas de Atendimento",
        color_col="horas_totais"
    )
    st.plotly_chart(fig_horas, use_container_width=True)

with col_h2:
    fig_contato = plot_ranking_horizontal(
        df_users,
        x_col="taxa_contato_atualizado_pct",
        y_col="nome_usuario",
        title="Conformidade: Tarefas com Contato Atualizado (%)",
        x_label="% de Tarefas com Contato Informado",
        color_col="taxa_contato_atualizado_pct"
    )
    st.plotly_chart(fig_contato, use_container_width=True)

st.write("")

# 5. Tabela Gerencial Completa por Vendedor
st.markdown("### 📋 3. Tabela Gerencial Consolidada por Vendedor")

df_users_display = df_users.rename(columns={
    "nome_usuario": "Vendedor / Consultor",
    "participacoes_totais": "Total Realizadas",
    "como_titular": "Como Titular",
    "tarefas_finalizadas": "Finalizadas",
    "tarefas_pendentes": "Pendentes",
    "taxa_conclusao_pct": "% Conclusão",
    "visitas_presenciais": "Visitas",
    "horas_totais": "Horas Totais",
    "duracao_media_min": "Duração Média (min)",
    "taxa_contato_atualizado_pct": "% Contato Preenchido",
    "taxa_sincronizacao_google_pct": "% Google Sync",
    "clientes_atendidos": "Clientes",
    "media_tarefas_diarias": "Média Diária",
    "media_dias_com_tarefa_semana": "Dias Ativos/Sem",
    "media_dias_sem_tarefa_semana": "Dias s/ Tarefa/Sem"
})

st.dataframe(
    df_users_display[[
        "Vendedor / Consultor",
        "Total Realizadas",
        "Finalizadas",
        "Pendentes",
        "% Conclusão",
        "Visitas",
        "Horas Totais",
        "Duração Média (min)",
        "% Contato Preenchido",
        "% Google Sync",
        "Clientes",
        "Média Diária",
        "Dias Ativos/Sem",
        "Dias s/ Tarefa/Sem"
    ]],
    use_container_width=True,
    hide_index=True
)

st.write("")

# 6. Seção de Tarefas em Atraso (Auditoria Gerencial)
st.markdown("### 🚨 4. Auditoria de Tarefas em Atraso")
st.caption("Tarefas cuja data de execução já expirou e ainda não foram marcadas como 'Finalizada = True' no CRM.")

df_atrasadas = get_overdue_tasks(df_filtered)

if not df_atrasadas.empty:
    st.warning(f"⚠️ Foram encontradas **{len(df_atrasadas)} tarefas em atraso** para o período selecionado.")
    
    df_atrasadas_display = df_atrasadas.rename(columns={
        "data_evento_str": "Data Agendada",
        "dias_de_atraso": "Dias em Atraso",
        "titulo": "Título da Tarefa",
        "duracao_minutos": "Duração (min)",
        "nome_cliente": "Cliente",
        "titulo_negocio": "Negócio",
        "usuario_principal": "Responsável",
        "tipo_tarefa": "Canal / Tipo",
        "contatos_relacionados": "Contato",
        "marcadores": "Tags"
    })
    
    cols_show = [c for c in ["Data Agendada", "Dias em Atraso", "Título da Tarefa", "Duração (min)", "Cliente", "Negócio", "Responsável", "Canal / Tipo", "Contato"] if c in df_atrasadas_display.columns]
    st.dataframe(
        df_atrasadas_display[cols_show],
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("🎉 Parabéns! Não há tarefas em atraso no período filtrado.")

st.write("")

# 7. Análise de Origem: Criador vs. Executor e Google Calendar
st.markdown("### 🔄 5. Origem do Agendamento e Google Calendar")
col_criador1, col_criador2 = st.columns([2, 3])

with col_criador1:
    if "is_sincronizado_google" in df_filtered.columns:
        df_sync = df_filtered["is_sincronizado_google"].value_counts().reset_index()
    else:
        df_sync = pd.DataFrame({"is_sincronizado_google": [False], "count": [len(df_filtered)]})
    df_sync.columns = ["sincronizado", "total"]
    df_sync["rotulo"] = df_sync["sincronizado"].map({
        True: "Sincronizado (Google Calendar)",
        False: "Criado Manualmente no CRM"
    })
    fig_sync = plot_donut_distribution(
        df_sync,
        values_col="total",
        names_col="rotulo",
        title="Integração Google Calendar",
        hole=0.6
    )
    st.plotly_chart(fig_sync, use_container_width=True)

with col_criador2:
    df_criadores_top = df_filtered["criador"].value_counts().head(8).reset_index()
    df_criadores_top.columns = ["criador", "total_criadas"]
    fig_criadores = plot_ranking_horizontal(
        df_criadores_top,
        x_col="total_criadas",
        y_col="criador",
        title="Top Criadores de Tarefas no CRM",
        x_label="Tarefas Criadas"
    )
    st.plotly_chart(fig_criadores, use_container_width=True)
