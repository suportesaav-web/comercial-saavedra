"""
Componente de Cards de KPIs - Comercial Saavedra.
"""

from typing import Dict, Any
import streamlit as st


def render_overview_kpis(kpis: Dict[str, Any]):
    """
    Renderiza os KPIs executivos demandados pela gestão em formato de painel executivo.
    """
    # Linha 1: Operação e Volume
    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

    with row1_col1:
        st.metric(
            label="Total de Tarefas",
            value=f"{kpis['total_tarefas']:,}".replace(",", "."),
            help="Total de atividades cadastradas no CRM para o período e filtros selecionados."
        )

    with row1_col2:
        st.metric(
            label="Tarefas Finalizadas",
            value=f"{kpis['finalizadas']:,}".replace(",", "."),
            delta=f"{kpis['taxa_conclusao_pct']}% Conclusão",
            delta_color="normal",
            help="Total de tarefas concluídas e taxa de efetividade de execução."
        )

    with row1_col3:
        pct_atraso = round((kpis['atrasadas'] / kpis['total_tarefas']) * 100, 1) if kpis['total_tarefas'] > 0 else 0
        st.metric(
            label="Tarefas em Atraso ⚠️",
            value=f"{kpis['atrasadas']:,}".replace(",", "."),
            delta=f"{pct_atraso}% em atraso" if kpis['atrasadas'] > 0 else "0% em dia",
            delta_color="inverse",
            help="Tarefas não finalizadas cuja data de agendamento já expirou."
        )

    with row1_col4:
        st.metric(
            label="Média de Tarefas Diárias",
            value=f"{kpis['media_diaria_geral']}",
            delta=f"{kpis['dias_distintos_com_tarefa']} dias ativos",
            delta_color="off",
            help="Média de tarefas realizadas por dia em que houve pelo menos uma atividade comercial registrada."
        )

    st.write("")

    # Linha 2: Cobertura Comercial e Visitas
    row2_col1, row2_col2, row2_col3 = st.columns(3)

    with row2_col1:
        st.metric(
            label="Visitas Presenciais (Tipo)",
            value=f"{kpis['visitas_presenciais']:,}".replace(",", "."),
            delta=f"{kpis['pct_visitas']}% do mix de canais",
            delta_color="normal",
            help="Principal canal de atuação da equipe comercial em campo."
        )

    with row2_col2:
        st.metric(
            label="Clientes Atendidos",
            value=f"{kpis['clientes_unicos']}",
            help="Total de clientes distintos (hospitais e clínicas) com interações no período."
        )

    with row2_col3:
        st.metric(
            label="Negócios Trabalhados",
            value=f"{kpis['negocios_unicos']}",
            help="Quantidade de oportunidades / demandas comerciais associadas às tarefas."
        )

    st.write("")

    # Linha 3: Gestão de Tempo, Contatos e Sincronização Google Calendar
    row3_col1, row3_col2, row3_col3 = st.columns(3)

    with row3_col1:
        st.metric(
            label="⏱️ Horas de Atendimento",
            value=f"{kpis['horas_totais']:.1f}h",
            delta=f"Média de {kpis['duracao_media_visita_min']:.0f} min/visita",
            delta_color="normal",
            help="Carga horária total dedicada a atendimentos a clientes calculada a partir do campo 'Duração'."
        )

    with row3_col2:
        st.metric(
            label="👤 Contatos Atualizados",
            value=f"{kpis['taxa_contato_atualizado_pct']}%",
            delta=f"{kpis['tarefas_com_contato']} de {kpis['total_tarefas']} tarefas",
            delta_color="normal" if kpis['taxa_contato_atualizado_pct'] >= 50 else "inverse",
            help="Percentual de tarefas em que o vendedor preencheu o campo 'Contato Relacionado'. Medida de conformidade cadastral."
        )

    with row3_col3:
        st.metric(
            label="📅 Sincronização Google Calendar",
            value=f"{kpis['taxa_sincronizacao_google_pct']}%",
            delta=f"{kpis['tarefas_sincronizadas_google']} integradas",
            delta_color="normal" if kpis['taxa_sincronizacao_google_pct'] >= 80 else "inverse",
            help="Percentual de tarefas criadas ou integradas via Google Calendar (presença de e-mail corporativo)."
        )
