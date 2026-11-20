"""Refresh the protected leads and save the closed front and side views."""
from datetime import datetime,timezone
from pathlib import Path
from runpy import run_path
import hashlib,json,os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore,QtWidgets

folder=Path(__file__).resolve().parent
native=folder/'whole-cat20D.FCStd'
d=App.ActiveDocument
assert Path(d.FileName).resolve()==native.resolve() and d.Label=='whole-cat20D' and len(d.Objects)==574
assert not d.isTouched()
g=run_path(str(folder/'layout.py')); w=g['wire_budgets']()
def read(name):
    return json.loads((folder/name).read_bytes())

def write(name,value):
    p=folder/name;t=p.with_suffix('.tmp')
    prior=p.read_bytes()
    with t.open('x',encoding='utf-8',newline='\n') as out:
        json.dump(value,out,indent=2,ensure_ascii=False);out.write('\n')
    assert p.read_bytes()==prior
    os.replace(t,p)

local=read('20D-local-wires.json')
assert not local['W076_factory']['contact_needing_local_disposition']
assert set(local['W076_custom']['contact_needing_local_disposition'])=={'S0_ring_IN_0_0'}
assert set(local['W001']['contact_needing_local_disposition'])=={'WAGO615_power_0_0'}
triangle=App.Vector
point=lambda row:triangle(*row)
for n,coords in (('C20_Protected_and_Return',w['W076_custom']['allocated_waypoints']),
                 ('C20_F0_Outlet_Ideal',w['W076_complete_FHAC_out']['shape_points'])):
    o=d.getObject(n)
    o.Shape=Part.makeCompound([Part.makePolygon([point(p) for p in coords])])
d.recompute()
Gui.runCommand('Std_Save',0);Gui.updateGui()

view=Gui.activeDocument().activeView()
def camera(dirn):
    z=point(dirn);z.normalize()
    x=triangle(0,0,1).cross(z);x.normalize()
    view.setCameraOrientation(App.Rotation(x,z.cross(x),z,'ZXY').Q)
    view.fitAll();view.redraw();Gui.updateGui()

def render(name,dirn):
    camera(dirn)
    path=folder/name
    tmp=path.with_suffix('.tmp.png')
    prior=path.read_bytes() if path.exists() else None
    view.saveImage(str(tmp),1720,1160,'White')
    assert tmp.stat().st_size>10000
    assert (path.read_bytes() if path.exists() else None)==prior
    os.replace(tmp,path)

render('20D-closed-front.png',(-.98,.9,.44))
render('20D-closed-side.png',(0,1,.016))
opened=('E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','Speaker','E19_ReSpeakerSource',
        'E19_BUS_PCB','E19_BUS_population','E19_BatteryDoor','C20_BatteryUpperBridge',
        'C20_Bridge_M3x12_1','C20_Bridge_M3x12_2','C20_Bridge_M3_Nut_1','C20_Bridge_M3_Nut_2')
references=('C20_BAT_Leads_Indicative','D20_BAT_Leads_At14','C20_Inlet_W075','C20_F0_Outlet_Ideal',
            'C20_Protected_and_Return','D20_W001_Regional','C20_Pack_XT60_Stroke','D20_Battery_Auxiliary_Plug_Envelope')
transparent=('E19_RearBase','H19_FrontFrame','E19_WagoRearPos','E19_WagoForePos','Motor_ATO4A_1_2')
before={n:d.getObject(n).ViewObject.Visibility for n in [*opened,*references]}
alpha={n:d.getObject(n).ViewObject.Transparency for n in transparent}
try:
    for n in opened:
        d.getObject(n).ViewObject.Visibility=False
    for n in references:
        d.getObject(n).ViewObject.Visibility=True
    render('20D-open-service.png',(.34,.91,1.24))
    for n in transparent:
        d.getObject(n).ViewObject.Transparency=76
    render('20D-short-end-cutaway.png',(.38,1.06,.56))
finally:
    for n,v in before.items():
        d.getObject(n).ViewObject.Visibility=v
    for n,v in alpha.items():
        d.getObject(n).ViewObject.Transparency=v
    camera((-.98,.9,.44))
d.recompute()
Gui.runCommand('Std_Save',0);Gui.updateGui()
gate=read('20D-final-gate.json')
gate['wire_budgets']=w
write('20D-final-gate.json',gate)

def readback():
    windows=Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
    active=[q for q in windows if q.isVisible() and d.Label in q.windowTitle()]
    assert len(active)==1
    old=read('20D-native-readback.json')
    old.update(sha256=hashlib.sha256(native.read_bytes()).hexdigest(),document_label=d.Label,
               document_name=d.Name,object_count=len(d.Objects),modified=bool(active[0].isWindowModified()),
               touched=bool(d.isTouched()),gui_pid=os.getpid(),
               saved_utc=datetime.now(timezone.utc).isoformat(),pending_operation=None,state='IDLE')
    write('20D-native-readback.json',old)
    print('20D FINAL NATIVE',old,flush=True)
QtCore.QTimer.singleShot(650,readback)
