import os
import pandas as pd
import numpy as np
import json

file_path = os.path.join('dados', 'bruto', 'Tarefas Power BI.xlsx')
df = pd.read_excel(file_path, sheet_name='Ploomes')

print("=== COLUNAS E TIPOS ===")
print(df.dtypes)

print("\n=== RESUMO GERAL ===")
print(f"Total de Linhas: {len(df)}")
print(f"Total de Colunas: {len(df.columns)}")

print("\n=== NULOS POR COLUNA ===")
print(df.isnull().sum())

print("\n=== DISTINTOS POR COLUNA ===")
print(df.nunique(dropna=False))

print("\n=== MULTI-VALORES / DELIMITADORES EM TEXTOS ===")
for col in ['Usuários', 'Marcadores', 'Tipo', 'Criador']:
    if col in df.columns:
        s = df[col].dropna().astype(str)
        has_comma = s.str.contains(',').sum()
        has_semicolon = s.str.contains(';').sum()
        has_pipe = s.str.contains(r'\|').sum()
        print(f"Coluna '{col}': com vírgula={has_comma}, com ponto-e-vírgula={has_semicolon}, com pipe={has_pipe}")

print("\n=== VALORES DISTINTOS DE 'Tipo' ===")
print(df['Tipo'].value_counts(dropna=False))

print("\n=== VALORES DISTINTOS DE 'Finalizada' ===")
print(df['Finalizada'].value_counts(dropna=False))

print("\n=== TOP 10 'Usuários' ===")
print(df['Usuários'].value_counts(dropna=False).head(10))

print("\n=== TOP 10 'Criador' ===")
print(df['Criador'].value_counts(dropna=False).head(10))

print("\n=== RELAÇÃO USUÁRIO vs CRIADOR ===")
same_user = (df['Usuários'] == df['Criador']).sum()
diff_user = (df['Usuários'] != df['Criador']).sum()
print(f"Mesmo Usuário e Criador: {same_user} ({same_user/len(df)*100:.1f}%)")
print(f"Diferentes: {diff_user} ({diff_user/len(df)*100:.1f}%)")

print("\n=== MARCADORES (TAGS) ===")
print(df['Marcadores'].value_counts(dropna=False).head(15))

print("\n=== DATAS ===")
for col in ['Data', 'Data de criação']:
    print(f"\nColuna '{col}':")
    print(f"  Min: {df[col].min()}")
    print(f"  Max: {df[col].max()}")
    print(f"  Nulos: {df[col].isnull().sum()}")

# Difference between Data and Data de criação
df['diff_dias'] = (df['Data'] - df['Data de criação']).dt.total_seconds() / 86400.0
print("\nDiferença em dias (Data - Data de criação):")
print(df['diff_dias'].describe())

print("\n=== ANÁLISE DE EXTRAÇÃO DE NÚMEROS / VALORES / MOEDAS EM TEXTOS ===")
# Check if Título, Título do Negócio, or Descrição contain numbers, currency, units
for col in ['Título', 'Descrição', 'Título do Negócio']:
    s = df[col].dropna().astype(str)
    has_currency = s.str.contains(r'R\$|\$', regex=True).sum()
    has_numbers = s.str.contains(r'\d+', regex=True).sum()
    print(f"Coluna '{col}': mencao moeda={has_currency}, contem digitos={has_numbers}")

# Sample lines with currency
for col in ['Título', 'Descrição', 'Título do Negócio']:
    s = df[col].dropna().astype(str)
    curr_samples = s[s.str.contains(r'R\$|\$', regex=True)]
    if not curr_samples.empty:
        print(f"\nExemplos de valores monetários em '{col}':")
        print(curr_samples.head(5).tolist())

print("\n=== VERIFICAÇÃO DE DUPLICIDADES TOTAIS E PARCIAIS ===")
full_dups = df.drop(columns=['diff_dias']).duplicated(keep=False)
print(f"Linhas idênticas em TODAS as 11 colunas: {full_dups.sum()}")
if full_dups.sum() > 0:
    print(df[full_dups].sort_values(by=['Data de criação', 'Título']).head(6))

# Duplicates ignoring 'Data de criação'
dups_no_created = df.drop(columns=['diff_dias', 'Data de criação']).duplicated(keep=False)
print(f"\nLinhas idênticas ignorando 'Data de criação': {dups_no_created.sum()}")

