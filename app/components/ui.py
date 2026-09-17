"""
Componentes de Interface de Usuário (UI) - Comercial Saavedra.
"""

import streamlit as st


def render_header(title: str, subtitle: str, icon: str = "📊"):
    """
    Renderiza o cabeçalho padronizado da página.
    """
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <h1 style="margin: 0; color: #1E3A8A; font-size: 2.2rem;">{icon} {title}</h1>
            <p style="margin-top: 5px; color: #64748B; font-size: 1.05rem;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()


def render_filter_badge(total_filtrado: int, total_base: int):
    """
    Exibe uma tag indicando a proporção de dados filtrados em relação ao total da base.
    """
    pct = round((total_filtrado / total_base) * 100, 1) if total_base > 0 else 0
    st.caption(f"🔍 Exibindo **{total_filtrado:,}** de **{total_base:,}** registros da base ({pct}% dos dados).".replace(",", "."))


def render_anomaly_alert(qtd_anomalas: int):
    """
    Alerta informativo sobre registros com anos distantes (> 2026).
    """
    if qtd_anomalas > 0:
        st.warning(
            f"ℹ️ **Aviso de Integridade:** Existem **{qtd_anomalas} registros** na base com datas em anos distantes (2027 e 2032). "
            "Por padrão, eles estão ocultos para não distorcer as análises operacionais de 2025/2026. "
            "Você pode habilitá-los na barra lateral de filtros caso queira inspecioná-los."
        )
