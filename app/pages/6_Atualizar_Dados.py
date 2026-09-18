"""
Página 6: Atualização & Carga de Dados - Comercial Saavedra.
Permite aos gestores sincronizar os dados diretamente da API v2 do Ploomes CRM com 1 clique,
ou fazer upload de novas planilhas exportadas como contingência, executando o pipeline ETL
e atualizando a camada colunar Parquet em tempo real.
"""

import sys
import os
from pathlib import Path
import io
import time

_current_file = Path(__file__).resolve()
_app_dir_norm = os.path.normcase(str(_current_file.parent.parent))
_project_root = str(_current_file.parent.parent.parent)

sys.path = [p for p in sys.path if os.path.normcase(os.path.abspath(p)) != _app_dir_norm]
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st
import pandas as pd
from datetime import datetime
from app.config.settings import (
    PAGE_CONFIG,
    PATH_FATO_PARQUET,
    PATH_PONTE_PARQUET,
    PATH_DADOS_BRUTOS,
    get_ploomes_credentials,
    PLOOMES_API_KEY,
    PLOOMES_BASE_URL
)
from app.data.loader import load_data, clear_cache
from app.components.ui import render_header
from etl.load import run_etl
from etl.api_client import PloomesClient

st.set_page_config(**PAGE_CONFIG)

render_header(
    title="Atualização & Carga de Dados da Base",
    subtitle="Sincronização automatizada via API Ploomes CRM e processamento colunar de alta performance",
    icon="⚙️"
)

# 1. Informações da Base Atual em Produção
st.markdown("### 📊 Status da Base Atual em Memória")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

try:
    df_fato_atual, _, _ = load_data()
    total_linhas_atual = len(df_fato_atual)
    d_min = df_fato_atual["data_evento"].min()
    d_max = df_fato_atual["data_evento"].max()
    data_min_atual = d_min.strftime("%d/%m/%Y") if hasattr(d_min, "strftime") else str(d_min)
    data_max_atual = d_max.strftime("%d/%m/%Y") if hasattr(d_max, "strftime") else str(d_max)
    mtime_atual = datetime.fromtimestamp(os.path.getmtime(PATH_FATO_PARQUET)).strftime("%d/%m/%Y %H:%M:%S")
except Exception:
    total_linhas_atual = 0
    data_min_atual = "-"
    data_max_atual = "-"
    mtime_atual = "Não carregado"

with col_stat1:
    st.metric(label="Total de Tarefas em Produção", value=f"{total_linhas_atual:,}".replace(",", "."))
with col_stat2:
    st.metric(label="Data Mais Antiga", value=data_min_atual)
with col_stat3:
    st.metric(label="Data Mais Recente", value=data_max_atual)
with col_stat4:
    st.metric(label="Última Atualização", value=mtime_atual)

st.write("")
st.divider()

# 2. Sincronização Direta via API Ploomes CRM
st.markdown("### 🔄 Sincronização Direta via API Ploomes CRM")
st.markdown(
    "A sincronização via API busca automaticamente todas as tarefas, negócios, clientes e participações "
    "da equipe direto do banco do **Ploomes CRM**, eliminando a necessidade de exportação manual."
)

api_key_configured = bool(PLOOMES_API_KEY)
masked_key = f"{PLOOMES_API_KEY[:6]}...{PLOOMES_API_KEY[-6:]}" if api_key_configured and len(PLOOMES_API_KEY) > 12 else "Não configurada"

card_col1, card_col2 = st.columns([3, 2])

with card_col1:
    if api_key_configured:
        st.success(f"🟢 **API Configurada & Pronta:** User-Key conectada (`{masked_key}`).")
    else:
        st.warning("⚠️ **Chave de API não localizada.** Configure sua `PLOOMES_API_KEY` no arquivo `.env` ou abaixo.")

with card_col2:
    btn_test_conn = st.button("🔍 Testar Conexão com a API", use_container_width=True)

if btn_test_conn:
    with st.spinner("Testando conectividade com https://api2.ploomes.com..."):
        client_test = PloomesClient()
        is_ok, msg = client_test.test_connection()
        if is_ok:
            try:
                remote_count = client_test.get_total_tasks_count()
                st.success(f"✅ {msg} | **{remote_count:,} tarefas** disponíveis no CRM remoto.".replace(",", "."))
            except Exception:
                st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")

# Botão principal de sincronização
st.write("")
btn_sync_api = st.button(
    "🚀 Sincronizar Base com Ploomes CRM Agora",
    type="primary",
    disabled=not api_key_configured,
    use_container_width=True,
    help="Conecta ao Ploomes CRM, baixa todos os registros, executa as transformações analíticas e atualiza a base Parquet."
)

