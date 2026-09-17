# Arquitetura da Aplicação Web Analítica - Comercial Saavedra

Este documento detalha a arquitetura técnica, fluxo de dados, organização de pastas, dependências, rotinas operacionais e guia de deploy da aplicação analítica construída em **Python + Streamlit + Plotly + Apache Parquet** para o projeto **Comercial Saavedra**.

---

## 1. Visão Geral e Princípios Arquiteturais

A aplicação foi projetada com base em quatro princípios fundamentais de engenharia de software e analytics:

1. **Desacoplamento entre Extração e Apresentação:**
   - A aplicação Streamlit **nunca lê o arquivo Excel bruto diretamente**.
   - As transformações pesadas, sanitizações e cálculos de chaves são executados previamente pelo pipeline de ETL e salvos em arquivos colunares Parquet.
2. **Armazenamento em Formato Apache Parquet:**
   - Redução drástica do tempo de I/O (< 5 ms de carregamento).
   - Preservação estrita de tipagem colunar (`Date`, `Time`, `Boolean`, `Int64`).
   - Tamanho reduzido em disco com compressão Snappy.
3. **Modularidade e Reutilização:**
   - Separação clara de responsabilidades: ETL, Configurações, Carregadores de Dados com Cache, Filtros, Componentes Visuais, Métricas e Páginas.
4. **Fidelidade Rigorosa aos Dados Reais:**
   - Métricas, páginas e dimensões 100% aderentes à realidade do CRM Ploomes (atividades, visitas, reuniões, consultores, clientes e negócios), sem inventar dados de faturamento ou vendas inexistentes na fonte.

---

## 2. Fluxo Completo dos Dados (Pipeline)

```
[1. Fonte Bruta]
dados/bruto/Tarefas Power BI.xlsx (Excel Ploomes, 1.083 tarefas)
       │
       ▼
[2. Camada de Engenharia de Dados (ETL)]
etl/extract.py     ──> Lê a aba 'Ploomes' com openpyxl/pandas
etl/validate.py    ──> Valida integridade, schema e limites
etl/transform.py   ──> Aplica regras de negócio:
                       - Cria Surrogate Key inteira (sk_tarefa: 1..N)
                       - Substitui nulos de clientes por "Cliente Não Informado"
                       - Gera títulos substitutos para as 14 tarefas vazias
                       - Separa data_evento (Date) e hora_evento (Time)
                       - Calcula lead_time_dias (data_evento - data_criacao)
                       - Constrói a tabela-ponte despivotada (tarefas_usuarios_ponte)
                       - Pré-computa agregações mensais (kpis_agregados_mensais)
etl/load.py        ──> Grava arquivos Parquet com compressão Snappy
       │
       ▼
[3. Camada de Dados Otimizados]
dados/tratado/tarefas_fato.parquet               (1.083 linhas, 28 colunas)
dados/tratado/tarefas_usuarios_ponte.parquet     (1.596 participações)
dados/analitico/kpis_agregados_mensais.parquet   (70 agregações temporais)
       │
       ▼
[4. Camada Analítica Web (Streamlit)]
app/data/loader.py                  ──> Carrega Parquets com @st.cache_data
app/filters/sidebar_filters.py      ──> Aplica filtros reativos e bidirecionais
app/analytics/ & app/charts/        ──> Computa KPIs e gráficos interativos Plotly
app/pages/                          ──> Renderiza os dashboards modulares
```

---

## 3. Estrutura de Diretórios do Projeto

```
comercial-saavedra/
├── app/                                 # Aplicação Web Analítica
│   ├── app.py                           # Ponto de entrada (Hub & Visão Geral)
│   ├── config/                          # Configurações globais e temas
│   │   ├── __init__.py
│   │   └── settings.py                  # Constantes de layout, cores corporativas e caminhos
│   ├── data/                            # Camada de acesso a dados
│   │   ├── __init__.py
│   │   └── loader.py                    # Carregador com cache (@st.cache_data)
│   ├── filters/                         # Filtros da interface
│   │   ├── __init__.py
│   │   └── sidebar_filters.py           # Componente único de filtros da barra lateral
│   ├── components/                      # Componentes reutilizáveis
│   │   ├── __init__.py
│   │   ├── kpi_cards.py                 # Renderizador de cards de KPIs e métricas
│   │   └── ui.py                        # Cabeçalhos padronizados, badges e banners
│   ├── analytics/                       # Motor analítico
│   │   ├── __init__.py
│   │   ├── metrics.py                   # Funções puras de cálculo de indicadores
│   │   └── aggregations.py              # Agrupamentos para gráficos e matrizes
│   ├── charts/                          # Visualizações Plotly
│   │   ├── __init__.py
│   │   ├── temporal.py                  # Linha do tempo e distribuição de lead time
│   │   ├── ranking.py                   # Barras horizontais e comparativos de equipe
│   │   └── distribution.py              # Rosca de categorias e mapa de calor
│   ├── utils/                           # Utilitários
│   │   ├── __init__.py
│   │   └── export.py                    # Gerador de downloads em CSV e Excel (XLSX)
│   └── pages/                           # Páginas navegáveis do Streamlit
│       ├── 1_Visao_Geral.py             # Visão executiva macro
│       ├── 2_Vendedores_e_Equipe.py     # Desempenho e participações da equipe
│       ├── 3_Clientes_e_Negocios.py     # Cobertura de contas hospitalares
│       ├── 4_Analise_Temporal.py        # Sazonalidade, horários e lead time
│       └── 5_Detalhamento_Operacional.py# Tabela detalhada e exportações
│
├── etl/                                 # Pipeline de Engenharia de Dados
│   ├── __init__.py
│   ├── extract.py                       # Extração da planilha bruta
│   ├── validate.py                      # Validações de integridade estrutural
│   ├── transform.py                     # Regras de limpeza, SKs e desaninhamento
│   └── load.py                          # Escrita dos arquivos Parquet
│
├── dados/
│   ├── bruto/                           # Arquivo bruto original (Tarefas Power BI.xlsx)
│   ├── tratado/                         # tarefas_fato.parquet, tarefas_usuarios_ponte.parquet
│   └── analitico/                       # kpis_agregados_mensais.parquet
│
└── documentacao/
    ├── arquitetura_app.md               # Este documento
    ├── inventario_base.md               # Inventário do arquivo bruto
    ├── analise_exploratoria.md          # Análise descritiva detalhada
    ├── chaves_e_relacionamentos.md      # Modelagem dimensional e chaves
    ├── granularidade.md                 # Comprovação de granularidade
    ├── qualidade_dados.md               # Relatório de qualidade e anomalias
    └── scripts_analise/                 # Scripts Python de auditoria
```

