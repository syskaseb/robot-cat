from pathlib import Path
import runpy,traceback
P=Path(__file__).parent
try:runpy.run_path(str(P/"finish-port-space.py"),run_name="__main__")
except Exception:(P/"final-space-error.txt").write_bytes(traceback.format_exc().encode())
