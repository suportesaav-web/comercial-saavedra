"""
Página 7: Guia do Usuário & Central de Ajuda - Comercial Saavedra.
Manual operacional interativo, glossário de métricas e regras de negócio da plataforma.
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
from app.config.settings import PAGE_CONFIG
from app.components.ui import render_header

st.set_page_config(**PAGE_CONFIG)

render_header(
    title="Central de Ajuda & Guia do Usuário",
    subtitle="Manual operacional, glossário de indicadores e diretrizes de governança do Comercial Saavedra",
    icon="📖"
)

tab1, tab2, tab3, tab4 = st.tabs([
    "🧭 Navegação & Módulos",
    "📐 Dicionário de KPIs & Fórmulas",
    "🎯 Melhores Práticas no CRM",
    "❓ Perguntas Frequentes (FAQ)"
])

with tab1:
    st.markdown("### 🗺️ Como Navegar na Plataforma")
    st.markdown(
        """
        A plataforma foi construída com foco em **agilidade analítica** e suporte à tomada de decisão da diretoria e gerência comercial.
        Abaixo está o resumo de cada página disponível no menu lateral:
        """
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            #### 1. 📈 Visão Geral
            * **Objetivo:** Painel macro de produtividade corporativa.
            * **O que você vê:** Volume total de tarefas, taxa de conclusão consolidada, horas dedicadas a clientes, volume de atrasos e mix de canais (Visita, Telefone, WhatsApp, etc.).
            * **Diagnósticos Inteligentes:** Alertas automáticos que destacam desvios e oportunidades em tempo real.

            #### 2. 👥 Vendedores & Equipe
            * **Objetivo:** Gestão da força de vendas e produtividade individual.
            * **O que você vê:** Ranking de tarefas totais e finalizadas, carga horária em campo, média de tarefas diárias, tempo ocioso na semana (dias úteis sem visita), conformidade de contatos e sincronização com Google Calendar.
            * **Seleção Individual:** Filtre qualquer consultor para ver seu raio-X detalhado.

            #### 3. 🏥 Clientes & Negócios
            * **Objetivo:** Cobertura de contas hospitalares e oportunidades comerciais.
            * **O que você vê:** Top 15 clientes com maior volume de atendimento, distribuição de esforço por oportunidade de negócio e intensidade de visitas presenciais.
            """
        )

    with c2:
        st.markdown(
            """
            #### 4. ⏳ Análise Temporal
            * **Objetivo:** Identificar sazonalidades, horários de pico e planejamento de rotas.
            * **O que você vê:** Heatmap de dia da semana vs turno (Manhã, Tarde, Noite), distribuição por hora do dia e lead time de agendamento.

            #### 5. 📋 Detalhamento Operacional
            * **Objetivo:** Auditoria granular linha a linha de cada tarefa.
            * **O que você vê:** Tabela interativa com busca textual por cliente, filtros combinados de status e botão de **exportação direta para Excel (.xlsx) e CSV**.

            #### 6. ⚙️ Atualizar Dados
            * **Objetivo:** Atualização contínua do dashboard pela própria equipe.
            * **O que você vê:** Upload da nova planilha do Ploomes CRM com execução imediata do pipeline de ETL e recarga automática do painel.
            """
        )

    st.write("")
    st.info("💡 **Dica de Navegação:** Os filtros aplicados na barra lateral (período, vendedor, canal, status) afetam simultaneamente todas as páginas analíticas.")

