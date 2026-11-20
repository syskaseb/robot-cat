"""Update only the calibrated 20D copy, save native views, and export three prints."""
from pathlib import Path
from runpy import run_path
from datetime import datetime,timezone
import hashlib
import json
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
import MeshPart
from PySide import QtCore,QtWidgets

folder=Path(__file__).resolve().parent
source=folder.parent/'20C'/'whole-cat20C.FCStd'
native=folder/'whole-cat20D.FCStd'
known='92fc832c49983ce98cd8d0c7b182f126481d2aff89de36a9c76ee67842985059'
def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def write(name,data):
    dest=folder/name;tmp=dest.with_suffix('.tmp')
    before=dest.read_bytes() if dest.exists() else None
    with tmp.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    assert (dest.read_bytes() if dest.exists() else None)==before
    os.replace(tmp,dest)

assert not native.exists()
assert sha(source)==known
d=App.ActiveDocument
assert Path(d.FileName).resolve()==source.resolve() and len(d.Objects)==568 and not d.isTouched()
gate=json.loads((folder/'20D-final-gate.json').read_bytes())
support=json.loads((folder/'20D-support-fit.json').read_bytes())
assert all(not row['intersections'] for row in gate['areas'].values()), 'unresolved source gate'
assert not gate['affected_head_motion']
assert all(not row for row in support['positive_volume_overlap'].values()), 'unresolved mount interference'
assert min(support['bearing'].values())>0
assert max(support['attachment_regions'].values())<.05

g=run_path(str(folder/'geometry.py')); l=run_path(str(folder/'layout.py'))
parts=g['forms'](); cube=g['cube']; V=App.Vector
w=l['wire_budgets']()
d.saveAs(str(native))
d.Label='whole-cat20D'
Gui.runCommand('Std_Save',0)
d.openTransaction('20D fixed axial inlet')

def obj(name,shape,label,color,visible=True):
    o=d.getObject(name)
    if o is None:
        o=d.addObject('Part::Feature',name)
    o.Shape=shape;o.Label=label
    o.ViewObject.ShapeColor=color
    o.ViewObject.LineColor=(.15,.17,.19)
    o.ViewObject.Visibility=visible
    return o

def pieces(name,paths,color,label):
    lines=[Part.makePolygon([V(*q) for q in vs]) for vs in paths]
    o=obj(name,Part.makeCompound(lines),label,color,False)
    o.ViewObject.LineColor=color;o.ViewObject.LineWidth=4.0
    return o

try:
    d.removeObject('C20_F0_OpenMount')
    d.removeObject('C20_Post_OpenSlottedMount')
    labels={
      'D20_XT60_Axial_Adapter':'20D mały adapter XT60 | stała oś X',
      'D20_F0_Open_Adapter':'20D otwarty uchwyt FHAC | oddzielny adapter',
      'D20_POST_Aft_Slotted':'20D stopniowany uchwyt POST | regulacja Y',
      'D20_POST_Clamp_M3x12':'POST zacisk DIN912 M3 x 12',
      'D20_POST_Clamp_Nut':'POST nakrętka M3'
    }
    for n,s in parts.items():
        obj(n,s,labels[n],(.52,.61,.75) if 'Clamp' not in n else (.65,.66,.7))
    gold=(.95,.66,.19)
    obj('XT60H_mated_with_boots',cube(l['BOX_M']),'XT60H-M i osłona | strona stała, projekt',gold)
    p=obj('C20_Pack_XT60_F',cube(l['BOX_F']),'Fabryczna F z odgiętką | pozycja połączona, projekt',gold)
    stroke=list(l['BOX_F']);stroke[0]+=14;stroke[3]+=14
    ghost=obj('C20_Pack_XT60_Stroke',cube(stroke),'Fabryczna F z odgiętką | +14 mm, projekt',(1.,.73,.23),False)
    ghost.ViewObject.Transparency=68
    obj('F0_FHAC0002_30A',cube(l['F0']),'FHAC0002ZXJ cały uchwyt | wysokość 21,5 mm przyjęta',(.84,.38,.16))
    obj('PBAY_POST_F0',cube(l['POST']),'POST_F0 WAGO 221-412 | regulacja portu Y -34...-20',(.34,.61,.42))
    small=obj('D20_Battery_Auxiliary_Plug_Envelope',cube(l['SMALL_PLUG']),
          'Dodatkowa fabryczna wtyczka | kieszeń projektowa 24 x 12 x 14 mm',(.68,.48,.76))
    small.ViewObject.Transparency=48
    cables=[
      pieces('C20_BAT_Leads_Indicative',[w['pack'][pole]['states']['parked']['stations'] for pole in ('plus','minus')],
             (.88,.37,.12),'Dwie fabryczne żyły od krótkiego boku | ułożenie projektowe'),
      pieces('D20_BAT_Leads_At14',[w['pack'][pole]['states']['withdraw']['stations'] for pole in ('plus','minus')],
             (.94,.68,.24),'Dwie żyły po skoku +14 mm | ułożenie projektowe'),
      pieces('C20_Inlet_W075',[w['W075']['points']],(.73,.22,.1),'W075 oryginalna niechroniona żyła FHAC do robotowej XT60'),
      pieces('C20_F0_Outlet_Ideal',[w['W076_complete_FHAC_out']['shape_points']],(.82,.49,.16),'W076 cała fabryczna żyła wyjściowa do POST_F0'),
      pieces('C20_Protected_and_Return',[w['W076_custom']['allocated_waypoints']],(.21,.53,.68),'HELU chroniony od POST_F0 do S0 | obszar ułożenia'),
      pieces('D20_W001_Regional',[w['W001']['allocated_waypoints']],(.27,.23,.32),'W001 LAPP ciągłe, stacjonarne | obszar ułożenia')
    ]
    small.ViewObject.Visibility=False
    d.recompute()
    d.commitTransaction()
