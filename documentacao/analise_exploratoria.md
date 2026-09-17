# Análise Exploratória Profunda - Comercial Saavedra

Este documento apresenta o perfil estatístico, estrutural e analítico de todas as colunas da base bruta `Tarefas Power BI.xlsx` (aba `Ploomes`), além de mapear colunas derivadas e padrões de negócio.

---

## 1. Perfil Detalhado das Colunas

### 1.1. `Título`
- **Tipo Inferido (Pandas):** `object`
- **Tipo Real Armazenado:** `string` (1.069 linhas) e `NoneType` (14 linhas)
- **Quantidade de Valores Preenchidos:** 1.069
- **Quantidade de Nulos:** 14 (1,29%)
- **Quantidade de Valores Distintos:** 872
- **Cardinalidade / Razão de Distintos:** 81,57% (872 / 1.069)
- **Comprimento do Texto:** Mínimo: 2 caracteres | Máximo: 123 caracteres
- **Espaços Extras:** Detectados em 28 registros (espaços no início ou no fim do texto).
- **Inconsistência de Caixa Alta/Baixa:** 858 versões distintas em minúsculo contra 872 originais (diferenças sutis de caixa).
- **Exemplos de Valores:**
  - `Entregar Picc e Guia vencimento 31/01`
  - `Contagem consignados`
  - `Acompanhar cirurgia Dr. X`
  - `Reunião Semanal Saavedra`
- **Diagnóstico & Problemas:** 14 tarefas não possuem título no CRM. O título é livremente digitado pelos vendedores, resultando em descrições variantes para uma mesma finalidade (ex: "Contagem consignados", "Contagem de consignado", "CONTAGEM DE CONSIGNADO").
- **Impacto no Power BI:** Dificuldade para criar agregações diretas por esse campo. Recomenda-se tratar nulos como `"Sem Título"` e aplicar `Text.Trim`.

---

### 1.2. `Descrição`
- **Tipo Inferido (Pandas):** `object`
- **Tipo Real Armazenado:** `string` (410 linhas) e `NoneType` (673 linhas)
- **Quantidade de Valores Preenchidos:** 410
- **Quantidade de Nulos:** 673 (62,14%)
- **Quantidade de Valores Distintos:** 384
- **Cardinalidade / Razão de Distintos:** 93,66% (384 / 410)
- **Comprimento do Texto:** Mínimo: 1 caractere | Máximo: 1.000+ caracteres
- **Quebras de Linha e Formatação:** Contém quebras de linha (`\n`), listas e anotações livres de reuniões/visitas.
- **Exemplos de Valores:**
  - `ATS`
  - `Visita para alinhamento de consignado`
  - `são em Três Horários pois será para as equipes UTI, EMERGÊNCIA...`
- **Diagnóstico & Problemas:** Alta vacância (62,14% nulo). Não é uma coluna analítica para filtros ou eixos de gráficos.
- **Impacto no Power BI:** Textos longos ocupam grande volume de memória no dicionário do VertiPaq. Deve ser avaliado se este campo deve ser descartado no Power BI ou mantido apenas para *drill-through* e detalhamento pontual.

---

### 1.3. `Finalizada`
- **Tipo Inferido (Pandas):** `bool`
- **Tipo Real Armazenado:** `bool` (1.083 linhas)
- **Quantidade de Valores Preenchidos:** 1.083
- **Quantidade de Nulos:** 0 (0,00%)
- **Distribuição de Valores:**
  - `True`: 971 (89,66%)
  - `False`: 112 (10,34%)
- **Quantidade de Valores Distintos:** 2
- **Cardinalidade:** 0,18%
- **Diagnóstico & Problemas:** Campo de status booleano perfeitamente preenchido.
- **Impacto no Power BI:** Excelente compressão no VertiPaq (bit único). Ideal para segmentação de tarefas (Concluídas vs. Pendentes/Atrasadas) e criação de medidas de taxa de conclusão.

---

### 1.4. `Data`
- **Tipo Inferido (Pandas):** `datetime64[ns]`
- **Tipo Real Armazenado:** `datetime` (1.083 linhas)
- **Quantidade de Valores Preenchidos:** 1.083
- **Quantidade de Nulos:** 0 (0,00%)
- **Quantidade de Valores Distintos:** 927
- **Cardinalidade:** 85,60%
- **Data Mínima:** `2025-01-29 11:00:00`
- **Data Máxima:** `2032-04-28 14:30:00`
- **Presença de Horário:** Sim (horas e minutos em quase todas as linhas).
- **Distribuição por Ano:**
  - 2025: 123 (11,36%)
  - 2026: 958 (88,46%)
  - 2027: 1 (0,09%) - `2027-07-01 08:00:00`
  - 2032: 1 (0,09%) - `2032-04-28 14:30:00`
