from pathlib import Path
import runpy,traceback
P=Path(__file__).parent
try:runpy.run_path(str(P/"correct-whole-allocation.py"),run_name="__main__")
except Exception:(P/"correction-error.txt").write_bytes(traceback.format_exc().encode())
