"""
Componente de Insights & Alertas Inteligentes da Gestão - Comercial Saavedra.
Analisa a base filtrada e gera diagnósticos acionáveis automáticos em tempo real.
"""

import pandas as pd
import streamlit as st


def render_smart_insights(df_filtered: pd.DataFrame, df_ponte_filtered: pd.DataFrame):
    """
    Renderiza um painel moderno com diagnósticos e recomendações executivas
    baseadas no comportamento real da equipe comercial no período filtrado.
    """
    if df_filtered.empty:
        return

    # Cálculos operacionais
    total_tarefas = len(df_filtered)
    atrasadas = df_filtered[df_filtered["status_operacional"] == "Atrasada"]
    qtd_atrasadas = len(atrasadas)
    pct_atrasadas = (qtd_atrasadas / total_tarefas * 100) if total_tarefas > 0 else 0

    # Conformidade de Contato
    if "has_contato_preenchido" in df_filtered.columns:
        pct_contato = df_filtered["has_contato_preenchido"].mean() * 100
        qtd_sem_contato = total_tarefas - df_filtered["has_contato_preenchido"].sum()
    else:
        pct_contato = 100
        qtd_sem_contato = 0

    # Sincronização Google Calendar
    if "is_sincronizado_google" in df_filtered.columns:
        pct_sync = df_filtered["is_sincronizado_google"].mean() * 100
    else:
        pct_sync = 100

    # Concentração de Vendedor em Atrasos
    top_atrasado_user = "Nenhum"
    top_atrasado_qtd = 0
    if qtd_atrasadas > 0 and not df_ponte_filtered.empty:
        ponte_atrasada = df_ponte_filtered[df_ponte_filtered["sk_tarefa"].isin(atrasadas["sk_tarefa"])]
        if not ponte_atrasada.empty:
            contagem_atraso = ponte_atrasada["nome_usuario"].value_counts()
            top_atrasado_user = contagem_atraso.index[0]
            top_atrasado_qtd = contagem_atraso.iloc[0]

    # Cliente mais visitado
    top_cliente = "Nenhum"
    top_cliente_qtd = 0
    if not df_filtered.empty and "nome_cliente" in df_filtered.columns:
        contagem_cli = df_filtered[df_filtered["nome_cliente"] != "Cliente Não Informado"]["nome_cliente"].value_counts()
        if not contagem_cli.empty:
            top_cliente = contagem_cli.index[0]
            top_cliente_qtd = contagem_cli.iloc[0]

    # Renderização visual
    st.markdown("### 💡 Diagnósticos e Alertas da Gestão Comercial")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if qtd_atrasadas == 0:
            st.success(
                f"**✅ Fila Operacional em Dia**\n\n"
                f"Nenhuma tarefa atrasada pendente no período selecionado. Efetividade máxima de execução."
            )
        else:
            st.error(
                f"**🚨 Atenção: {qtd_atrasadas} Tarefas em Atraso ({pct_atrasadas:.1f}%)**\n\n"
                f"Vendedor com maior volume pendente: **{top_atrasado_user}** ({top_atrasado_qtd} tarefas). "
                f"Recomenda-se alinhamento de prioridades para baixa no CRM."
            )

    with col2:
        if pct_contato >= 70:
            st.success(
                f"**🎯 Excelente Qualidade de Cadastro**\n\n"
                f"**{pct_contato:.1f}%** das tarefas possuem contato médico/clínico preenchido. Base enriquecida."
            )
        else:
            st.warning(
                f"**📋 Conformidade de Contatos: {pct_contato:.1f}%**\n\n"
                f"**{int(qtd_sem_contato)}** tarefas estão sem interlocutor cadastrado. "
                f"Cobrar vendedores para registrar o nome do decisor nas próximas atividades."
            )

    with col3:
        if pct_sync >= 85:
            st.info(
                f"**📅 Sincronização Google: {pct_sync:.1f}%**\n\n"
                f"Integração de agendas operando normalmente. Hospital com maior foco de atendimento: **{top_cliente}** ({top_cliente_qtd} ações)."
            )
        else:
            st.warning(
                f"**⚠️ Integração de Calendário: {pct_sync:.1f}%**\n\n"
                f"Abaixo da meta corporativa (85%). Incentivar consultores a manterem o e-mail Google Calendar ativo."
            )
