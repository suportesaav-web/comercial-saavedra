import os
import pandas as pd
import numpy as np
import json

file_path = os.path.join('dados', 'bruto', 'Tarefas Power BI.xlsx')
df = pd.read_excel(file_path, sheet_name='Ploomes')

print("=== ANÁLISE DE DATAS ANÔMALAS ===")
print("Distribuição por ano de 'Data':")
print(df['Data'].dt.year.value_counts().sort_index())

print("\nDistribuição por ano de 'Data de criação':")
print(df['Data de criação'].dt.year.value_counts().sort_index())

print("\nRegistros com 'Data' >= 2027:")
future_tasks = df[df['Data'].dt.year >= 2027]
print(future_tasks[['Data', 'Data de criação', 'Título', 'Nome do Cliente', 'Usuários', 'Criador']])

print("\n=== ANÁLISE DE NULOS EM 'Nome do Cliente' E 'Título' ===")
null_client = df[df['Nome do Cliente'].isnull()]
print(f"Linhas sem 'Nome do Cliente' ({len(null_client)}):")
print(null_client[['Data', 'Título', 'Título do Negócio', 'Usuários', 'Criador']])

null_title = df[df['Título'].isnull()]
print(f"\nLinhas sem 'Título' ({len(null_title)}):")
print(null_title[['Data', 'Nome do Cliente', 'Título do Negócio', 'Tipo', 'Usuários', 'Criador']].head(5))

print("\n=== ANÁLISE DE USUÁRIOS INDIVIDUAIS ===")
# Split multi-valued users
all_users = set()
for u_str in df['Usuários'].dropna():
    parts = [p.strip() for p in str(u_str).split(';')]
    all_users.update(parts)
print(f"Total de usuários únicos encontrados no campo 'Usuários': {len(all_users)}")
print("Lista de usuários:", sorted(list(all_users)))

creators = set(df['Criador'].dropna().unique())
print(f"\nTotal de criadores únicos: {len(creators)}")
print("Lista de criadores:", sorted(list(creators)))

diff_users_creators = creators - all_users
print("Criadores que nunca aparecem como Usuários atribuídos:", diff_users_creators)

diff_assigned_creators = all_users - creators
print("Usuários atribuídos que nunca criaram tarefas:", diff_assigned_creators)

print("\n=== ANÁLISE DE CLIENTES ===")
clients = df['Nome do Cliente'].dropna().unique()
print(f"Total de clientes únicos: {len(clients)}")
# Check trailing/leading spaces
ws_clients = [c for c in clients if len(c) != len(c.strip())]
print(f"Clientes com espaços no início/fim: {len(ws_clients)}")

# Check lower case collision
clients_lower = {}
for c in clients:
    cl = c.strip().lower()
    clients_lower.setdefault(cl, []).append(c)
collisions = {k: v for k, v in clients_lower.items() if len(v) > 1}
print(f"Clientes com grafias quase idênticas (diferença apenas de case/espaço): {len(collisions)}")
if collisions:
    print("Colisões:", collisions)

print("\n=== RELAÇÃO 'Nome do Cliente' vs 'Título do Negócio' ===")
# Is a business deal always associated with the same client?
deal_client = df.dropna(subset=['Nome do Cliente', 'Título do Negócio']).groupby('Título do Negócio')['Nome do Cliente'].nunique()
multi_client_deals = deal_client[deal_client > 1]
print(f"Total de 'Título do Negócio': {df['Título do Negócio'].nunique()}")
print(f"Negócios associados a mais de 1 cliente: {len(multi_client_deals)}")
if len(multi_client_deals) > 0:
    print("Exemplos de negócios com múltiplos clientes:")
    print(multi_client_deals.head(5))
    for deal in multi_client_deals.head(3).index:
        print(f"\nDetalhes do negócio '{deal}':")
        print(df[df['Título do Negócio'] == deal][['Nome do Cliente', 'Título', 'Data', 'Usuários']].head(4))

print("\n=== DUPLICIDADES DETALHADAS IGNORANDO 'Data de criação' ===")
dups = df[df.drop(columns=['Data de criação']).duplicated(keep=False)].sort_values(by=['Data', 'Título'])
print(f"Linhas duplicadas exceto 'Data de criação': {len(dups)}")
print(dups[['Data', 'Data de criação', 'Título', 'Nome do Cliente', 'Usuários', 'Tipo']])

print("\n=== TESTES DE CHAVE PRIMÁRIA COMPILADOS ===")
# Let's test combinations
candidates = [
    ['Data', 'Título', 'Nome do Cliente', 'Usuários'],
    ['Data de criação', 'Título', 'Usuários'],
    ['Data de criação', 'Data', 'Usuários'],
    ['Data de criação', 'Nome do Cliente', 'Título'],
    ['Data', 'Data de criação', 'Título', 'Nome do Cliente', 'Usuários', 'Tipo']
]
for c in candidates:
    n_distinct = len(df[c].drop_duplicates())
    print(f"Colunas: {c} -> Distintos: {n_distinct} / {len(df)} ({n_distinct/len(df)*100:.2f}%)")

