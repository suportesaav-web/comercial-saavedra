# Dicionário de Dados

Este documento descreve as tabelas, colunas, tipos de dados e descrições das entidades utilizadas no modelo de BI.

---

## Tabelas Dimensão

### d_exemplo
| Coluna | Tipo de Dado | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `id_exemplo` | Inteiro | Chave primária / surrogate key | `1` |
| `nome` | Texto | Nome ou descrição | `Exemplo A` |

---

## Tabelas Fato

### f_vendas (Exemplo)
| Coluna | Tipo de Dado | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `id_venda` | Inteiro | Identificador único da venda | `1001` |
| `id_cliente` | Inteiro | Chave estrangeira para d_cliente | `50` |
| `data_venda` | Data | Data em que a venda foi realizada | `2026-01-15` |
| `valor_total` | Decimal | Valor total faturado | `150.00` |
