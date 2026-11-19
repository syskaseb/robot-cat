from pathlib import Path
import runpy,traceback
P=Path(__file__).parent
try:runpy.run_path(str(P/"integrate-whole-roots.py"),run_name="__main__")
except Exception:(P/"roots-error.txt").write_bytes(traceback.format_exc().encode())
