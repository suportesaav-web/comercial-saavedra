# Relatório de Qualidade dos Dados - Comercial Saavedra

Este documento consolida a auditoria de qualidade de dados da base bruta `Tarefas Power BI.xlsx` (aba `Ploomes`), categorizando as anomalias por severidade, quantificando seus impactos e definindo as recomendações de tratamento.

---

## 1. Resumo da Qualidade por Nível de Severidade

| Nível de Severidade | Quantidade de Problemas Mapeados | Impacto no Power BI |
| :--- | :---: | :--- |
| **CRÍTICO** | 2 | Impossibilita modelagem dimensional correta e integridade de chaves. |
| **ALTO** | 3 | Gera distorções temporais e falhas em filtros dimensionais básicos. |
| **MÉDIO** | 4 | Inchaço de memória no VertiPaq e risco de relacionamentos N:N ambíguos. |
| **BAIXO** | 3 | Desalinhamentos estéticos e poluição de rótulos visuais. |

---

## 2. Detalhamento dos Problemas Identificados

### 2.1. Nível: CRÍTICO

#### Problema C-01: Ausência de Chave Primária Corporativa (Task ID)
- **Tabela:** `Ploomes`
- **Coluna:** Nenhuma (coluna de ID não existe no arquivo)
- **Problema:** A exportação do CRM não trouxe o código identificador nativo da tarefa (`Id`). Nenhuma coluna isolada é 100% única.
- **Quantidade Afetada:** 1.083 linhas (100% da base)
- **Exemplo:** Linhas distintas que compartilham todos os metadados temporais e comerciais.
- **Impacto no Power BI:** Risco de duplicação indevida em agregações, impossibilidade de criar relacionamentos determinísticos ou rastrear atualizações incrementais.
- **Recomendação Técnica:** No Power Query, adicionar uma Surrogate Key inteira sequencial (`SK_Tarefa`). Solicitar à equipe de CRM a inclusão do campo `Id` nas próximas extrações.

---

#### Problema C-02: Campo Multivalorado em `Usuários` (Violação da 1ª Forma Normal)
- **Tabela:** `Ploomes`
- **Coluna:** `Usuários`
- **Problema:** Múltiplos colaboradores agrupados em uma única célula de texto separados por ponto-e-vírgula (`;`).
- **Quantidade Afetada:** 220 linhas (20,31% da base)
- **Exemplo:** `"Kyanne Reis; Fernando Bomfoco; Priscila Scherer; Miriã Kruno; Saulo Scherer; Cristiana Gehm"`
- **Impacto no Power BI:** Impossibilita relacionar a fato de tarefas com uma dimensão de colaboradores/vendedores de forma 1:N direta. Filtrar por vendedor omitirá ou duplicará tarefas em visuais analíticos.
- **Recomendação Técnica:** Criar no Power Query uma tabela-ponte (*Bridge Table*) despivotando os usuários por `SK_Tarefa`, mantendo a fato principal com o primeiro usuário como responsável primário.

---

### 2.2. Nível: ALTO

#### Problema A-01: Datas Futuras Anômalas / Erro de Digitação
- **Tabela:** `Ploomes`
- **Coluna:** `Data`
- **Problema:** Presença de tarefas com anos `2027` e `2032` em uma base focada no biênio 2025/2026.
- **Quantidade Afetada:** 2 linhas (0,18% da base)
- **Exemplo:**
  - Linha 37: `2027-07-01 08:00:00` (Criada em 2025)
  - Linha 317: `2032-04-28 14:30:00` (Criada em 2025 por Miriã Kruno)
- **Impacto no Power BI:** Se uma tabela `d_calendario` for gerada por funções automáticas como `CALENDAR(MIN(), MAX())`, ela gerará centenas de milhares de linhas vazias cobrindo anos inexistentes até 2032, degradando filtros e performance.
- **Recomendação Técnica:** Aplicar regra de validação no Power Query: limitar a dimensão calendário a `Ano Atual + 1` e sinalizar essas tarefas anômalas para correção na origem (Ploomes).

---

#### Problema A-02: Cliente com Valor NULO
- **Tabela:** `Ploomes`
- **Coluna:** `Nome do Cliente`
- **Problema:** Registro sem identificação de cliente associado a uma contagem de consignado.
- **Quantidade Afetada:** 1 linha (0,09% da base - Linha de índice 2)
- **Exemplo:** `Data: 2025-02-06 11:00:00`, `Título: Contagem de consignado`, `Título do Negócio: Contagem Consignad`, `Nome do Cliente: NaN`
- **Impacto no Power BI:** Criação de linha em branco automática na dimensão `d_cliente` do Power BI ou perda de integridade referencial.
- **Recomendação Técnica:** Aplicar substituição de valor no Power Query (`if [Nome do Cliente] = null then "Cliente Não Informado" else [Nome do Cliente]`).

---

#### Problema A-03: Ausência de Identificadores de Negócio / Chaves de Entidade
- **Tabela:** `Ploomes`
- **Colunas:** `Nome do Cliente`, `Título do Negócio`, `Usuários`, `Criador`
- **Problema:** Todos os relacionamentos dependem exclusivamente de strings textuais abertas sujeitas a variações de digitação, sem códigos numéricos ou IDs de ERP/CRM.
- **Quantidade Afetada:** 1.083 linhas (100% da base)
- **Exemplo:** Negócios homônimos para clientes diferentes (`REAJUSTE DE PREÇO 2026 - MAT. MED.` ocorre em 16 hospitais distintos).
- **Impacto no Power BI:** Relações podem se tornar $N:N$ ou mesclar dados de contextos comerciais distintos.
- **Recomendação Técnica:** Criar chaves substitutas compostas (`Nome do Cliente + Título do Negócio`) para desambiguação até que os IDs do sistema sejam fornecidos.

