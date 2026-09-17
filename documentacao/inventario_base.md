# Inventário da Base de Dados - Comercial Saavedra

Este documento apresenta o inventário técnico e estrutural detalhado do arquivo de dados bruto fornecido para o projeto de BI da **Comercial Saavedra**.

---

## 1. Metadados do Arquivo

| Atributo | Valor Identificado | Observações Técnicas |
| :--- | :--- | :--- |
| **Nome do Arquivo** | `Tarefas Power BI.xlsx` | Arquivo bruto armazenado em `dados/bruto/` |
| **Extensão** | `.xlsx` | Formato Microsoft Excel OpenXML Spreadsheet |
| **Tamanho do Arquivo** | `89.699 bytes` (~87,60 KB) | Arquivo leve, exportado diretamente de CRM |
| **Quantidade de Abas** | `1 aba` | Apenas uma pasta de trabalho ativa |
| **Nome da Aba** | `Ploomes` | Indica origem dos dados no CRM Ploomes |
| **Total de Linhas no Excel** | `1.084 linhas` | 1 linha de cabeçalho + 1.083 linhas de dados |
| **Total de Colunas no Excel** | `11 colunas` | Colunas preenchidas de A a K |
| **Linhas de Dados Efetivas** | `1.083 linhas` | Sem linhas de totalizadores no rodapé |
| **Linhas Totalmente Vazias** | `0` | Nenhuma linha em branco detectada |
| **Colunas Totalmente Vazias**| `0` | Todas as 11 colunas contêm dados |

---

## 2. Inspeção Estrutural da Planilha

| Critério de Inspeção | Status | Detalhes |
| :--- | :--- | :--- |
| **Fórmulas do Excel** | **Ausentes (0)** | Todos os 11.913 valores armazenados são literais/estáticos. Nenhuma célula utiliza fórmulas (`=SOMA`, `=PROCV`, etc.). |
| **Células Mescladas** | **Ausentes (0)** | Nenhuma célula mesclada detectada na planilha. Layout tabular uniforme. |
| **Linhas Ocultas** | **Ausentes (0)** | Nenhuma linha com propriedade `hidden=True`. |
| **Colunas Ocultas** | **Ausentes (0)** | Nenhuma coluna com propriedade `hidden=True`. |
| **Estrutura de Cabeçalhos** | **Linha 1 Única** | Não existem cabeçalhos hierárquicos ou em múltiplas linhas. Cabeçalho direto na linha 1. |
| **Caracteres Especiais nos Cabeçalhos** | **Presentes** | Cabeçalhos contêm acentuação (`Título`, `Descrição`, `Usuários`, `Data de criação`). Recomenda-se normalização no Power Query. |

---

## 3. Cobertura Temporal Aparente

| Campo de Data | Data Mínima | Data Máxima | Intervalo | Observações |
| :--- | :--- | :--- | :--- | :--- |
| **`Data de criação`** | `29/01/2025 11:09:35` | `17/09/2026 07:44:14` | ~20 meses | Data e hora em que a tarefa foi inserida no CRM (inclui milissegundos). |
| **`Data`** | `29/01/2025 11:00:00` | `28/04/2032 14:30:00` | > 7 anos | Data e hora agendada/realizada da tarefa. Contém 2 datas futuras anômalas (`01/07/2027` e `28/04/2032`). |

---

## 4. Relação das Colunas e Tipos de Armazenamento

| Índice | Coluna | Tipo Inferido (Pandas) | Tipos Reais no Excel (OpenPyXL) | Preenchidos | Nulos | % Nulos |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| 0 | `Título` | `object (string)` | `str`, `NoneType` | 1.069 | 14 | 1,29% |
| 1 | `Descrição` | `object (string)` | `str`, `NoneType` | 410 | 673 | 62,14% |
| 2 | `Finalizada` | `bool` | `bool` | 1.083 | 0 | 0,00% |
| 3 | `Data` | `datetime64[ns]` | `datetime` | 1.083 | 0 | 0,00% |
| 4 | `Nome do Cliente` | `object (string)` | `str`, `NoneType` | 1.082 | 1 | 0,09% |
| 5 | `Título do Negócio`| `object (string)` | `str` | 1.083 | 0 | 0,00% |
| 6 | `Usuários` | `object (string)` | `str` | 1.083 | 0 | 0,00% |
| 7 | `Marcadores` | `object (string)` | `str`, `NoneType` | 453 | 630 | 58,17% |
| 8 | `Data de criação` | `datetime64[ns]` | `datetime` | 1.083 | 0 | 0,00% |
| 9 | `Tipo` | `object (string)` | `str` | 1.083 | 0 | 0,00% |
| 10 | `Criador` | `object (string)` | `str` | 1.083 | 0 | 0,00% |

---

## 5. Diagnóstico de Adequação para Power BI

* **O que foi identificado:** Arquivo tabular limpo em formato Excel de uma única aba (`Ploomes`), sem mesclagens ou linhas em branco, contendo 1.083 tarefas de CRM.
* **Problema existente:** Ausência de ID primário da tarefa, ausência de valores numéricos/métricas financeiras, datas futuras distorcidas e presença de campos multivalorados (`Usuários` separados por `;`).
* **Solução recomendada:** Tratamento dessas inconsistências no Power Query e enriquecimento da modelagem com dimensões e chaves sintéticas antes da ingestão final.
* **Impacto no Power BI:** Carga direta sem tratamento resultaria em distorção da dimensão calendário (datas até 2032) e impossibilidade de relacionar colaboradores de forma 1:N.
