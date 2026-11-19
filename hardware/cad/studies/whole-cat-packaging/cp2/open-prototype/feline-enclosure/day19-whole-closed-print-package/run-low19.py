"""Run the current whole allocation once and persist any native exception."""
from pathlib import Path
import runpy,traceback,json,datetime
P=Path(__file__).parent
try:
    runpy.run_path(str(P/"make-low-layout.py"),run_name="__main__")
    runpy.run_path(str(P/"build-whole-envelope.py"),run_name="__main__")
except Exception:
    (P/"native-error.txt").write_bytes(traceback.format_exc().encode())
    print(traceback.format_exc())