---

## 4. Dependências de Software

A aplicação utiliza bibliotecas padrão de engenharia de dados e web analytics em Python:

```toml
python = ">=3.10"
streamlit = ">=1.30.0"
pandas = ">=2.0.0"
openpyxl = ">=3.1.0"
pyarrow = ">=14.0.0"
plotly = ">=5.18.0"
```

---

## 5. Como Executar Localmente

### Pré-requisitos:
Certifique-se de que o Python está instalado e as bibliotecas acima estão disponíveis no ambiente.

### Passo 1: Executar o Pipeline de ETL (Carga Inicial ou Atualização)
No terminal, dentro da pasta raiz do projeto (`comercial-saavedra`):
```bash
python -m etl.load
```
*Saída esperada:* Geração dos 3 arquivos Parquet em `dados/tratado/` e `dados/analitico/`.

### Passo 2: Iniciar a Aplicação Streamlit
```bash
streamlit run app/app.py
```
A aplicação iniciará automaticamente e abrirá o navegador no endereço padrão:
`http://localhost:8501`

---

## 6. Como Atualizar os Dados

Sempre que um novo arquivo Excel for exportado do Ploomes:

1. Substitua o arquivo em `dados/bruto/Tarefas Power BI.xlsx` (ou mantenha o mesmo nome).
2. Execute o comando de ETL:
   ```bash
   python -m etl.load
   ```
3. Abra a aplicação Streamlit e clique no botão **"Recarregar Dados"** ou reinicie a sessão para que o `@st.cache_data` recarregue os Parquets atualizados.

---

## 7. Como Adicionar Novas Análises ou Páginas

A arquitetura modular facilita a expansão sem alterar o código existente:

1. **Adicionar uma Nova Página:**
   - Crie um arquivo no diretório `app/pages/` seguindo o padrão de numeração, por exemplo: `6_Nova_Analise.py`.
   - O Streamlit registrará a nova página automaticamente no menu lateral.
2. **Adicionar Novos Gráficos:**
   - Crie a função de renderização em `app/charts/` utilizando Plotly e as cores padronizadas de `app/config/settings.py`.
3. **Adicionar Novas Agregações ou Métricas:**
   - Adicione funções puras em `app/analytics/metrics.py` ou `app/analytics/aggregations.py`.
   - Teste a função isoladamente antes de integrá-la aos visuais.

---

## 8. Estratégia de Deploy em Produção

A aplicação é *stateless* e totalmente autocontida, permitindo múltiplos cenários de publicação:

### Opção A: Servidor Interno / Máquina Virtual (Windows Server / Linux)
1. Instale Python e as dependências: `pip install -r requirements.txt`.
2. Configure um serviço do sistema (ex: *Windows Service* ou *systemd* no Linux) para manter o Streamlit rodando:
   ```bash
   streamlit run app/app.py --server.port=8501 --server.address=0.0.0.0
   ```
3. Configure o agendador de tarefas do Windows (*Task Scheduler*) ou *Cron* para executar `python -m etl.load` diariamente após o fechamento comercial.

### Opção B: Streamlit Community Cloud / Docker
1. Crie um `requirements.txt` com as dependências listadas na Seção 4.
2. Configure o arquivo `.streamlit/config.toml` para ajustes de tema e porta.
3. No Docker, utilize uma imagem leve `python:3.11-slim`, copie o repositório e defina o `ENTRYPOINT ["streamlit", "run", "app/app.py"]`.

---

## 9. Governança e Boas Práticas Adotadas

- **Cache inteligente com `@st.cache_data(ttl=3600)`**: Reduz o custo de processamento a zero após o primeiro carregamento.
- **Tratamento de Exceções**: A aplicação valida se os Parquets existem e executa o ETL em lote automaticamente caso detecte ausência de dados.
- **Exportação com Formatação Regional (pt-BR)**: Os downloads em CSV são gerados com ponto-e-vírgula (`;`) e assinatura `utf-8-sig` para compatibilidade imediata com o Microsoft Excel em português.
