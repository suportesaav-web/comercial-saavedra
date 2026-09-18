"""
Módulo de Transformação de Dados - Comercial Saavedra.
Aplica regras de negócio, padronização, geração de Surrogate Keys,
desaninhamento de usuários para tabela-ponte, sanitização de dados e
incorporação das novas métricas de Duração, Contatos e Sincronização de E-mail.
"""

from typing import Tuple
import pandas as pd
import numpy as np

try:
    from app.config.settings import ANOMALOUS_FUTURE_YEAR_THRESHOLD, DATE_FORMAT_BR
except Exception:
    ANOMALOUS_FUTURE_YEAR_THRESHOLD = 2026
    DATE_FORMAT_BR = "%d/%m/%Y"


def clean_text(val: object) -> str:
    """Limpa espaços nas bordas e converte valores vazios."""
    if pd.isna(val):
        return ""
    return str(val).strip()


def transform_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Executa todas as transformações de engenharia de dados.

    Args:
        df_raw: DataFrame extraído do arquivo bruto.

    Returns:
        Tuple contendo:
        1. df_fato: Tabela fato de tarefas tratada (1 linha = 1 tarefa).
        2. df_ponte: Tabela ponte tarefas-usuários (1 linha = 1 participação de usuário).
        3. df_mensal: Tabela agregada analítica mensal pré-computada.
    """
    df = df_raw.copy()

    # 1. Criação da Surrogate Key única
    df["sk_tarefa"] = np.arange(1, len(df) + 1, dtype=np.int64)

    # 2. Tratamento e padronização de campos de texto com suporte a aliases
    col_cli = next((c for c in ["Nome do Cliente", "Cliente"] if c in df.columns), None)
    df["nome_cliente"] = df[col_cli].apply(clean_text) if col_cli else "Cliente Não Informado"
    df["nome_cliente"] = df["nome_cliente"].replace("", "Cliente Não Informado")

    col_tipo = next((c for c in ["Tipo"] if c in df.columns), None)
    df["tipo_tarefa"] = df[col_tipo].apply(clean_text).replace("", "Não Informado") if col_tipo else "Não Informado"

    col_tit = next((c for c in ["Título", "Titulo"] if c in df.columns), None)
    df["titulo"] = df[col_tit].apply(clean_text) if col_tit else ""
    mask_titulo_vazio = df["titulo"] == ""
    df.loc[mask_titulo_vazio, "titulo"] = (
        df.loc[mask_titulo_vazio, "tipo_tarefa"] + " - " + df.loc[mask_titulo_vazio, "nome_cliente"]
    )

    col_desc = next((c for c in ["Descrição", "Descricao"] if c in df.columns), None)
    df["descricao"] = df[col_desc].fillna("").astype(str).str.strip() if col_desc else ""

    col_neg = next((c for c in ["Título do Negócio", "Negócio", "Titulo do Negocio"] if c in df.columns), None)
    df["titulo_negocio"] = df[col_neg].apply(clean_text).replace("", "Negócio Não Informado") if col_neg else "Negócio Não Informado"

    col_marc = next((c for c in ["Marcadores"] if c in df.columns), None)
    df["marcadores"] = df[col_marc].apply(clean_text).replace("", "Sem Marcador") if col_marc else "Sem Marcador"

    col_cria = next((c for c in ["Criador"] if c in df.columns), None)
    df["criador"] = df[col_cria].apply(clean_text).replace("", "Não Informado") if col_cria else "Não Informado"

    col_usr = next((c for c in ["Usuários", "Usuarios"] if c in df.columns), None)
    df["usuarios_raw"] = df[col_usr].apply(clean_text) if col_usr else "Não Informado"

    # 3. Tratamento de datas e isolamento de componentes no formato brasileiro DD/MM/AAAA
    col_data = next((c for c in ["Data", "Data do Evento"] if c in df.columns), None)
    df["data_hora_evento"] = pd.to_datetime(df[col_data], errors="coerce") if col_data else pd.NaT
    df["data_evento"] = df["data_hora_evento"].dt.date
    # Formato padrão DD/MM/AAAA para exibição gerencial
    df["data_evento_str"] = df["data_hora_evento"].dt.strftime(DATE_FORMAT_BR).fillna("")
    df["data_evento_iso"] = df["data_hora_evento"].dt.strftime("%Y-%m-%d").fillna("")

    # Se a coluna 'Horário' nativa existir, usa-a com fallback seguro contra nulos
    col_hora = next((c for c in ["Horário", "Horario"] if c in df.columns), None)
    if col_hora:
        df["hora_evento"] = df[col_hora].fillna("").astype(str).str[:5]
        mask_invalido = df["hora_evento"].isin(["", "nan", "None"])
        df.loc[mask_invalido, "hora_evento"] = df.loc[mask_invalido, "data_hora_evento"].dt.strftime("%H:%M").fillna("00:00")
    else:
        df["hora_evento"] = df["data_hora_evento"].dt.strftime("%H:%M").fillna("00:00")

    df["hora_do_dia"] = df["data_hora_evento"].dt.hour
    df["ano_evento"] = df["data_hora_evento"].dt.year
    df["mes_evento"] = df["data_hora_evento"].dt.month
    df["mes_ano_evento"] = df["data_hora_evento"].dt.strftime("%Y-%m")
    df["dia_semana_nome"] = df["data_hora_evento"].dt.day_name()

    col_dt_cria = next((c for c in ["Data de criação", "Data de criacao", "Data de Criação", "Data Criação"] if c in df.columns), None)
    df["data_hora_criacao"] = pd.to_datetime(df[col_dt_cria], errors="coerce") if col_dt_cria else pd.NaT
    df["data_criacao"] = df["data_hora_criacao"].dt.date

    # Lead Time em dias (diferença entre a data de realização e a data de criação no CRM)
    df["lead_time_dias"] = (df["data_hora_evento"] - df["data_hora_criacao"]).dt.total_seconds() / 86400.0
    df["lead_time_dias"] = df["lead_time_dias"].round(1)

    # Sinalização de anomalias de data (datas futuras fora do ciclo operacional)
    df["is_data_futura_anomala"] = df["ano_evento"] > ANOMALOUS_FUTURE_YEAR_THRESHOLD

    # 4. Status da Tarefa
    df["finalizada"] = df["Finalizada"].astype(bool)
    
    # Classificação de status operacional
    agora = pd.Timestamp.now()
    conditions = [
        df["finalizada"] == True,
        (df["finalizada"] == False) & (df["data_hora_evento"] < agora),
        (df["finalizada"] == False) & (df["data_hora_evento"] >= agora)
    ]
    choices = ["Finalizada", "Atrasada", "Agendada"]
    df["status_operacional"] = np.select(conditions, choices, default="Indefinido")

    # 5. Tratamento das Novas Colunas (Duração, Contatos, E-mail/Google Calendar)
    # Duração (em minutos e horas)
    col_dur = "Duração" if "Duração" in df.columns else ("Duração ( minutos )" if "Duração ( minutos )" in df.columns else None)
    if col_dur:
        df["duracao_minutos"] = pd.to_numeric(df[col_dur], errors="coerce").fillna(0.0)
    else:
        df["duracao_minutos"] = 0.0
    df["duracao_horas"] = (df["duracao_minutos"] / 60.0).round(2)

    # Contatos relacionados
    col_contato = "Contatos relacionados" if "Contatos relacionados" in df.columns else ("Contato" if "Contato" in df.columns else None)
    if col_contato:
        df["contatos_relacionados"] = df[col_contato].apply(clean_text).replace("", "Sem Contato Informado")
        df["has_contato_preenchido"] = df["contatos_relacionados"] != "Sem Contato Informado"
    else:
        df["contatos_relacionados"] = "Sem Contato Informado"
        df["has_contato_preenchido"] = False

    # E-mail do criador / Google Calendar
    col_email = "E-mail do criador (Google Calendar)" if "E-mail do criador (Google Calendar)" in df.columns else ("E-mail" if "E-mail" in df.columns else None)
    if col_email:
        df["email_criador"] = df[col_email].apply(clean_text).replace("", "Não Sincronizado")
        df["is_sincronizado_google"] = df["email_criador"] != "Não Sincronizado"
    else:
        df["email_criador"] = "Não Sincronizado"
        df["is_sincronizado_google"] = False

    # 6. Tratamento de múltiplos usuários e identificação do responsável principal
    def extract_user_info(user_str: str):
        parts = [p.strip() for p in user_str.split(";") if p.strip()]
        if not parts:
            return "Não Informado", 1
        return parts[0], len(parts)

    user_info = df["usuarios_raw"].apply(extract_user_info)
    df["usuario_principal"] = [info[0] for info in user_info]
    df["qtd_usuarios_tarefa"] = [info[1] for info in user_info]
    df["is_tarefa_conjunta"] = df["qtd_usuarios_tarefa"] > 1

    df["is_criador_igual_usuario"] = df["criador"] == df["usuario_principal"]

    # Seleção e organização das colunas da fato tratada
    cols_fato = [
        "sk_tarefa",
        "titulo",
        "tipo_tarefa",
        "status_operacional",
        "finalizada",
        "duracao_minutos",
        "duracao_horas",
        "contatos_relacionados",
        "has_contato_preenchido",
        "email_criador",
        "is_sincronizado_google",
        "data_hora_evento",
        "data_evento",
        "data_evento_str",
        "hora_evento",
        "hora_do_dia",
        "ano_evento",
        "mes_evento",
        "mes_ano_evento",
        "dia_semana_nome",
        "is_data_futura_anomala",
        "nome_cliente",
        "titulo_negocio",
        "usuario_principal",
        "usuarios_raw",
        "qtd_usuarios_tarefa",
        "is_tarefa_conjunta",
        "criador",
        "is_criador_igual_usuario",
        "marcadores",
        "data_hora_criacao",
        "data_criacao",
        "lead_time_dias",
        "descricao"
    ]
    df_fato = df[cols_fato].copy()

    # 7. Construção da Tabela-Ponte de Usuários (tarefas_usuarios_ponte)
    ponte_rows = []
    for _, row in df.iterrows():
        sk = row["sk_tarefa"]
        raw_u = row["usuarios_raw"]
        parts = [p.strip() for p in raw_u.split(";") if p.strip()]
        if not parts:
            parts = ["Não Informado"]
        for idx, u in enumerate(parts, start=1):
            ponte_rows.append({
                "sk_tarefa": sk,
                "nome_usuario": u,
                "is_usuario_principal": idx == 1,
                "ordem_usuario": idx,
                "tipo_tarefa": row["tipo_tarefa"],
                "finalizada": row["finalizada"],
                "status_operacional": row["status_operacional"],
                "duracao_minutos": row["duracao_minutos"],
                "duracao_horas": row["duracao_horas"],
                "has_contato_preenchido": row["has_contato_preenchido"],
                "is_sincronizado_google": row["is_sincronizado_google"],
                "data_evento": row["data_evento"],
                "data_evento_str": row["data_evento_str"],
                "ano_evento": row["ano_evento"],
                "mes_ano_evento": row["mes_ano_evento"],
                "nome_cliente": row["nome_cliente"]
            })

    df_ponte = pd.DataFrame(ponte_rows)
    df_ponte["sk_tarefa"] = df_ponte["sk_tarefa"].astype(np.int64)

    # 8. Construção da Camada Analítica Agregada Mensal
    df_mensal = (
        df_fato[~df_fato["is_data_futura_anomala"]]
        .groupby(["mes_ano_evento", "tipo_tarefa"], as_index=False)
        .agg(
            total_tarefas=("sk_tarefa", "count"),
            tarefas_finalizadas=("finalizada", lambda x: int(x.sum())),
            visitas_presenciais=("tipo_tarefa", lambda x: int((x == "Visita").sum())),
            horas_totais=("duracao_horas", "sum"),
            clientes_distintos=("nome_cliente", "nunique"),
            lead_time_medio=("lead_time_dias", "mean")
        )
    )
    df_mensal["taxa_conclusao_pct"] = (
        (df_mensal["tarefas_finalizadas"] / df_mensal["total_tarefas"]) * 100
    ).round(1)
    df_mensal["lead_time_medio"] = df_mensal["lead_time_medio"].fillna(0.0).round(1)
    df_mensal["horas_totais"] = df_mensal["horas_totais"].round(1)

    return df_fato, df_ponte, df_mensal


if __name__ == "__main__":
    from etl.extract import extract_raw_tasks
    df_raw = extract_raw_tasks()
    df_fato, df_ponte, df_mensal = transform_data(df_raw)
    print("Transformação concluída com sucesso:")
    print(f"  Fato: {df_fato.shape}")
    print(f"  Ponte: {df_ponte.shape}")
    print(f"  Mensal: {df_mensal.shape}")
