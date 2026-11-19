from pathlib import Path
P=Path(__file__).parent
for file in ['vertical-bank.py','keeper-seats.py']:
 exec(compile((P/file).read_text(),str(P/file),'exec'),{'__file__':str(P/file),'__name__':'__main__'})
import FreeCAD
FreeCAD.ActiveDocument.recompute();FreeCAD.ActiveDocument.save()
