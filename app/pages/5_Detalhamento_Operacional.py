"""
Página 5: Detalhamento Operacional & Exportação - Comercial Saavedra.
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
from app.utils.export import convert_df_to_csv, convert_df_to_excel, prepare_export_dataframe

st.set_page_config(**PAGE_CONFIG)

df_fato, df_ponte, df_mensal = load_data()
df_filtered, df_ponte_filtered = render_sidebar_filters(df_fato, df_ponte)

render_header(
    title="Detalhamento Operacional & Exportação",
    subtitle="Consulta analítica granular, busca textual livre e extração de dados para CSV e Excel",
    icon="📋"
)

render_filter_badge(len(df_filtered), len(df_fato))
st.write("")

# Campo de Busca Textual Livre
col_search, col_stats = st.columns([3, 1])

with col_search:
    termo_busca = st.text_input(
        "🔎 Pesquisa rápida (Título, Cliente, Negócio, Vendedor ou Observação):",
        placeholder="Digite para filtrar instantaneamente..."
    )

df_display = df_filtered.copy()

if termo_busca:
    termo = termo_busca.lower()
    mask = (
        df_display["titulo"].str.lower().str.contains(termo, na=False, regex=False) |
        df_display["nome_cliente"].str.lower().str.contains(termo, na=False, regex=False) |
        df_display["titulo_negocio"].str.lower().str.contains(termo, na=False, regex=False) |
        df_display["usuarios_raw"].str.lower().str.contains(termo, na=False, regex=False) |
        df_display["descricao"].str.lower().str.contains(termo, na=False, regex=False) |
        df_display["contatos_relacionados"].str.lower().str.contains(termo, na=False, regex=False) |
        df_display["criador"].str.lower().str.contains(termo, na=False, regex=False)
    )
    df_display = df_display[mask]


with col_stats:
    st.metric("Tarefas Listadas", len(df_display))

st.write("")

# Botões de Exportação
st.markdown("### 📥 Exportar Resultados Filtrados")
col_exp1, col_exp2, col_exp3 = st.columns([2, 2, 4])

with col_exp1:
    csv_bytes = convert_df_to_csv(df_display)
    st.download_button(
        label="📄 Baixar em CSV (Excel)",
        data=csv_bytes,
        file_name="tarefas_comercial_saavedra.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp2:
    xlsx_bytes = convert_df_to_excel(df_display)
    st.download_button(
        label="📊 Baixar em Excel (.xlsx)",
        data=xlsx_bytes,
        file_name="tarefas_comercial_saavedra.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.write("")

# Renderização da Tabela Formatada
df_export_friendly = prepare_export_dataframe(df_display)

st.dataframe(
    df_export_friendly,
    use_container_width=True,
    hide_index=True,
    height=550
)