---

### 2.3. Nível: MÉDIO

#### Problema M-01: Duplicidade Quase Idêntica de Tarefas (Reenvio / Clique Duplo)
- **Tabela:** `Ploomes`
- **Colunas:** Todas
- **Problema:**
  - As linhas 718 e 805 possuem os mesmos cliente, negócio, data, usuários, criador e a **mesma data de criação até o milissegundo** (`2026-08-03 15:29:43.940`), diferindo apenas por um detalhe de formatação na descrição.
  - Outras 7 linhas são duplicadas em todas as colunas exceto o timestamp de criação (intervalo de segundos).
- **Quantidade Afetada:** 9 linhas (0,83% da base)
- **Exemplo:** Linha 693 e 694 (WhatsApp enviado por Priscila Scherer no mesmo dia com 10 segundos de intervalo).
- **Impacto no Power BI:** Infla a contagem de tarefas operacionais realizadas.
- **Recomendação Técnica:** Analisar com a área de negócio se atividades com mesmo título, cliente, data e usuário em intervalo inferior a 1 minuto devem ser desduplicadas no Power Query.

---

#### Problema M-02: Mistura de Data e Hora com Milissegundos em Colunas Temporais
- **Tabela:** `Ploomes`
- **Colunas:** `Data` e `Data de criação`
- **Problema:** As colunas contêm componentes de hora, minuto, segundo e milissegundo.
- **Quantidade Afetada:** 1.083 linhas (100%)
- **Exemplo:** `2026-09-17 07:44:14.527000`
- **Impacto no Power BI:** Alta cardinalidade inútil no mecanismo VertiPaq. Uma coluna `DateTime` com milissegundos consome até 10x mais memória do que uma coluna `Date` pura.
- **Recomendação Técnica:** No Power Query, transformar `Data` em tipo `Date` para relacionar com a `d_calendario` e extrair a hora em coluna separada `Time`.

---

#### Problema M-03: Campo `Marcadores` (Tags) com Alta Vacância e Multivalores
- **Tabela:** `Ploomes`
- **Coluna:** `Marcadores`
- **Problema:** 58,17% dos registros não possuem marcador preenchido e 3 linhas contêm múltiplos marcadores combinados por ponto-e-vírgula.
- **Quantidade Afetada:** 630 nulos (58,17%) e 3 multivalorados
- **Exemplo:** `"PISTOLA; Contagem OPME; Visita Recorrente"`
- **Impacto no Power BI:** Filtros de tag incompletos e quebra de granularidade em relatórios segmentados.
- **Recomendação Técnica:** Padronizar nulos como `"Sem Marcador"` e tratar valores combinados.

---

#### Problema M-04: Criação de Tarefas em Lote sem Rastreabilidade
- **Tabela:** `Ploomes`
- **Coluna:** `Data de criação`
- **Problema:** 25 grupos de timestamps idênticos, somando 121 tarefas geradas exatamente no mesmo milissegundo (tarefas recorrentes agendadas em lote).
- **Quantidade Afetada:** 121 linhas (11,17% da base)
- **Exemplo:** 26 tarefas criadas no timestamp `2026-03-23 07:39:43.077`.
- **Impacto no Power BI:** Pode distorcer análises de "quando o vendedor registrou a atividade" se não for distinguido o agendamento em lote da realização real.
- **Recomendação Técnica:** Manter documentado que `Data de criação` reflete o lote de agendamento no CRM, e `Data` reflete a data pretendida do evento.

---

### 2.4. Nível: BAIXO

#### Problema B-01: Tarefas sem Título
- **Tabela:** `Ploomes`
- **Coluna:** `Título`
- **Problema:** Tarefas cadastradas no CRM sem preenchimento do campo título.
- **Quantidade Afetada:** 14 linhas (1,29%)
- **Exemplo:** Tarefas de visita criadas por Priscila Scherer e Kyanne Reis com título em branco.
- **Impacto no Power BI:** Exibição de valores vazios em matrizes e tabelas visuais.
- **Recomendação Técnica:** Substituir por `[Tipo] & " - " & [Nome do Cliente]` ou `"Tarefa sem Título"`.

---

#### Problema B-02: Espaços em Branco no Início e Fim de Nomes de Clientes
- **Tabela:** `Ploomes`
- **Coluna:** `Nome do Cliente`
- **Problema:** Espaços em branco acidentais digitados nas bordas dos textos.
- **Quantidade Afetada:** 4 clientes (ex: `"Joseane  Arruda Secretária Dr. Gusmão quadril "`)
- **Impacto no Power BI:** Se houver no futuro uma tabela dimensão importada de ERP sem os espaços, o Power BI não relacionará os nomes ou criará clientes duplicados.
- **Recomendação Técnica:** Aplicar `Text.Trim` em todas as colunas de texto no Power Query.

---

#### Problema B-03: Descrições Longas e Ricas Não Estruturadas
- **Tabela:** `Ploomes`
- **Coluna:** `Descrição`
- **Problema:** 62,14% de valores nulos e 37,86% com anotações livres, quebras de linha e textos longos.
- **Quantidade Afetada:** 673 nulos
- **Impacto no Power BI:** Poluição do arquivo pbix se carregado integralmente sem necessidade visual.
- **Recomendação Técnica:** Avaliar remoção da coluna da fato principal ou mantê-la apenas em tabela de detalhamento pontual.
