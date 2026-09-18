"""
Configurações Globais da Aplicação Analítica - Comercial Saavedra.
"""

from pathlib import Path
import pandas as pd

# Raiz do projeto e caminhos de dados
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIR_DADOS_BRUTOS = PROJECT_ROOT / "dados" / "bruto"
DIR_DADOS_TRATADOS = PROJECT_ROOT / "dados" / "tratado"
DIR_DADOS_ANALITICOS = PROJECT_ROOT / "dados" / "analitico"

PATH_DADOS_BRUTOS = DIR_DADOS_BRUTOS / "Tarefas Power BI.xlsx"
PATH_FATO_PARQUET = DIR_DADOS_TRATADOS / "tarefas_fato.parquet"
PATH_PONTE_PARQUET = DIR_DADOS_TRATADOS / "tarefas_usuarios_ponte.parquet"
PATH_MENSAL_PARQUET = DIR_DADOS_ANALITICOS / "kpis_agregados_mensais.parquet"
PATH_USUARIOS_PARQUET = DIR_DADOS_TRATADOS / "usuarios_dim.parquet"

# Identidade Visual e Temas (Paleta Corporativa Premium)
APP_TITLE = "Comercial Saavedra — Analytics CRM"
APP_ICON = "📊"

COLORS = {
    "primary": "#1E3A8A",      # Azul Marinho Profundo
    "secondary": "#0D9488",    # Verde Petróleo / Teal
    "accent": "#F59E0B",       # Âmbar / Dourado
    "success": "#10B981",      # Esmeralda
    "danger": "#EF4444",        # Vermelho Alerta
    "warning": "#F97316",       # Laranja
    "neutral_dark": "#0F172A",  # Slate 900
    "neutral_light": "#F8FAFC", # Slate 50
    "card_bg": "#FFFFFF",
    "border": "#E2E8F0",
    "text_muted": "#64748B",
    "palette_plotly": [
        "#1E3A8A", "#0D9488", "#F59E0B", "#6366F1",
        "#EC4899", "#8B5CF6", "#14B8A6", "#F97316"
    ]
}

# Configuração de Página Streamlit Padrão
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

import os
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except Exception:
    pass

# Padrões de Formatação de Data e Governança
DATE_FORMAT_BR = "%d/%m/%Y"
DATE_TIME_FORMAT_BR = "%d/%m/%Y %H:%M"
ANOMALOUS_FUTURE_YEAR_THRESHOLD = 2026

# Integração Ploomes CRM API
def get_ploomes_credentials() -> tuple[str, str]:
    """
    Recupera as credenciais da API Ploomes na seguinte ordem de prioridade:
    1. st.secrets (para deploy no Streamlit Community Cloud)
    2. Variáveis de ambiente / arquivo .env (para ambiente local)
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "PLOOMES_API_KEY" in st.secrets:
            api_key = st.secrets["PLOOMES_API_KEY"]
            base_url = st.secrets.get("PLOOMES_BASE_URL", "https://api2.ploomes.com")
            return api_key, base_url
    except Exception:
        pass

    api_key = os.environ.get("PLOOMES_API_KEY", "")
    base_url = os.environ.get("PLOOMES_BASE_URL", "https://api2.ploomes.com")
    return api_key, base_url

PLOOMES_API_KEY, PLOOMES_BASE_URL = get_ploomes_credentials()

import unicodedata

# Usuários e integrações desconsiderados das análises da equipe comercial
# (conforme solicitação: Automação, Informática, Leonardo - Parceiro Ploomes, Rubem Júnior e integrações externas)
EXCLUDED_USERS_CANONICAL = {
    "automacao",
    "informatica",
    "ti",
    "leonardo - parceiro ploomes",
    "rubem junior",
    "google calendar",
    "mailchimp",
    "whatsapp",
    "power bi",
    "powerbi",
    "ploomes - vitor aranha",
    "nao informado"
}


def normalize_user_name(name: object) -> str:
    """Normaliza o nome do usuário removendo acentos e convertendo para minúsculas."""
    if not name or pd.isna(name):
        return ""
    clean = unicodedata.normalize("NFKD", str(name)).encode("ASCII", "ignore").decode("utf-8")
    return " ".join(clean.lower().strip().split())


def is_commercial_user(name: object) -> bool:
    """Verifica se o usuário pertence à equipe comercial (não é sistema, robô ou suporte/parceiro)."""
    norm = normalize_user_name(name)
    if not norm:
        return False
    return norm not in EXCLUDED_USERS_CANONICAL