with tab2:
    st.markdown("### 📐 Fórmulas e Regras dos Indicadores Gerenciais")
    st.markdown("Todas as métricas seguem rigorosamente as regras de governança estabelecidas pela gestão:")

    kpi_data = [
        {
            "kpi": "Total de Tarefas Realizadas por Vendedor",
            "regra": "Soma de todas as tarefas em que o vendedor participou, seja como titular (responsável primário) ou como participante de visita conjunta (tabela-ponte).",
            "formula": "COUNT(tarefas_usuarios_ponte.sk_tarefa)"
        },
        {
            "kpi": "Total de Tarefas Finalizadas",
            "regra": "Tarefas que foram marcadas com status de conclusão no CRM Ploomes.",
            "formula": "COUNTIF(finalizada == True)"
        },
        {
            "kpi": "Taxa de Conclusão (%)",
            "regra": "Percentual de tarefas concluídas em relação ao total de tarefas planejadas no período.",
            "formula": "(Tarefas Finalizadas / Total de Tarefas) * 100"
        },
        {
            "kpi": "Tarefas em Atraso ⚠️",
            "regra": "Tarefas cuja data e horário agendados já expiraram no passado, mas que ainda constam como 'Não Finalizadas' no CRM.",
            "formula": "COUNTIF(finalizada == False AND data_evento < HOJE())"
        },
        {
            "kpi": "Média de Tarefas Diárias",
            "regra": "Média de atividades realizadas considerando estritamente os dias em que o vendedor teve registro de campo (evitando distorções por finais de semana ou férias).",
            "formula": "Total de Tarefas / Dias Distintos com Atividade"
        },
        {
            "kpi": "Tempo sem Tarefas na Semana",
            "regra": "Média de dias úteis (Segunda a Sexta) em uma semana comercial típica em que o vendedor não registrou nenhuma atividade no CRM.",
            "formula": "5 - (Dias Úteis com Atividade / Total de Semanas Úteis)"
        },
        {
            "kpi": "Duração & Horas de Atendimento",
            "regra": "Tempo dedicado em visitas e atendimentos clínicos, convertido de minutos para horas.",
            "formula": "SUM(duracao_minutos) / 60"
        },
        {
            "kpi": "Conformidade de Contatos (%)",
            "regra": "Percentual de tarefas em que o consultor cadastrou o nome do interlocutor clínico (médico, enfermeiro-chefe, comprador ou farmacêutico).",
            "formula": "(Tarefas com Contato Preenchido / Total de Tarefas) * 100"
        },
        {
            "kpi": "Sincronização Google Calendar (%)",
            "regra": "Percentual de tarefas integradas à agenda corporativa do Google Workspace via e-mail do criador.",
            "formula": "(Tarefas com E-mail Válido / Total de Tarefas) * 100"
        }
    ]

    for item in kpi_data:
        with st.expander(f"📌 {item['kpi']}", expanded=False):
            st.markdown(f"**Regra de Negócio:** {item['regra']}")
            st.code(item['formula'], language="sql")

with tab3:
    st.markdown("### 🎯 Boas Práticas de Operação no Ploomes CRM")
    st.markdown(
        """
        Para que a diretoria da Comercial Saavedra tenha visibilidade de ponta a ponta da operação de campo, os consultores devem seguir estas orientações:
        """
    )

    b1, b2 = st.columns(2)

    with b1:
        st.success(
            """
            **✅ 1. Preenchimento Obrigatório do Interlocutor (Contato)**
            * Ao agendar ou concluir uma visita hospitalar, sempre informe quem foi atendido (Ex: *Dr. Roberto - Cirurgia Geral*, *Mariana - Farmácia Central*).
            * **Benefício:** Permite à diretoria mapear quem são os reais decisores em cada hospital e protege a memória institucional da empresa.
            """
        )
        st.success(
            """
            **✅ 2. Registro Preciso da Duração da Visita**
            * Insira os minutos reais gastos no atendimento hospitalar.
            * **Benefício:** Auxilia na análise de dimensionamento da força de vendas e rentabilidade por cliente.
            """
        )

    with b2:
        st.warning(
            """
            **⚠️ 3. Baixa Imediata após a Realização**
            * Dê baixa na tarefa no mesmo dia em que o atendimento ocorreu.
            * **Atenção:** Tarefas não finalizadas após o horário agendado entram automaticamente no indicador de **Tarefas em Atraso**, gerando alertas para a gerência.
            """
        )
        st.info(
            """
            **📅 4. Integração com Google Calendar**
            * Mantenha seu e-mail institucional autenticado no Ploomes para que suas visitas sejam refletidas na sua agenda do celular e contem no índice de sincronização corporativa.
            """
        )

with tab4:
    st.markdown("### ❓ Perguntas Frequentes (FAQ)")

    with st.expander("Por que a data padrão do filtro vem travada nos últimos 30 dias?"):
        st.markdown(
            "A gestão definiu os últimos 30 dias (`18/08/2026` a `17/09/2026`) como período padrão para garantir foco imediato na operação corrente e nas pendências ativas. Você pode alterar as datas livremente na barra lateral a qualquer momento."
        )

    with st.expander("Qual a diferença entre Vendedor Titular e Vendedor Participante?"):
        st.markdown(
            "Quando duas pessoas realizam uma visita conjunta (ex: `Consultor A; Consultor B`), o primeiro nome é considerado o **Titular** e o segundo o **Participante**. No módulo *Vendedores & Equipe*, ambos recebem os devidos créditos pela participação através da tabela-ponte de relacionamento N:N."
        )

    with st.expander("Como exportar os dados para gerar relatórios no Excel?"):
        st.markdown(
            "Basta acessar a página **5. Detalhamento Operacional**, aplicar os filtros desejados e clicar no botão **Exportar para Excel (.xlsx)** ou **Exportar para CSV**. O arquivo virá com formatação brasileira (BOM UTF-8)."
        )

    with st.expander("Com que frequência devo atualizar a base na tela 'Atualizar Dados'?"):
        st.markdown(
            "Recomenda-se atualizar semanalmente (ou ao final de cada dia de fechamento). O processo leva menos de 5 segundos e atualiza instantaneamente todos os gráficos e KPIs da plataforma."
        )
