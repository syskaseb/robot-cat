from pathlib import Path
base=Path(__file__).parent
for file in ['support-details.py','cradle-bands.py','neck-guard.py']:
 src=(base/file).read_text().replace('D.save()','pass')
 exec(compile(src,str(base/file),'exec'),{'__file__':str(base/file),'__name__':'__main__'})
import FreeCAD
FreeCAD.ActiveDocument.recompute();FreeCAD.ActiveDocument.save()
