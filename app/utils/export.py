"""
Módulo de Exportação de Dados - Comercial Saavedra.
Gera downloads em formatos CSV (com BOM para Excel) e Excel XLSX nativo em memória.
"""

import io
import pandas as pd

COLUMNS_FRIENDLY_NAMES = {
    "sk_tarefa": "ID Tarefa",
    "titulo": "Título da Tarefa",
    "tipo_tarefa": "Canal / Tipo",
    "status_operacional": "Status",
    "finalizada": "Finalizada (Sim/Não)",
    "duracao_minutos": "Duração (Minutos)",
    "duracao_horas": "Duração (Horas)",
    "data_evento_str": "Data do Evento",
    "hora_evento": "Hora",
    "nome_cliente": "Cliente",
    "titulo_negocio": "Negócio / Oportunidade",
    "usuario_principal": "Responsável Principal",
    "usuarios_raw": "Todos os Usuários",
    "qtd_usuarios_tarefa": "Qtd Participantes",
    "contatos_relacionados": "Contatos Relacionados",
    "email_criador": "E-mail do Criador",
    "is_sincronizado_google": "Sincronizado Google",
    "criador": "Criador",
    "marcadores": "Marcadores / Tags",
    "lead_time_dias": "Lead Time (Dias)",
    "descricao": "Observações"
}


def prepare_export_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara e renomeia o DataFrame com rótulos de negócio amigáveis."""
    cols_to_keep = [c for c in COLUMNS_FRIENDLY_NAMES.keys() if c in df.columns]
    df_export = df[cols_to_keep].copy()
    df_export = df_export.rename(columns=COLUMNS_FRIENDLY_NAMES)
    return df_export


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Converte DataFrame em bytes CSV (UTF-8 com BOM para abrir perfeitamente no Excel pt-BR)."""
    df_export = prepare_export_dataframe(df)
    return df_export.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")


def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """Converte DataFrame em bytes XLSX do Excel."""
    df_export = prepare_export_dataframe(df)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Tarefas_Filtradas")
    return output.getvalue()
