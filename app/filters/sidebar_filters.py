from typing import Tuple
from datetime import date, timedelta
import pandas as pd
import streamlit as st


def render_sidebar_filters(df_fato: pd.DataFrame, df_ponte: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Renderiza os filtros na barra lateral e retorna os DataFrames devidamente filtrados.

    Args:
        df_fato: DataFrame completo da fato.
        df_ponte: DataFrame da tabela-ponte de usuários.

    Returns:
        Tuple contendo (df_fato_filtrado, df_ponte_filtrado).
    """
    st.sidebar.image(
        "https://raw.githubusercontent.com/feathericons/feather/master/icons/activity.svg",
        width=40
    )
    st.sidebar.title("Filtros Globais")
    st.sidebar.caption("Selecione os parâmetros para refinar as análises:")

    # 1. Checkbox para datas anômalas (> 2026)
    incluir_anomalas = st.sidebar.checkbox(
        "Incluir datas anômalas (> 2026)",
        value=False,
        help="Exibe tarefas registradas com anos distantes (ex: 2027 e 2032)."
    )

    # Base de trabalho inicial
    if not incluir_anomalas:
        df_base = df_fato[~df_fato["is_data_futura_anomala"]].copy()
    else:
        df_base = df_fato.copy()

    # 2. Seletor de Período Temporal (Padrão: Últimos 30 Dias)
    datas_validas = pd.to_datetime(df_base["data_evento"]).dropna()
    min_date = datas_validas.min().date() if not datas_validas.empty else date(2025, 1, 1)
    max_date = datas_validas.max().date() if not datas_validas.empty else date(2026, 12, 31)

    # Data de referência de hoje: 2026-09-17 (fixado nos últimos 30 dias por padrão)
    hoje = min(date.today(), max_date)
    default_start = max(min_date, hoje - timedelta(days=30))
    default_end = hoje

    periodo_selecionado = st.sidebar.date_input(
        "Período do Evento",
        value=(default_start, default_end),
        min_value=min_date,
        max_value=max_date,
        help="Padrão fixado nos últimos 30 dias (18/08/2026 a 17/09/2026). Você pode alterar livremente."
    )

    # 3. Filtro de Vendedores / Consultores
    todos_vendedores = sorted(df_ponte["nome_usuario"].dropna().unique().tolist())
    vendedores_sel = st.sidebar.multiselect(
        "Vendedores / Consultores",
        options=todos_vendedores,
        placeholder="Todos os consultores",
        help="Filtra tarefas onde o colaborador participou (como titular ou conjunto)."
    )

    # 4. Filtro de Clientes
    todos_clientes = sorted(df_base["nome_cliente"].dropna().unique().tolist())
    clientes_sel = st.sidebar.multiselect(
        "Clientes",
        options=todos_clientes,
        placeholder="Todos os clientes",
        help="Filtra tarefas associadas a clientes específicos."
    )

    # 5. Filtro de Tipo de Tarefa (Canal)
    todos_tipos = sorted(df_base["tipo_tarefa"].dropna().unique().tolist())
    tipos_sel = st.sidebar.multiselect(
        "Canal / Tipo de Atividade",
        options=todos_tipos,
        placeholder="Todos os tipos",
        help="Visita, Reunião, WhatsApp, etc."
    )

    # 6. Filtro de Status Operacional
    todos_status = sorted(df_base["status_operacional"].dropna().unique().tolist())
    status_sel = st.sidebar.multiselect(
        "Status da Tarefa",
        options=todos_status,
        placeholder="Todos os status",
        help="Finalizada, Atrasada ou Agendada."
    )

    # 7. Filtro de Marcadores
    todos_marcadores = sorted([m for m in df_base["marcadores"].dropna().unique().tolist() if m != "Sem Marcador"])
    marcadores_sel = st.sidebar.multiselect(
        "Marcadores / Tags",
        options=todos_marcadores,
        placeholder="Todas as tags"
    )

    # Botão para Limpar Filtros
    if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True):
        st.rerun()

    # Aplicação dos filtros na fato
    df_filtered = df_base.copy()

    # Filtro de data
    if isinstance(periodo_selecionado, (tuple, list)) and len(periodo_selecionado) == 2:
        dt_inicio, dt_fim = periodo_selecionado
        df_filtered = df_filtered[
            (df_filtered["data_evento"] >= dt_inicio) & (df_filtered["data_evento"] <= dt_fim)
        ]
    elif isinstance(periodo_selecionado, (tuple, list)) and len(periodo_selecionado) == 1:
        dt_inicio = periodo_selecionado[0]
        df_filtered = df_filtered[df_filtered["data_evento"] >= dt_inicio]

    # Filtro de clientes
    if clientes_sel:
        df_filtered = df_filtered[df_filtered["nome_cliente"].isin(clientes_sel)]

    # Filtro de tipos
    if tipos_sel:
        df_filtered = df_filtered[df_filtered["tipo_tarefa"].isin(tipos_sel)]

    # Filtro de status
    if status_sel:
        df_filtered = df_filtered[df_filtered["status_operacional"].isin(status_sel)]

    # Filtro de marcadores
    if marcadores_sel:
        df_filtered = df_filtered[df_filtered["marcadores"].isin(marcadores_sel)]

    # Filtro de vendedores através da tabela ponte
    if vendedores_sel:
        sk_tarefas_vendedor = df_ponte[df_ponte["nome_usuario"].isin(vendedores_sel)]["sk_tarefa"].unique()
        df_filtered = df_filtered[df_filtered["sk_tarefa"].isin(sk_tarefas_vendedor)]

    # Filtra a tabela ponte em consonância com a fato filtrada
    df_ponte_filtered = df_ponte[df_ponte["sk_tarefa"].isin(df_filtered["sk_tarefa"])].copy()
    if vendedores_sel:
        df_ponte_filtered = df_ponte_filtered[df_ponte_filtered["nome_usuario"].isin(vendedores_sel)]

    st.sidebar.divider()
    st.sidebar.caption("Comercial Saavedra — v1.0.0")

    return df_filtered, df_ponte_filtered
