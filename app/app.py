"""
Aplicação Principal (Entry Point) - Comercial Saavedra Analytics.
Redireciona automaticamente para a página 1_Visao_Geral.py
"""

import sys
import os
from pathlib import Path

_current_file = Path(__file__).resolve()
_app_dir_norm = os.path.normcase(str(_current_file.parent))
_project_root = str(_current_file.parent.parent)

sys.path = [p for p in sys.path if os.path.normcase(os.path.abspath(p)) != _app_dir_norm]
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import streamlit as st
from app.config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

# Esconde a barra lateral enquanto redireciona
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.switch_page("pages/1_Visao_Geral.py")
