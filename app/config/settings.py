"""
Configurações Globais da Aplicação Analítica - Comercial Saavedra.
"""

from pathlib import Path

# Raiz do projeto e caminhos de dados
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIR_DADOS_BRUTOS = PROJECT_ROOT / "dados" / "bruto"
DIR_DADOS_TRATADOS = PROJECT_ROOT / "dados" / "tratado"
DIR_DADOS_ANALITICOS = PROJECT_ROOT / "dados" / "analitico"

PATH_DADOS_BRUTOS = DIR_DADOS_BRUTOS / "Tarefas Power BI.xlsx"
PATH_FATO_PARQUET = DIR_DADOS_TRATADOS / "tarefas_fato.parquet"
PATH_PONTE_PARQUET = DIR_DADOS_TRATADOS / "tarefas_usuarios_ponte.parquet"
PATH_MENSAL_PARQUET = DIR_DADOS_ANALITICOS / "kpis_agregados_mensais.parquet"

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
