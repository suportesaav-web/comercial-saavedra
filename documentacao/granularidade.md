# Definição de Granularidade - Comercial Saavedra

A granularidade é o nível mais atômico e fundamental de detalhe armazenado em uma tabela. Este documento comprova analiticamente a granularidade da base bruta `Ploomes`.

---

## 1. Granularidade Identificada

> [!IMPORTANT]
> **Granularidade Oficial da Base:**
> **1 linha representa uma (1) Tarefa / Interação Comercial registrada no CRM Ploomes**, associada a uma data/hora de agendamento, um negócio e um ou mais colaboradores.

---

## 2. Evidências Empíricas nos Dados

Para determinar com precisão a granularidade sem suposições, foram realizados testes de hipótese diretamente contra os dados:

| Hipótese de Granularidade | Resultado do Teste | Evidência de Rejeição |
| :--- | :---: | :--- |
| **1 linha por Pedido / Venda** | **REJEITADA** | Não existem números de pedido, notas fiscais, itens de produto ou valores monetários. |
| **1 linha por Cliente** | **REJEITADA** | Existem 77 clientes para 1.083 linhas. O cliente `UNIMED VALE DO SINOS` possui 75 linhas distintas. |
| **1 linha por Negócio / Oportunidade** | **REJEITADA** | Existem 188 títulos de negócio para 1.083 linhas. O negócio `POWER PORT - UNIMED VALE DO SINOS` possui 47 linhas. |
| **1 linha por Vendedor** | **REJEITADA** | Existem 10 colaboradores para 1.083 linhas. O colaborador `Fernando Bomfoco` aparece em centenas de linhas. |
| **1 linha por Dia** | **REJEITADA** | Em um único dia (ex: `2026-08-18`) ocorrem múltiplas tarefas de diferentes colaboradores e clientes. |
| **1 linha por Participação de Vendedor** | **REJEITADA** | Em 220 linhas, múltiplos vendedores aparecem na mesma linha separados por ponto-e-vírgula. |
| **1 linha por Evento de Tarefa do CRM** | **CONFIRMADA** | Cada linha descreve uma atividade única (Visita, Reunião, Ligação, WhatsApp) com status (`Finalizada = True/False`), timestamp de criação e agendamento. |

---

## 3. O Desafio da Granularidade nos Múltiplos Usuários

Em 220 registros (20,3% da base), o campo `Usuários` contém mais de um colaborador. Exemplo real da linha #17:
- **Título:** `Alinhar reajuste`
- **Data:** `2026-02-18 10:00:00`
- **Nome do Cliente:** `HOSPITAL DIVINA PROVIDENCIA`
- **Usuários:** `Kyanne Reis; Rubem Júnior`

### Implicações Críticas para a Modelagem:
1. **Se a tabela fato mantiver a granularidade original (1 linha por tarefa):**
   - A contagem de tarefas da empresa estará 100% precisa (`Total Tarefas = 1.083`).
   - Porém, ao filtrar por `Rubem Júnior`, essa tarefa não será filtrada diretamente caso o relacionamento seja feito por texto simples sem tratamento.
2. **Se a tabela for despivotada / desmembrada no Power Query por usuário:**
   - A tarefa da linha #17 virará 2 linhas (uma para Kyanne e uma para Rubem).
   - Nesse caso, a granularidade da fato mudaria para: **1 linha por Participação de Usuário na Tarefa**.
   - **Impacto no DAX:** A fórmula simples `COUNTROWS(f_tarefas)` resultará em contagem inflada de tarefas globais da empresa, exigindo `DISTINCTCOUNT(f_tarefas[SK_Tarefa])` para medir tarefas reais.

---

## 4. Recomendações de Granularidade para a Arquitetura

1. **Manter a Fato Principal (`f_tarefas`) na Granularidade de Evento da Tarefa:**
   - Cada linha deve permanecer como uma tarefa única (1.083 linhas), garantindo integridade e simplicidade analítica.
2. **Criar uma Tabela Ponte (`f_tarefas_responsaveis`):**
   - Tabela auxiliar com granularidade `1 linha por Usuário por Tarefa` ligada à fato principal por `SK_Tarefa`.
   - Isso permite ao gestor filtrar "todas as tarefas em que o Colaborador X esteve presente" sem corromper as métricas globais de produtividade da empresa.