if btn_sync_api:
    progress_bar = st.progress(0, text="Iniciando comunicação com a API...")
    status_box = st.empty()

    def update_ui_progress(current: int, total: int, msg: str):
        pct = 0.05
        if total > 0:
            pct = min(1.0, max(0.05, current / total))
        progress_bar.progress(pct, text=msg)

    t_start = time.time()
    try:
        status_box.info("⏳ Conectando aos servidores do Ploomes CRM e requisitando lotes OData...")
        stats = run_etl(source="api", progress_callback=update_ui_progress)
        
        progress_bar.progress(1.0, text="Atualizando memória analítica em cache...")
        clear_cache()
        t_total = time.time() - t_start

        status_box.empty()
        st.balloons()
        st.success(f"✅ **Sincronização concluída com sucesso em {t_total:.1f} segundos!** Todos os dashboards foram atualizados.")

        # Resumo da Carga
        st.markdown("#### 📋 Resumo da Carga via API")
        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1:
            st.metric("Tarefas Fato Processadas", f"{stats['fato_rows']:,}".replace(",", "."))
        with r_col2:
            st.metric("Participações de Consultores", f"{stats['ponte_rows']:,}".replace(",", "."))
        with r_col3:
            st.metric("Agregações Mensais", f"{stats['mensal_rows']:,}".replace(",", "."))
        with r_col4:
            st.metric("Tamanho Parquet Otimizado", f"{stats['fato_size_kb']} KB")

        st.info("💡 Você já pode navegar pelas páginas do menu lateral (**Visão Geral**, **Vendedores & Equipe**, etc.) para visualizar os dados atualizados.")

    except Exception as e:
        status_box.empty()
        st.error(f"❌ Falha durante a sincronização via API: {e}")
        st.warning("Verifique sua conexão com a internet e as credenciais do CRM Ploomes.")

# Configuração Opcional de Chave via Interface
with st.expander("🔑 Alterar / Informar outra Chave de API temporariamente", expanded=False):
    st.markdown("Caso queira testar uma chave de API diferente da configurada no `.env`:")
    custom_key_input = st.text_input("Ploomes User-Key", type="password", help="Insira a chave gerada no painel do Ploomes")
    if st.button("Salvar Chave nesta Sessão"):
        if custom_key_input.strip():
            os.environ["PLOOMES_API_KEY"] = custom_key_input.strip()
            st.success("Chave atualizada para a sessão atual! Clique em 'Testar Conexão' acima.")
            st.rerun()

st.write("")
st.divider()

# 3. Carga Manual de Planilha Excel (Contingência)
st.markdown("### 📁 Carga Manual de Planilha Excel (Contingência)")
st.caption("Utilize esta opção caso a API do CRM esteja temporariamente inacessível ou necessite auditar uma planilha exportada manualmente.")

with st.expander("ℹ️ Instruções para exportar arquivo manual do Ploomes CRM", expanded=False):
    st.markdown(
        """
        Para garantir a compatibilidade total com os algoritmos de BI:
        1. Acesse o **Ploomes CRM** > **Tarefas**.
        2. Remova filtros restritivos de vendedor para obter a visão de toda a equipe.
        3. Clique em **Opções** > **Exportar para Excel (.xlsx)**.
        4. Faça o upload do arquivo gerado logo abaixo.
        """
    )

uploaded_file = st.file_uploader(
    label="Selecione ou arraste a planilha exportada do Ploomes (.xlsx ou .xls)",
    type=["xlsx", "xls"],
    help="O sistema fará a leitura da aba de dados, executará o saneamento de texto, tratará múltiplos usuários e gerará a base Parquet."
)

if uploaded_file is not None:
    file_size_kb = uploaded_file.size / 1024
    st.info(f"📁 Arquivo carregado: **{uploaded_file.name}** ({file_size_kb:.1f} KB)")

    col_btn_upload, _ = st.columns([2, 3])
    with col_btn_upload:
        start_processing = st.button("🚀 Processar Planilha Excel", type="secondary", use_container_width=True)

    if start_processing:
        prog_excel = st.progress(10, text="Iniciando processamento da planilha...")
        try:
            stats = run_etl(file_source=uploaded_file, save_raw_copy=True)
            prog_excel.progress(80, text="Atualizando arquivos e invalidando cache...")
            clear_cache()
            prog_excel.progress(100, text="Processamento concluído!")

            st.balloons()
            st.success("✅ **Base de dados atualizada a partir do arquivo Excel com sucesso!**")
            
            res_c1, res_c2, res_c3 = st.columns(3)
            with res_c1:
                st.metric("Tarefas Fato", f"{stats['fato_rows']:,}".replace(",", "."))
            with res_c2:
                st.metric("Participações", f"{stats['ponte_rows']:,}".replace(",", "."))
            with res_c3:
                st.metric("Tamanho Parquet", f"{stats['fato_size_kb']} KB")

        except Exception as e:
            st.error(f"❌ Ocorreu um erro ao processar a planilha: {e}")

st.write("")
st.divider()

# 4. Exportação e Download dos Dados Tratados para Power BI / Excel
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
