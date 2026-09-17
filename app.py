"""
Ponto de entrada raiz da aplicação Streamlit Comercial Saavedra.
Permite iniciar o dashboard executando diretamente na raiz do projeto:
    streamlit run app.py
ou
    streamlit run app/app.py
"""

import sys
from pathlib import Path
import runpy

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

target_app = project_root / "app" / "app.py"
runpy.run_path(str(target_app), run_name="__main__")
