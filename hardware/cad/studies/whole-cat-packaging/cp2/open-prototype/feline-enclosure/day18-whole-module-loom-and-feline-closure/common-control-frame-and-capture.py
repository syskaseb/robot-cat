import FreeCAD as A, FreeCADGui as G, Part, json, pathlib
from PySide import QtCore
D=A.ActiveDocument; P=pathlib.Path(__file__).parent; V=A.Vector
def box(x,y,z,dx,dy,dz): return Part.makeBox(dx,dy,dz,V(x,y,z))
old=D.getObject('D18C_COMMON_PI_OPEN_CARRIER'); base=old.Shape.copy()
members=[box(-42,27,90,11,5.5,5),box(-37,29.5,88,6,3,46),box(-37,29.5,95,89,3,8.5),box(7,19,101,44,35,3)]
# Four BUS primary pads use the existing full steel stack, with 3 mm printed stand-offs.
for x in [10.5,47.5]:
 for y in [22.5,50.5]: members.append(Part.makeCylinder(4,3,V(x,y,104)))
# Open window carries the PCA four mounting pads without pressing its underside components.
members += [box(-24,25.55,130,133,3,3),box(-24,25.55,160,133,3,3),box(-24,25.55,130,3,3,33),box(106,25.55,130,3,3,33),box(-37,25.55,130,16,6.95,4)]
for x in [-14.825,41.055]:
 for z in [135.775,154.825]:
  members.append(Part.makeCylinder(4,3,V(x,25.55,z),V(0,1,0)))
  members.append(Part.makeCylinder(3,3,V(x,22.55,z),V(0,1,0)))
  zz=130 if z<145 else 157
  members.append(box(x-3,25.55,min(z,zz),6,3,abs(z-zz)+3))
s=base.multiFuse(members).removeSplitter(); intended=s.copy()
for x in [10.5,47.5]:
 for y in [22.5,50.5]: s=s.cut(Part.makeCylinder(1.1,9,V(x,y,100)))
for x in [-14.825,41.055]:
 for z in [135.775,154.825]: s=s.cut(Part.makeCylinder(1.1,8,V(x,21.55,z),V(0,1,0)))
s=s.removeSplitter();o=D.addObject('PartDesign::Feature','F2_COMMON_PI_BUS_PCA_RECEIVER');o.Shape=s;o.ViewObject.ShapeColor=(.18,.24,.28);old.ViewObject.Visibility=False
checks=[]
for n in ['BNO085','Speaker_VISATON_K50FL','MAX98357A_amp','BUS_DRIVER_INSTALLED_SCOPE','PCA9685','E1_MODULE','F0_FHAC0002_30A']:
 q=D.getObject(n)
 if q is None or not hasattr(q,'Shape') or q.Shape.isNull():continue
 try:checks.append(dict(name=n,gap=s.distToShape(q.Shape)[0],common=s.common(q.Shape).Volume))
 except Exception as e:checks.append(dict(name=n,status='UNQUALIFIED',reason=str(e)))
report=dict(valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,PETG_g=s.Volume*.00127,old_relief_carrier_volume=base.Volume,delta_PETG_g=(s.Volume-base.Volume)*.00127,member_count=len(members),old_carrier_material_missing_mm3=base.cut(s).Volume,nominal_new_member_missing_excluding_explicit_holes_mm3=intended.cut(s).Volume,checks=checks,scope='ACTUAL common Pi/BUS/PCA receiver; full existing source mount steel retained. Remaining E1/MAIN/AUX/audio/terminal and shell joints OPEN. No mesh release.',physical_PASS=False)
(P/'common-control-frame-result.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
forms=[q for q in D.Objects if q.Name.startswith(('F2_BODY_','F2_HEAD_','F2_GOLD_','F2_DARK_'))]
lines=[q for q in D.Objects if q.Name.startswith(('D18C_FFC200_OCCUPIED_EDGE_','D18C_DATA500_CONNECTED_STATIC_BAY'))]
shots=[('whole-opaque-front.png',(-1,0,.04),False),('whole-opaque-side.png',(0,-1,.04),False),('whole-opaque-front-three-quarter.png',(-1.4,-1,.55),False),('whole-interior.png',(-1.2,-1,.9),True)]
pins=[]
def step(i):
 if i>=len(shots):
  D.Label='DAY18_WHOLE_MODULE_LOOM_HOLLOW_CLOSURE_OPEN';G.runCommand('Std_Save');(P/'snapshot-camera-pins.json').write_bytes((json.dumps(pins,indent=2)+'\n').encode());return
 name,di,inside=shots[i]
 for q in forms:q.ViewObject.Visibility=not inside
 for q in lines:q.ViewObject.Visibility=inside
 v=V(*di);v.normalize();right=V(0,0,1).cross(v);right.normalize();G.activeDocument().activeView().setCameraOrientation(A.Rotation(right,v.cross(right),v,'ZXY').Q);G.activeDocument().activeView().fitAll();G.activeDocument().activeView().redraw()
 def capture():
  G.activeDocument().activeView().saveImage(str(P/name),1800,1250,'White');pins.append(dict(file=name,camera=list(G.activeDocument().activeView().getCameraOrientation().Q),interior=inside,status='ACTUAL current hollow material; unmounted shell joins and visible protrusions not concealed'));QtCore.QTimer.singleShot(500,lambda:step(i+1))
 QtCore.QTimer.singleShot(700,capture)
A._f2_capture_step=step
D.recompute();D.save();step(0)
print(json.dumps(report))
