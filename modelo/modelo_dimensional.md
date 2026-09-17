# Modelo Dimensional

Documentação da arquitetura e modelagem dimensional do projeto (Star Schema / Snowflake).

---

## Visão Geral

- **Granularidade da Fato Principal**: (ex: nível de item do pedido / linha de venda)
- **Frequência de Atualização**: Diária / Sob demanda
- **Fonte de Dados**: ERP / Banco de Dados SQL / Planilhas

---

## Diagrama Conceitual (Star Schema)

```mermaid
erDiagram
    d_calendario ||--o{ f_vendas : "data_venda = data"
    d_cliente ||--o{ f_vendas : "id_cliente"
    d_produto ||--o{ f_vendas : "id_produto"
    d_vendedor ||--o{ f_vendas : "id_vendedor"

    f_vendas {
        int id_venda PK
        int id_cliente FK
        int id_produto FK
        int id_vendedor FK
        date data_venda FK
        decimal valor_venda
        int quantidade
    }
```

---

## Regras de Negócio e Relacionamentos

1. **Relacionamentos**: Preferencialmente 1 para N (1:*) com direção de filtro único (Dimensão filtrando Fato).
2. **Surrogate Keys**: Utilização de chaves sintéticas para garantir integridade histórica e performance.
