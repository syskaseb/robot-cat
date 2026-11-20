"""Save a 20G reference document for the paired wire layout and mounting hold."""
from pathlib import Path
from runpy import run_path
from datetime import datetime,timezone
import hashlib
import json
import os
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore,QtWidgets

here=Path(__file__).resolve().parent
src=here.parent/'20D/whole-cat20D.FCStd'
dest=here/'whole-cat20G.FCStd'
guide=here/'20G-assembly-gate.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads(guide.read_bytes())
assert proof['status']=='PAIRED_ELECTRICAL_LAYOUT_AND_OPEN_INSERTION_SUPPORTED_FASTENING_HOLD'
assert sha(src)==proof['source_pins']['20D_native']['sha256']
d=App.ActiveDocument
assert Path(d.FileName).resolve()==src.resolve() and not d.isTouched() and len(d.Objects)==574
assert not dest.exists()
g=run_path(str(here/'candidate.py'))
f=run_path(str(here.parent/'20F/clocked.py'))
steel=run_path(str(here/'hardware.py'))['load']()
V=App.Vector

# Write a clean working copy first. All following edits affect the new file.
d.saveAs(str(dest))
d.Label='whole-cat20G'
Gui.runCommand('Std_Save',0)
d.openTransaction('20G paired S0 terminals and protected cable reference')

def reference(name,shape,label,color):
    o=d.getObject(name) or d.addObject('Part::Feature',name)
    o.Shape=shape
    o.Label=label
    o.ViewObject.ShapeColor=color
    o.ViewObject.LineColor=color
    o.ViewObject.LineWidth=3.5
    o.ViewObject.Visibility=False
    return o

def property(o,name,value):
    if name not in o.PropertiesList:o.addProperty('App::PropertyString',name,'20G')
    setattr(o,name,value)

try:
    rings={k:d.getObject(k).Shape for k in (g['ring_in'],g['ring_out'])}
    for key,angle,pin in ((g['ring_in'],g['in_clock'],g['pin_in']),(g['ring_out'],g['out_clock'],g['pin_out'])):
        o=d.getObject(key)
        o.Shape=g['turned'](rings[key],pin,angle)
        o.Label=f'S0 {key.split("_")[2]} | pełne oczko obrócone na istniejącym trzpieniu'
        property(o,'ReferenceState','20G paired protected wire layout. S0 mechanical retention remains HOLD.')
    old=json.loads((here.parent/'20D/20D-final-gate.json').read_bytes())['wire_budgets']['W076_custom']
    p=[V(*q) for q in old['allocated_waypoints']]
    j=next(i for i in range(len(p)-1) if p[i].x<4<p[i+1].x)
    prefix=Part.makePolygon([*p[:j+1],f['gateway']])
    w076=reference('C20_Protected_and_Return',
               Part.makeCompound([prefix,*f['edges'].values()]),
               'W076/custom | POST_F0.2 do S0.IN',(.16,.49,.65))
    w066=reference('G20_W066_Out_To_PSYS',
               Part.makeCompound(list(g['out_edges'].values())),
               'W066 | S0.OUT do P_SYS.1',(.83,.36,.10))
    property(w076,'Purpose','Reference only. S0 fastening, insulation and actual wire length require dry-fit.')
    property(w066,'Purpose','Reference only. 210.315 mm regional route with 25.2 mm inner bend. S0 fastening HOLD.')
    fast=reference('G20_S0_Fixing_HOLD_Reference',Part.makeCompound(list(steel.values())),
                   'S0 HOLD | 2 M6×20, 4 podkładki i 2 AF10 | zamocowanie do przymiarki',(.63,.65,.68))
    property(fast,'PrototypeDecision','Occupied key radius is too large for the upper/lower external steel in the current nominal model. No replacement print is released.')
    d.recompute()
    d.commitTransaction()
except Exception:
    d.abortTransaction()
    raise

Gui.runCommand('Std_Save',0)
Gui.updateGui()
view=Gui.activeDocument().activeView()
def camera(direction):
    z=V(*direction);z.normalize()
    x=V(0,0,1).cross(z);x.normalize()
    view.setCameraOrientation(App.Rotation(x,z.cross(x),z,'ZXY').Q)
    view.fitAll();view.redraw();Gui.updateGui()

names=('E19_RearLid','F19_RearCap','E19_ForeLid','F19_ForeCap','E19_ReSpeakerSource','Speaker',
       'G20_W066_Out_To_PSYS','C20_Protected_and_Return')
flags={name:d.getObject(name).ViewObject.Visibility for name in names}
alpha_names=('E19_RearBase','S0_body','E19_WagoRearPos','E1_populated_prototype_board')
alpha={n:d.getObject(n).ViewObject.Transparency for n in alpha_names}
try:
    for n in names[:6]:d.getObject(n).ViewObject.Visibility=False
    for n in names[6:]:d.getObject(n).ViewObject.Visibility=True
    for n in alpha_names:d.getObject(n).ViewObject.Transparency=76
    camera((.8,.94,1.08))
    target=here/'20G-open-reference.png'
    view.saveImage(str(target),1660,1120,'White')
    assert target.stat().st_size>10000
finally:
    for n,v in flags.items():d.getObject(n).ViewObject.Visibility=v
    for n,v in alpha.items():d.getObject(n).ViewObject.Transparency=v
    camera((-.98,.9,.44))
Gui.runCommand('Std_Save',0)
Gui.updateGui()

def receipt():
    vs=[q for q in Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
        if q.isVisible() and d.Label in q.windowTitle()]
    assert len(vs)==1 and len(App.listDocuments())==1 and len(d.Objects)==576
    modified=bool(vs[0].isWindowModified())
    assert not modified and not d.isTouched()
    data={'document_label':d.Label,'document_name':d.Name,'path':dest.name,'sha256':sha(dest),
          'source_20D_sha256':sha(src),'object_count':len(d.Objects),'modified':modified,'touched':False,
          'pending_operation':None,'state':'IDLE','gui_pid':os.getpid(),
          'scope':'Paired S0 wire fit-reference. Mounting HOLD. No replacement part printed or exported.',
          'saved_utc':datetime.now(timezone.utc).isoformat()}
    out=here/'20G-native-readback.json';tmp=out.with_suffix('.tmp')
    with tmp.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n')
    os.replace(tmp,out)
    print('20G SAVED',data,flush=True)
QtCore.QTimer.singleShot(650,receipt)
