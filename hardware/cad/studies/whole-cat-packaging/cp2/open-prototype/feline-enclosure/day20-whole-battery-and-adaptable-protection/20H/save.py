"""Save the 20H conditional parent and assemble one CAD view of the bench coupon."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore, QtWidgets

here=Path(__file__).resolve().parent
source=here.parent/'20G/whole-cat20G.FCStd'
dest=here/'whole-cat20H.FCStd'
proof=json.loads((here/'FIT_S0-gate.json').read_bytes())
assert proof['status']=='CONDITIONAL_REAR_BASE__FIT_S0_FIRST'
def sha(p):return sha256(p.read_bytes()).hexdigest()
assert sha(source)==proof['source_20G_native_sha256']
d=App.ActiveDocument
assert Path(d.FileName).resolve()==source.resolve() and len(d.Objects)==576 and not d.isTouched()
assert not dest.exists()
V=App.Vector
def solid(path,volume):
    shape=Part.Shape()
    shape.read(str(path))
    assert shape.isValid() and len(shape.Solids)==1 and abs(shape.Volume-volume)<.01,path
    return shape

rear=solid(here/'rear_base.brep',proof['rear_base_volume_mm3'])
coupon=solid(here/'coupon.brep',proof['coupon_volume_mm3'])
d.saveAs(str(dest))
d.Label='whole-cat20H'

def status(o,key,value):
    if key not in o.PropertiesList:
        o.addProperty('App::PropertyString',key,'20H')
    setattr(o,key,value)

d.openTransaction('20H source bores and bearing faces')
try:
    o=d.getObject('E19_RearBase')
    o.Shape=rear
    o.Label='20H RearBase | warunkowa po FIT_S0'
    status(o,'FitDisposition','CONDITIONAL. Print only after physical FIT_S0 verifies the complete switch, key and hardware.')
    status(d.getObject('S0_key'),'GeometryClass','Approximate tool and operation reserve R15 x 63.5. Actual key geometry and motion must be verified at FIT_S0.')
    co=d.addObject('Part::Feature','FIT_S0_coupon')
    co.Shape=coupon
    co.Label='FIT_S0 | kupon 56 × 57 × 3 mm, do próby bez zasilania'
    co.ViewObject.ShapeColor=(.76,.76,.79)
    status(co,'FitDisposition','One bench fitting coupon. Diagnostic only. Separate from the full rear-base print.')
    co.ViewObject.Visibility=False
    d.recompute()
    d.commitTransaction()
except Exception:
    d.abortTransaction()
    raise

view=Gui.activeDocument().activeView()
def camera(direction):
    z=V(*direction)
    z.normalize()
    x=V(0,0,1).cross(z)
    x.normalize()
    view.setCameraOrientation(App.Rotation(x,z.cross(x),z,'ZXY').Q)
    view.fitAll()
    view.redraw()
    Gui.updateGui()

actors={'FIT_S0_coupon','G20_S0_Fixing_HOLD_Reference','S0_body','S0_neck','S0_key',
        'S0_ring_IN_0_0','S0_ring_OUT_0_0','S0_nut_IN_0_0','S0_nut_OUT_0_0',
        'S0_stud_IN_0_0','S0_stud_OUT_0_0','S0_washer_IN_0_0','S0_washer_OUT_0_0'}
flags={o.Name:o.ViewObject.Visibility for o in d.Objects}
actors_obj={n:d.getObject(n).ViewObject for n in actors}
alphas={n:actors_obj[n].Transparency for n in ('S0_key','S0_body')}
try:
    for o in d.Objects:
        if flags[o.Name]!=(o.Name in actors):
            o.ViewObject.Visibility=(o.Name in actors)
    actors_obj['S0_key'].Transparency=89
    actors_obj['S0_body'].Transparency=82
    camera((-1.,-1.1,.7))
    img=here/'FIT_S0-trial-CAD.png'
    view.saveImage(str(img),1460,1100,'White')
    assert img.stat().st_size>10000
finally:
    for n in ('S0_key','S0_body'):
        actors_obj[n].Transparency=alphas[n]
    for o in d.Objects:
        if o.ViewObject.Visibility!=flags[o.Name]:
            o.ViewObject.Visibility=flags[o.Name]
    camera((-.98,.9,.44))
Gui.runCommand('Std_Save',0)
Gui.updateGui()

def receipt():
    windows=[w for w in Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
             if w.isVisible() and d.Label in w.windowTitle()]
    assert len(windows)==1 and len(App.listDocuments())==1 and len(d.Objects)==577
    assert not windows[0].isWindowModified() and not d.isTouched()
    assert sha(source)==proof['source_20G_native_sha256']
    out={'state':'IDLE','gui_pid':os.getpid(),'document_label':d.Label,'document_name':d.Name,
         'object_count':len(d.Objects),'path':dest.name,'sha256':sha(dest),
         'source_sha256':sha(source),'modified':False,'touched':False,'pending_operation':None,
         'saved_utc':datetime.now(timezone.utc).isoformat(),
         'physicalPASS':False,'rear_base_release':'CONDITIONAL_AFTER_FIT_S0'}
    path=here/'20H-native-readback.json'
    tmp=path.with_suffix('.tmp')
    with tmp.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
        f.write('\n')
    os.replace(tmp,path)
    print('20H NATIVE',out,flush=True)

QtCore.QTimer.singleShot(650,receipt)
