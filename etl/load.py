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


def run_etl(output_dir: Path | None = None) -> dict:
    """
    Executa o pipeline completo de ETL:
    1. Extração da planilha bruta
    2. Validação do schema e regras de integridade
    3. Transformação e enriquecimento dimensional
    4. Carga nos diretórios dados/tratado/ e dados/analitico/ em formato Parquet

    Returns:
        dict com estatísticas dos arquivos gerados.
    """
    root = get_project_root()
    tratado_dir = root / "dados" / "tratado"
    analitico_dir = root / "dados" / "analitico"

    tratado_dir.mkdir(parents=True, exist_ok=True)
    analitico_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("INICIANDO PIPELINE DE ETL - COMERCIAL SAAVEDRA")
    print("=" * 60)

    # 1. Extração
    print("[1/4] Extraindo dados da planilha bruta...")
    df_raw = extract_raw_tasks()
    print(f"      Dados brutos extraídos: {len(df_raw)} linhas.")

    # 2. Validação
    print("[2/4] Validando conformidade e schema...")
    val_report = validate_raw_schema(df_raw)
    if val_report.get("warnings"):
        for w in val_report["warnings"]:
            print(f"      [AVISO] {w}")

    # 3. Transformação
    print("[3/4] Aplicando transformações, regras de negócio e chaves...")
    df_fato, df_ponte, df_mensal = transform_data(df_raw)
    print(f"      Tabela Fato: {len(df_fato)} linhas, {len(df_fato.columns)} colunas.")
    print(f"      Tabela Ponte: {len(df_ponte)} participações de usuários.")
    print(f"      Camada Analítica Mensal: {len(df_mensal)} agregações pré-computadas.")

    # 4. Carga (Parquet)
    print("[4/4] Gravando arquivos otimizados em Parquet...")
    path_fato = tratado_dir / "tarefas_fato.parquet"
    path_ponte = tratado_dir / "tarefas_usuarios_ponte.parquet"
    path_mensal = analitico_dir / "kpis_agregados_mensais.parquet"

    # Salva com compressão Snappy via pyarrow
    df_fato.to_parquet(path_fato, engine="pyarrow", compression="snappy", index=False)
    df_ponte.to_parquet(path_ponte, engine="pyarrow", compression="snappy", index=False)
    df_mensal.to_parquet(path_mensal, engine="pyarrow", compression="snappy", index=False)

    size_fato = os.path.getsize(path_fato)
    size_ponte = os.path.getsize(path_ponte)
    size_mensal = os.path.getsize(path_mensal)

    print("=" * 60)
    print("ETL CONCLUÍDO COM SUCESSO!")
    print(f"  - Fato Tratada: {path_fato.name} ({size_fato/1024:.1f} KB)")
    print(f"  - Ponte Usuários: {path_ponte.name} ({size_ponte/1024:.1f} KB)")
    print(f"  - Analítico Mensal: {path_mensal.name} ({size_mensal/1024:.1f} KB)")
    print("=" * 60)

    return {
        "status": "success",
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
    run_etl()