- **Diagnóstico & Problemas:**
  1. Existem 2 registros com datas futuras anômalas (2027 e 2032), provavelmente erros de digitação humana no CRM.
  2. Data e hora estão na mesma coluna. No VertiPaq, colunas `DateTime` possuem alta cardinalidade e aumentam o tamanho do arquivo pbix.
- **Impacto no Power BI:** Se uma tabela `d_calendario` for gerada automaticamente pelo `MAX(Data)`, ela irá até 2032 desnecessariamente. É mandatório dividir em `Data` (tipo `Date`) e `Hora` (tipo `Time`) no Power Query e criar uma regra para tratar datas anômalas.

---

### 1.5. `Nome do Cliente`
- **Tipo Inferido (Pandas):** `object`
- **Tipo Real Armazenado:** `string` (1.082 linhas) e `NoneType` (1 linha)
- **Quantidade de Valores Preenchidos:** 1.082
- **Quantidade de Nulos:** 1 (0,09% - Registro #2 associado ao negócio "Contagem Consignad")
- **Quantidade de Valores Distintos:** 77
- **Cardinalidade:** 7,12%
- **Espaços Extras:** 4 clientes possuem espaços em branco no início ou fim (ex: `"Joseane  Arruda Secretária Dr. Gusmão quadril "`).
- **Exemplos de Valores:**
  - `UNIMED VALE DO SINOS` (75 tarefas)
  - `HOSPITAL DIVINA PROVIDENCIA` (66 tarefas)
  - `HOSPITAL REGINA` (59 tarefas)
  - `HOSPITAL SAO LUCAS DA PUCRS` (43 tarefas)
- **Diagnóstico & Problemas:** Não há código/CNPJ de cliente. A identificação é puramente nominal, com risco de divergências em clientes com nomes de médicos ou departamentos.
- **Impacto no Power BI:** No Power Query, deve-se aplicar `Text.Trim` e substituir o valor nulo por `"Cliente Não Identificado"` para viabilizar relacionamento 1:N com a dimensão `d_cliente`.

---

### 1.6. `Título do Negócio`
- **Tipo Inferido (Pandas):** `object`
- **Tipo Real Armazenado:** `string` (1.083 linhas)
- **Quantidade de Valores Preenchidos:** 1.083
- **Quantidade de Nulos:** 0 (0,00%)
- **Quantidade de Valores Distintos:** 188
- **Cardinalidade:** 17,36%
- **Exemplos de Valores:**
  - `POWER PORT - UNIMED VALE DO SINOS` (47 tarefas)
  - `CPM` (33 tarefas)
  - `REAJUSTE DE PREÇO 2026 - MAT. MED.` (27 tarefas)
  - `Contagem Consignad` (26 tarefas)
- **Diagnóstico & Problemas:**
  - 7 títulos de negócios estão vinculados a múltiplos clientes distintos (ex: `REAJUSTE DE PREÇO 2026 - MAT. MED.` ocorre em 16 clientes diferentes).
  - O campo mistura oportunidades comerciais específicas com atividades operacionais genéricas.
- **Impacto no Power BI:** Não se pode assumir que `Título do Negócio` é hierarquicamente subordinado a `Nome do Cliente`. Se transformado em dimensão sem chave própria, pode gerar ambiguidade ou relação muitos-para-muitos.

---

### 1.7. `Usuários`
- **Tipo Inferido (Pandas):** `object`
- **Tipo Real Armazenado:** `string` (1.083 linhas)
- **Quantidade de Valores Preenchidos:** 1.083
- **Quantidade de Nulos:** 0 (0,00%)
- **Quantidade de Valores Distintos Combinados:** 74 padrões de agrupamento
- **Presença de Delimitador:** **220 linhas contêm o caractere `;`** (ponto-e-vírgula), indicando múltiplos usuários atribuídos à mesma tarefa.
- **Usuários Individuais Identificados (10):**
  1. `Cristiana Gehm`
  2. `Fernando Bomfoco`
  3. `Informatica`
  4. `João Eraldo de Aguiar Rolim`
  5. `Kyanne Reis`
  6. `Mariana Ferreira Arrieche`
  7. `Miriã Kruno`
  8. `Priscila Scherer`
  9. `Rubem Júnior`
  10. `Saulo Scherer`
- **Diagnóstico & Problemas:** Este é um dos maiores desafios de modelagem da base. Se uma tarefa foi atribuída a 6 pessoas (`Kyanne Reis; Fernando Bomfoco; Priscila Scherer; Miriã Kruno; Saulo Scherer; Cristiana Gehm`), como atribuir métricas a um vendedor no Power BI sem duplicar linhas de fatos?
- **Impacto no Power BI:** Relação N:N. Necessitará de tratamento específico no Power Query: ou separação do "Responsável Principal" ou tabela-ponte (*Bridge Table*) desnormalizada.

---

### 1.8. `Marcadores`
- **Tipo Inferido (Pandas):** `object`
- **Tipo Real Armazenado:** `string` (453 linhas) e `NoneType` (630 linhas)
- **Quantidade de Valores Preenchidos:** 453
- **Quantidade de Nulos:** 630 (58,17%)
- **Quantidade de Valores Distintos:** 17
- **Valores Mais Frequentes:**
  - `Visita Recorrente` (177)
  - `ADM.` (72)
  - `Contagem OPME` (66)
  - `REUNIÃO SEMANAL` (34)
  - `1ª Visita` (28)
  - `EVENTO` (20)
  - `Retorno` (18)
- **Presença de Delimitador:** 3 linhas contêm `;` (ex: `PISTOLA; Contagem OPME; Visita Recorrente`).
- **Diagnóstico & Problemas:** Alto percentual de ausência de classificação (58,17%).
- **Impacto no Power BI:** Substituir nulos por `"Sem Marcador"` e padronizar valores múltiplos.

---

### 1.9. `Data de criação`
- **Tipo Inferido (Pandas):** `datetime64[ns]`
- **Tipo Real Armazenado:** `datetime` (1.083 linhas)
- **Quantidade de Valores Preenchidos:** 1.083
- **Quantidade de Nulos:** 0 (0,00%)
- **Quantidade de Valores Distintos:** 987
- **Data Mínima:** `2025-01-29 11:09:35.617000`
- **Data Máxima:** `2026-09-17 07:44:14.527000`
- **Presença de Milissegundos:** Sim.
- **Geração em Lote:** 25 timestamps ocorrem em duplicidade exata (até milissegundos), somando 121 tarefas criadas por rotinas automáticas de recorrência.
- **Diagnóstico & Problemas:** Milissegundos aumentam drasticamente a cardinalidade da coluna sem valor para relatórios comerciais.
- **Impacto no Power BI:** Converter para tipo `Date` (se usada para relacionar com calendário) ou truncar os milissegundos.

---

### 1.10. `Tipo`
- **Tipo Inferido (Pandas):** `object`
- **Tipo Real Armazenado:** `string` (1.083 linhas)
- **Quantidade de Valores Preenchidos:** 1.083
- **Quantidade de Nulos:** 0 (0,00%)
- **Quantidade de Valores Distintos:** 7
- **Distribuição de Frequência:**
  - `Visita`: 851 (78,58%)
  - `Reunião`: 90 (8,31%)
  - `Simples`: 63 (5,82%)
  - `WhatsApp`: 56 (5,17%)
  - `Conferência`: 10 (0,92%)
  - `E-mail`: 10 (0,92%)
  - `Telefone`: 3 (0,28%)
- **Diagnóstico & Problemas:** Campo de alta qualidade, 100% preenchido, sem variações ortográficas.
- **Impacto no Power BI:** Dimensão pura de canal/tipo de contato comercial. Excelente para eixos de análise e segmentações.

---

### 1.11. `Criador`
- **Tipo Inferido (Pandas):** `object`
- **Tipo Real Armazenado:** `string` (1.083 linhas)
- **Quantidade de Valores Preenchidos:** 1.083
- **Quantidade de Nulos:** 0 (0,00%)
- **Quantidade de Valores Distintos:** 8
- **Distribuição de Frequência:**
  - `Fernando Bomfoco`: 395 (36,47%)
  - `Priscila Scherer`: 271 (25,02%)
  - `Miriã Kruno`: 191 (17,64%)
  - `Kyanne Reis`: 121 (11,17%)
  - `Google Calendar`: 57 (5,26%)
  - `Cristiana Gehm`: 42 (3,88%)
  - `Informatica`: 5 (0,46%)
  - `Rubem Júnior`: 1 (0,09%)
- **Diagnóstico & Problemas:**
  - Em 75,3% dos casos (815 tarefas), o Criador é a mesma pessoa que executa a tarefa.
  - Em 24,7% dos casos (268 tarefas), o Criador é diferente (ex: sincronização via `Google Calendar` com 57 tarefas, ou secretária/assistente criando para o consultor de campo).
- **Impacto no Power BI:** Deve ser modelado como atributo secundário ou dimensão de Usuário com relação de *Role-Playing* (Criador vs. Responsável).

---

## 2. Análise de Métricas Numéricas e Financeiras

> [!WARNING]
> **Ausência de Dados Transacionais de Faturamento e Preço**
> O arquivo fornecido não contém colunas de valor monetário (R$), preço unitário, custo, margem, desconto ou quantidade vendida de itens.
> As análises de texto evidenciaram que não há valores de moeda embutidos nos campos descritivos.
> Trata-se exclusivamente de uma base de **Atividades Operacionais do CRM** (visitas, ligações, reuniões, contagens de consignado).

---

## 3. Classificação de Colunas Derivadas

Mapeamento de indicadores e campos que devem ou não ser calculados:

| Conceito / Métrica | Natureza | Recomendação de Implementação | Justificativa Técnica |
| :--- | :--- | :--- | :--- |
| **`Data_Sem_Hora`** | Campo de Junção | **(B) Power Query** | Necessário para criar a chave de data inteira (`AAAAMMDD`) e ligar com `d_calendario`. |
| **`Hora_Agendada`** | Atributo Temporal | **(B) Power Query** | Isolar hora para análise de horários de visita sem inflar cardinalidade. |
| **`Tempo_Criacao_Ate_Tarefa`** | Duração (Dias/Horas) | **(B) Power Query** ou **(C) DAX** | Power Query se for usado como faixa/segmentador; DAX se for média ponderada. |
| **`Status_Tarefa`** | Categoria de Status | **(B) Power Query** | Rotular: "Finalizada", "Pendente", "Atrasada" com base na data atual e `Finalizada`. |
| **`Total de Tarefas`** | Medida | **(C) Medida DAX** | `COUNTROWS(f_tarefas)` |
| **`Tarefas Finalizadas`** | Medida | **(C) Medida DAX** | `CALCULATE(COUNTROWS(f_tarefas), f_tarefas[Finalizada] = TRUE)` |
| **`Tarefas Pendentes`** | Medida | **(C) Medida DAX** | `CALCULATE(COUNTROWS(f_tarefas), f_tarefas[Finalizada] = FALSE)` |
| **`% Conclusão`** | Medida | **(C) Medida DAX** | `DIVIDE([Tarefas Finalizadas], [Total de Tarefas])` |
| **`Total de Visitas`** | Medida | **(C) Medida DAX** | `CALCULATE(COUNTROWS(f_tarefas), d_tipo[Tipo] = "Visita")` |
| **`Clientes Ativos em Tarefas`** | Medida | **(C) Medida DAX** | `DISTINCTCOUNT(f_tarefas[Nome do Cliente])` |

---

## 4. Padrões de Negócio Identificados

1. **Predomínio Massivo de Visitas Presenciais:**
   - 78,6% de todas as interações comerciais são visitas *in loco*. A empresa possui uma força de vendas essencialmente de campo (hospitalar/OPME).
2. **Alta Concentração na Equipe de Vendas:**
   - Apenas 3 colaboradores (Fernando Bomfoco, Priscila Scherer e Miriã Kruno) concentram **79,1%** das tarefas atribuídas individualmente.
3. **Foco Hospitalar e Clínico:**
   - Os clientes mais demandantes são grandes operadoras e hospitais do Rio Grande do Sul (ex: `UNIMED VALE DO SINOS`, `HOSPITAL DIVINA PROVIDENCIA`, `HOSPITAL REGINA`, `HOSPITAL SAO LUCAS DA PUCRS`).
4. **Volume Expressivo de Atividades de Consignado e Treinamento:**
   - Termos como `"Contagem OPME"`, `"Contagem de consignado"`, `"Treinamento"`, `"Curso Portocath"` são frequentes nas atividades e marcadores, demonstrando forte atuação no segmento de materiais especiais e cirúrgicos.
