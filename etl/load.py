"""
Módulo de Carga (Load) - Comercial Saavedra.
Persiste os DataFrames tratados e analíticos no formato colunar Apache Parquet com compressão Snappy.
"""

from pathlib import Path
import os
import pandas as pd
from etl.extract import extract_raw_tasks, get_project_root
from etl.validate import validate_raw_schema
from etl.transform import transform_data


import sys
import argparse
from typing import Callable, Optional, Dict, Any
from etl.extract import extract_raw_tasks, extract_tasks_from_api, get_project_root
from etl.validate import validate_raw_schema
from etl.transform import transform_data


def run_etl(
    file_source=None,
    source: str = "api",
    save_raw_copy: bool = True,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Executa o pipeline completo de ETL:
    1. Extração (via API Ploomes CRM ou arquivo Excel bruto)
    2. Validação de conformidade e schema
    3. Transformação dimensional, regras de negócio e chaves
    4. Carga nos diretórios dados/tratado/ e dados/analitico/ em formato Apache Parquet

    Args:
        file_source: Caminho (str/Path) ou objeto de buffer (BytesIO/UploadedFile). Se informado, força modo Excel.
        source: 'api' para buscar do CRM Ploomes, ou 'excel' para carregar planilha padrão em disco.
        save_raw_copy: Se True e file_source for um buffer, salva cópia em dados/bruto/Tarefas Power BI.xlsx.
        progress_callback: Callback para notificação de progresso na UI.

    Returns:
        dict com estatísticas dos arquivos gerados.
    """
    root = get_project_root()
    tratado_dir = root / "dados" / "tratado"
    analitico_dir = root / "dados" / "analitico"
    bruto_dir = root / "dados" / "bruto"

    tratado_dir.mkdir(parents=True, exist_ok=True)
    analitico_dir.mkdir(parents=True, exist_ok=True)
    bruto_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("INICIANDO PIPELINE DE ETL - COMERCIAL SAAVEDRA")
    print("=" * 60)

    # 1. Extração
    if file_source is not None:
        source_mode = "excel_upload"
        if save_raw_copy and hasattr(file_source, "read"):
            raw_target_path = bruto_dir / "Tarefas Power BI.xlsx"
            try:
                content = file_source.read()
                with open(raw_target_path, "wb") as f:
                    f.write(content)
                if hasattr(file_source, "seek"):
                    file_source.seek(0)
                print(f"      Arquivo bruto atualizado com sucesso em: {raw_target_path.name}")
            except Exception as e:
                print(f"      [AVISO] Não foi possível salvar cópia em disco: {e}")

        print("[1/4] Extraindo dados da planilha fornecida...")
        if progress_callback:
            progress_callback(10, 100, "Extraindo dados do arquivo Excel...")
        df_raw = extract_raw_tasks(file_source)

    elif source.lower() == "api":
        source_mode = "api_ploomes"
        print("[1/4] Extraindo dados diretamente da API Ploomes CRM...")
        df_raw = extract_tasks_from_api(progress_callback=progress_callback)

        # Salva snapshot bruto para contingência e auditoria
        try:
            snapshot_path = bruto_dir / "Tarefas_Ploomes_Snapshot.parquet"
            df_raw.to_parquet(snapshot_path, engine="pyarrow", index=False)
            print(f"      Snapshot bruto salvo em: {snapshot_path.name}")
        except Exception as e:
            print(f"      [AVISO] Snapshot bruto não salvo: {e}")

    else:
        source_mode = "excel_disk"
        print("[1/4] Extraindo dados da planilha bruta em disco...")
        if progress_callback:
            progress_callback(10, 100, "Lendo planilha Excel em disco...")
        df_raw = extract_raw_tasks()

    print(f"      Dados brutos extraídos: {len(df_raw)} linhas (Origem: {source_mode}).")

    # 2. Validação
    print("[2/4] Validando conformidade e schema...")
    if progress_callback:
        progress_callback(50, 100, "Validando schema e consistência dos dados...")
    val_report = validate_raw_schema(df_raw)
    if val_report.get("warnings"):
        for w in val_report["warnings"]:
            print(f"      [AVISO] {w}")

    # 3. Transformação
    print("[3/4] Aplicando transformações, regras de negócio e chaves...")
    if progress_callback:
        progress_callback(75, 100, "Aplicando modelagem dimensional e desaninhamento...")
    df_fato, df_ponte, df_mensal = transform_data(df_raw)
    print(f"      Tabela Fato: {len(df_fato)} linhas, {len(df_fato.columns)} colunas.")
    print(f"      Tabela Ponte: {len(df_ponte)} participações de usuários.")
    print(f"      Camada Analítica Mensal: {len(df_mensal)} agregações pré-computadas.")

    # 4. Carga (Parquet)
    print("[4/4] Gravando arquivos otimizados em Parquet...")
    if progress_callback:
        progress_callback(90, 100, "Gravando arquivos colunares Parquet com compressão Snappy...")

    path_fato = tratado_dir / "tarefas_fato.parquet"
    path_ponte = tratado_dir / "tarefas_usuarios_ponte.parquet"
    path_mensal = analitico_dir / "kpis_agregados_mensais.parquet"
    path_usuarios = tratado_dir / "usuarios_dim.parquet"

    df_fato.to_parquet(path_fato, engine="pyarrow", compression="snappy", index=False)
    df_ponte.to_parquet(path_ponte, engine="pyarrow", compression="snappy", index=False)
    df_mensal.to_parquet(path_mensal, engine="pyarrow", compression="snappy", index=False)

    size_fato = os.path.getsize(path_fato)
    size_ponte = os.path.getsize(path_ponte)
    size_mensal = os.path.getsize(path_mensal)

    # Atualiza a tabela dimensão de usuários do Ploomes CRM
    try:
        from etl.api_client import PloomesClient
        client_u = PloomesClient()
        df_u = client_u.fetch_users_dimension()
        df_u.to_parquet(path_usuarios, engine="pyarrow", compression="snappy", index=False)
        print(f"  - Dimensão Usuários: {path_usuarios.name} ({len(df_u)} cadastrados)")
    except Exception as e:
        print(f"      [AVISO] Não foi possível atualizar dimensão de usuários: {e}")

    if progress_callback:
        progress_callback(100, 100, "Processamento colunar concluído!")

    print("=" * 60)
    print("ETL CONCLUÍDO COM SUCESSO!")
    print(f"  - Origem: {source_mode}")
    print(f"  - Fato Tratada: {path_fato.name} ({size_fato/1024:.1f} KB)")
    print(f"  - Ponte Usuários: {path_ponte.name} ({size_ponte/1024:.1f} KB)")
    print(f"  - Analítico Mensal: {path_mensal.name} ({size_mensal/1024:.1f} KB)")
    print("=" * 60)

    return {
        "status": "success",
        "source": source_mode,
        "fato_path": str(path_fato),
        "fato_rows": len(df_fato),
        "fato_size_kb": round(size_fato / 1024, 2),
        "ponte_path": str(path_ponte),
        "ponte_rows": len(df_ponte),
        "ponte_size_kb": round(size_ponte / 1024, 2),
        "mensal_path": str(path_mensal),
        "mensal_rows": len(df_mensal),
        "mensal_size_kb": round(size_mensal / 1024, 2)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline ETL Comercial Saavedra")
    parser.add_argument(
        "--source",
        choices=["api", "excel"],
        default="api",
        help="Fonte dos dados: 'api' (Ploomes CRM) ou 'excel' (planilha local)"
    )
    args = parser.parse_args()
    run_etl(source=args.source)
