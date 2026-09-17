"""
Página 6: Atualização & Carga de Dados - Comercial Saavedra.
Permite aos gestores fazer upload de novas planilhas exportadas do CRM Ploomes,
executando o pipeline ETL e atualizando a camada colunar Parquet em tempo real.
"""

import sys
import os
from pathlib import Path
import io

_current_file = Path(__file__).resolve()
_app_dir_norm = os.path.normcase(str(_current_file.parent.parent))
_project_root = str(_current_file.parent.parent.parent)

sys.path = [p for p in sys.path if os.path.normcase(os.path.abspath(p)) != _app_dir_norm]
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st
import pandas as pd
from datetime import datetime
from app.config.settings import PAGE_CONFIG, PATH_FATO_PARQUET, PATH_PONTE_PARQUET, PATH_DADOS_BRUTOS
from app.data.loader import load_data, clear_cache
from app.components.ui import render_header
from etl.load import run_etl

st.set_page_config(**PAGE_CONFIG)

render_header(
    title="Atualização & Carga de Dados da Base",
    subtitle="Importação e processamento colunar de novos relatórios de tarefas exportados do Ploomes CRM",
    icon="⚙️"
)

# 1. Informações da Base Atual em Produção
st.markdown("### 📊 Status da Base Atual em Memória")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

try:
    df_fato_atual, _, _ = load_data()
    total_linhas_atual = len(df_fato_atual)
    data_min_atual = df_fato_atual["data_evento"].min()
    data_max_atual = df_fato_atual["data_evento"].max()
    mtime_atual = datetime.fromtimestamp(os.path.getmtime(PATH_FATO_PARQUET)).strftime("%d/%m/%Y %H:%M:%S")
except Exception:
    total_linhas_atual = 0
    data_min_atual = "-"
    data_max_atual = "-"
    mtime_atual = "Não carregado"

with col_stat1:
    st.metric(label="Total de Tarefas em Produção", value=f"{total_linhas_atual:,}".replace(",", "."))
with col_stat2:
    st.metric(label="Data Mais Antiga", value=str(data_min_atual))
with col_stat3:
    st.metric(label="Data Mais Recente", value=str(data_max_atual))
with col_stat4:
    st.metric(label="Última Atualização", value=mtime_atual)

st.write("")
st.divider()

# 2. Instruções de Exportação no Ploomes CRM
with st.expander("ℹ️ Como exportar a base correta do Ploomes CRM", expanded=False):
    st.markdown(
        """
        Para garantir a compatibilidade 100% com os algoritmos de BI do Comercial Saavedra:
        1. Acesse o **Ploomes CRM** com seu usuário e senha.
        2. No menu lateral, acesse **Tarefas**.
        3. Remova filtros restritivos de vendedor para obter a visão de toda a equipe (ou filtre o período desejado).
        4. Clique no botão de opções e selecione **Exportar para Excel (.xlsx)**.
        5. Certifique-se de que a planilha contém as colunas padrão:
           * `Título`, `Tipo`, `Data`, `Finalizada`, `Criador`, `Usuários`, `Cliente` (ou `Nome do Cliente`), `Negócio`, `Duração`, `Contato`, `E-mail`.
        6. Faça o upload do arquivo gerado logo abaixo.
        """
    )

st.write("")
st.markdown("### 📤 Upload do Novo Arquivo do CRM")

uploaded_file = st.file_uploader(
    label="Selecione ou arraste a planilha exportada do Ploomes (.xlsx ou .xls)",
    type=["xlsx", "xls"],
    help="O sistema fará a leitura da aba de dados, executará o saneamento de texto, tratará múltiplos usuários e gerará a base Parquet."
)

if uploaded_file is not None:
    # Diagnóstico preliminar do arquivo
    file_size_kb = uploaded_file.size / 1024
    st.info(f"📁 Arquivo carregado: **{uploaded_file.name}** ({file_size_kb:.1f} KB)")

    col_btn1, col_btn2 = st.columns([2, 3])

    with col_btn1:
        start_processing = st.button("🚀 Processar e Atualizar Base Analítica", type="primary", use_container_width=True)

    if start_processing:
        progress_bar = st.progress(10, text="Iniciando extração e validação dos dados...")
        
        try:
            # 1. Executa o pipeline ETL completo
            progress_bar.progress(35, text="Aplicando regras de saneamento, chaves e desaninhamento...")
            stats = run_etl(file_source=uploaded_file, save_raw_copy=True)
            
            progress_bar.progress(80, text="Invalidando cache e atualizando arquivos Parquet...")
            clear_cache()
            
            progress_bar.progress(100, text="Processamento concluído com sucesso!")
            
            st.balloons()
            st.success("✅ **Base de dados atualizada com sucesso!** Todos os dashboards já estão sincronizados com os novos dados.")
            
            # Exibe métricas da nova carga
            st.markdown("#### 📋 Resumo da Carga Executada")
            r_col1, r_col2, r_col3 = st.columns(3)
            with r_col1:
                st.metric("Tarefas Fato Processadas", f"{stats['fato_rows']:,}".replace(",", "."))
            with r_col2:
                st.metric("Participações de Consultores", f"{stats['ponte_rows']:,}".replace(",", "."))
            with r_col3:
                st.metric("Tamanho Otimizado (Parquet)", f"{stats['fato_size_kb']} KB")
            
            st.write("")
            st.info("💡 Você pode navegar diretamente para a **Visão Geral** ou **Vendedores & Equipe** no menu lateral para analisar os novos dados.")

        except Exception as e:
            st.error(f"❌ Ocorreu um erro ao processar o arquivo: {e}")
            st.warning("Verifique se a planilha é uma exportação válida do Ploomes CRM e contém as colunas necessárias.")

st.write("")
st.divider()

# 3. Exportação e Download dos Dados Tratados para Power BI / Excel
st.markdown("### 💾 Exportação para Power BI ou Análise Local")
st.markdown(
    "Caso queira utilizar a base colunar já saneada em projetos do **Power BI Desktop** ou **Python Notebooks**, baixe os arquivos diretamente:"
)

c_down1, c_down2 = st.columns(2)

with c_down1:
    if PATH_FATO_PARQUET.exists():
        with open(PATH_FATO_PARQUET, "rb") as f:
            bytes_fato = f.read()
        st.download_button(
            label="📥 Baixar tarefas_fato.parquet (Tabela Fato)",
            data=bytes_fato,
            file_name="tarefas_fato.parquet",
            mime="application/octet-stream",
            use_container_width=True
        )

with c_down2:
    if PATH_PONTE_PARQUET.exists():
        with open(PATH_PONTE_PARQUET, "rb") as f:
            bytes_ponte = f.read()
        st.download_button(
            label="📥 Baixar tarefas_usuarios_ponte.parquet (Tabela Ponte)",
            data=bytes_ponte,
            file_name="tarefas_usuarios_ponte.parquet",
            mime="application/octet-stream",
            use_container_width=True
        )
