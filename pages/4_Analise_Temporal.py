import sys
from pathlib import Path
import runpy

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

target = project_root / "app" / "pages" / "4_Analise_Temporal.py"
runpy.run_path(str(target), run_name="__main__")