except Exception:
    d.abortTransaction()
    raise
Gui.runCommand('Std_Save',0)
Gui.updateGui()

view=Gui.activeDocument().activeView()
def camera(v):
    z=V(*v);z.normalize()
    x=V(0,0,1).cross(z);x.normalize()
    view.setCameraOrientation(App.Rotation(x,z.cross(x),z,'ZXY').Q)
    view.fitAll();view.redraw();Gui.updateGui()

def render(name,dirn):
    camera(dirn)
    path=folder/name
    view.saveImage(str(path),1720,1160,'White')
    assert path.is_file() and path.stat().st_size>10000

closed=(.60,.99,.50)
render('20D-closed.png',closed)
opened=('E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','Speaker','E19_ReSpeakerSource',
        'E19_BUS_PCB','E19_BUS_population','E19_BatteryDoor','C20_BatteryUpperBridge',
        'C20_Bridge_M3x12_1','C20_Bridge_M3x12_2','C20_Bridge_M3_Nut_1','C20_Bridge_M3_Nut_2')
before={n:d.getObject(n).ViewObject.Visibility for n in opened}
try:
    for n in opened:
        d.getObject(n).ViewObject.Visibility=False
    for item in cables+[ghost,small]:
        item.ViewObject.Visibility=True
    render('20D-open-service.png',(.34,.91,1.24))
    cf=['E19_RearBase','H19_FrontFrame','E19_WagoRearPos','E19_WagoForePos','Motor_ATO4A_1_2']
    old={n:d.getObject(n).ViewObject.Transparency for n in cf}
    try:
        for n in cf:
            d.getObject(n).ViewObject.Transparency=76
        render('20D-short-end-cutaway.png',(.38,1.06,.56))
    finally:
        for n,v in old.items():
            d.getObject(n).ViewObject.Transparency=v
finally:
    for n,v in before.items():
        d.getObject(n).ViewObject.Visibility=v
    for item in cables+[ghost,small]:
        item.ViewObject.Visibility=False
    camera(closed)
d.recompute()
Gui.runCommand('Std_Save',0)
Gui.updateGui()

exports=folder/'parts'
exports.mkdir()
prints={}
for n,outward,words in [
    ('D20_XT60_Axial_Adapter',(0,0,1),'Płaszczyzną górnej stopy na stół'),
    ('D20_F0_Open_Adapter',(0,-1,0),'Długą krawędzią -Y na stół'),
    ('D20_POST_Aft_Slotted',(0,0,1),'Górą szyny na stół'),
]:
    s=parts[n]
    s.exportStep(str(exports/(n+'.step')))
    norm=s.copy()
    norm.rotate(V(0,0,0),App.Rotation(V(*outward),V(0,0,-1)).Axis,
                App.Rotation(V(*outward),V(0,0,-1)).Angle*180/3.141592653589793)
    b=norm.BoundBox
    norm.translate(V(-b.XMin,-b.YMin,-b.ZMin))
    mesh=MeshPart.meshFromShape(Shape=norm,LinearDeflection=.035,AngularDeflection=.12,Relative=False)
    mesh.write(str(exports/(n+'.stl')))
    dims=g['bounds'](norm)[3:]
    brim=[round(dims[0]+16,2),round(dims[1]+16,2),dims[2]]
    assert max(brim)<256
    prints[n]={'bed_axes_mm':dims,'bed_axes_with_8mm_brim_mm':brim,'orientation_pl':words,
               'supports':'lokalne pod podcięciami i wolnymi krawędziami, zweryfikować w próbie produkcyjnej',
               'STL_sha256':sha(exports/(n+'.stl')),'STEP_sha256':sha(exports/(n+'.step'))}
write('20D-print-index.json',prints)

def receive():
    subwindows=Gui.getMainWindow().findChildren(QtWidgets.QMdiSubWindow)
    active=[q for q in subwindows if q.isVisible() and d.Label in q.windowTitle()]
    assert len(active)==1
    modified=bool(active[0].isWindowModified())
    result={'schema':'native live readback','frozen_source_sha256':sha(source),'path':native.name,
            'sha256':sha(native),'document_name':d.Name,'document_label':d.Label,'object_count':len(d.Objects),
            'modified':modified,'touched':bool(d.isTouched()),'gui_pid':os.getpid(),
            'saved_utc':datetime.now(timezone.utc).isoformat(),'pending_operation':None,'state':'IDLE'}
    write('20D-native-readback.json',result)
    print('20D NATIVE RECEIPT',result,flush=True)
QtCore.QTimer.singleShot(650,receive)
