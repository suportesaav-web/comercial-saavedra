import os
import openpyxl
import pandas as pd
import numpy as np
import json

file_path = os.path.join('dados', 'bruto', 'Tarefas Power BI.xlsx')
df = pd.read_excel(file_path, sheet_name='Ploomes')

print("=== INFORMAÇÕES DO NOVO ARQUIVO ===")
print("Dimensões:", df.shape)
print("\nColunas:")
for c in df.columns:
    print(f" - {c} (Tipo: {df[c].dtype})")

new_cols = [
    'Duração',
    'Horário',
    'Negócio',
    'Cliente',
    'Contatos relacionados',
    'E-mail do criador (Google Calendar)'
]

print("\n=== PERFIL DAS 6 NOVAS COLUNAS ===")
for c in new_cols:
    if c not in df.columns:
        print(f"\nColuna '{c}' não encontrada diretamente.")
        continue
    s = df[c]
    val_c = int(s.count())
    null_c = int(s.isnull().sum())
    dist_c = int(s.nunique(dropna=True))
    print(f"\nColuna: '{c}'")
    print(f"  Preenchidos: {val_c} ({val_c/len(df)*100:.1f}%) | Nulos: {null_c} ({null_c/len(df)*100:.1f}%) | Distintos: {dist_c}")
    
    if pd.api.types.is_numeric_dtype(s):
        print(f"  Mín: {s.min()}, Máx: {s.max()}, Média: {s.mean():.1f}, Mediana: {s.median()}")
        print(f"  Zeros: {(s == 0).sum()}, Negativos: {(s < 0).sum()}")
        print(f"  Amostras: {s.dropna().head(5).tolist()}")
    else:
        print(f"  Top 5 valores:\n{s.value_counts(dropna=False).head(5)}")

print("\n=== COMPARAÇÃO: 'Cliente' vs 'Nome do Cliente' ===")
if 'Cliente' in df.columns and 'Nome do Cliente' in df.columns:
    diff_cli = (df['Cliente'] != df['Nome do Cliente']).sum()
    null_cli1 = df['Cliente'].isnull().sum()
    null_cli2 = df['Nome do Cliente'].isnull().sum()
    print(f"Diferenças entre 'Cliente' e 'Nome do Cliente': {diff_cli}")
    print(f"Nulos em 'Cliente': {null_cli1} | Nulos em 'Nome do Cliente': {null_cli2}")
    if diff_cli > 0:
        print("Amostras de divergência:")
        mask_diff = df['Cliente'] != df['Nome do Cliente']
        print(df[mask_diff][['Cliente', 'Nome do Cliente']].head(5))

print("\n=== COMPARAÇÃO: 'Negócio' vs 'Título do Negócio' ===")
if 'Negócio' in df.columns and 'Título do Negócio' in df.columns:
    diff_neg = (df['Negócio'] != df['Título do Negócio']).sum()
    null_neg1 = df['Negócio'].isnull().sum()
    null_neg2 = df['Título do Negócio'].isnull().sum()
    print(f"Diferenças entre 'Negócio' e 'Título do Negócio': {diff_neg}")
    print(f"Nulos em 'Negócio': {null_neg1} | Nulos em 'Título do Negócio': {null_neg2}")
    if diff_neg > 0:
        print("Amostras de divergência:")
        mask_diff = df['Negócio'] != df['Título do Negócio']
        print(df[mask_diff][['Negócio', 'Título do Negócio']].head(5))

print("\n=== ANÁLISE DE 'Contatos relacionados' ===")
if 'Contatos relacionados' in df.columns:
    s_contato = df['Contatos relacionados'].dropna().astype(str)
    print(f"Total de contatos preenchidos: {len(s_contato)}")
    print(f"Contatos distintos: {s_contato.nunique()}")
    has_semi = s_contato.str.contains(';').sum()
    print(f"Contatos com múltiplos nomes (separados por ';'): {has_semi}")
    print("Top 10 contatos:")
    print(s_contato.value_counts().head(10))

print("\n=== ANÁLISE DE 'E-mail do criador (Google Calendar)' ===")
if 'E-mail do criador (Google Calendar)' in df.columns:
    s_email = df['E-mail do criador (Google Calendar)'].dropna().astype(str)
    print(f"Total de e-mails preenchidos: {len(s_email)}")
    print(f"E-mails distintos: {s_email.nunique()}")
    print("Contagem por e-mail:")
    print(s_email.value_counts())

print("\n=== ANÁLISE DE 'Duração' ===")
if 'Duração' in df.columns:
    s_dur = df['Duração'].dropna()
    print("Distribuição da duração (minutos):")
    print(s_dur.describe())
    dur_zero = (s_dur == 0).sum()
    print(f"Tarefas com duração = 0 min: {dur_zero}")
    # Duração média por tipo de tarefa
    print("\nDuração média (minutos) por Tipo de Tarefa:")
    print(df.groupby('Tipo')['Duração'].agg(['count', 'mean', 'median', 'min', 'max']))

print("\n=== ANÁLISE DE 'Horário' ===")
if 'Horário' in df.columns:
    s_hora = df['Horário'].dropna().astype(str)
    print(f"Preenchidos: {len(s_hora)} | Nulos: {df['Horário'].isnull().sum()}")
    print("Top 10 horários mais frequentes:")
    print(s_hora.value_counts().head(10))

