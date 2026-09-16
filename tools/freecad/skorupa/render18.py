"""Capture the real FreeCAD assembly and interior, then leave it CLOSED."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui

root=Path(__file__).resolve().parents[3]
out=root/'hardware/skorupa/v18'
doc=App.getDocument('Kot_v18_SKORUPA_DZIELONA')
App.setActiveDocument(doc.Name)
view=Gui.getDocument(doc.Name).activeView()
if hasattr(Gui,'Snapper') and Gui.Snapper.grid:
    Gui.Snapper.grid.off()
view.setAxisCross(False)
view.setCameraType('Orthographic')
def camera(z,x):
    view.setCameraOrientation(App.Rotation(x,z.cross(x),z,'ZXY').Q)
    view.fitAll()
    node=view.getCameraNode()
    node.height.setValue(node.height.getValue()*0.85)

parts=[doc.getObject(n) for n in ('ShellFront18','ShellRear18')]
highlight=[doc.getObject(n) for n in ('PiTray18','ShellJoinL','ShellJoinR')]
colours=[o.ViewObject.ShapeColor for o in highlight]
try:
    for o in parts: o.Visibility=False
    for o in highlight: o.ViewObject.ShapeColor=(0.95,0.48,0.12)
    camera(App.Vector(-0.8,-1.5,2),App.Vector(1.5,-0.8,0))
    view.saveImage(str(out/'kot-v18-wnetrze.png'),1400,1050,'White')
finally:
    for o in parts: o.Visibility=True
    for o,c in zip(highlight,colours): o.ViewObject.ShapeColor=c
    camera(App.Vector(-1,-1,0.65),App.Vector(1,-1,0))
    doc.Label='Kot v18 | skorupa dzielona | PROTOTYP PETG'
    doc.save()
    view.saveImage(str(out/'kot-v18-zlozony.png'),1400,1050,'White')
print('Interior captured; whole cat restored and saved')
