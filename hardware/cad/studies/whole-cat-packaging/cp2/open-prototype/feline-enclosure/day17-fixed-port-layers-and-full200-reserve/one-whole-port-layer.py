import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bounds(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
D.save();R=A.Rotation(V(1,0,0),-90);C=V(-17,-4.5,140.8);Cn=V(-23,-12.7,111);T=A.Placement(Cn-R.multVec(C),R)
moves=[]
for o in D.Objects:
 if o.Name=='BUS25514_installed' or o.Name.startswith('CB_BUS_'):
  old=bounds(o.Shape);vol=o.Shape.Volume;o.Placement=T.multiply(o.Placement);moves.append({'object':o.Name,'before':old,'after':bounds(o.Shape),'oldV':vol,'newV':o.Shape.Volume})
D.getObject('BUS25514_installed').Label='BUS whole42x33x24 PROJECT installation / fixedverticalcontrolface / not actualhousing';D.getObject('BUS25514_installed').ViewObject.Transparency=65
D.getObject('Pi_USB_DATA_Delock_mating').Label='Lanberg USB-A DATA full installation26x26x24 / POWERDelock60047 distinct / oldIDretained'
D.getObject('CB_REMOVABLE_BUS_E1_BRIDGE').Label='UNBUILT_OLD_BUS_E1_BRIDGE_FUNCTION_REPLACEMENT_REQUIRED';D.getObject('CB_REMOVABLE_BUS_E1_BRIDGE').ViewObject.Visibility=False
# Explicit manufacturer BOARD mapping via 4 actual source holes/topplane.
# No invalid117aggregate BOP/import or bbox registration.
S=Part.Shape();S.read('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/electronics/full-cat/pi-bus-primary-r1/Part__Feature.brep')
holes=[]
for f in S.Faces:
 try:
  c=f.Surface
  if isinstance(c,Part.Cylinder) and abs(c.Radius-1.25)<.01:holes.append([c.Center.x,c.Center.y,c.Radius])
 except Exception:pass
Tboard=A.Placement(V(-44,-11.9,127.5),R);S.Placement=Tboard.multiply(S.Placement)
g=D.addObject('App::DocumentObjectGroup','N17_WHOLE_PORT_LAYER_AND_LOOM_REFERENCE_NOT_PRINT')
o=D.addObject('PartDesign::Feature','N17_PRIMARY_BUS_BOARD_NO_EXTRA_BOM');o.Shape=S;o.ViewObject.ShapeColor=(.1,.55,.25);g.addObject(o)
# Bounds of ALL117 from sourcecatalog, preserving knowninvalid member as
# sourceoccupiedextent reference, not physicalfused case/pressurebearing.
q=Part.makeBox(42.0242,33.8163,14.6,V(-.0121,-.8042,-3.6));q.Placement=Tboard.multiply(q.Placement)
o=D.addObject('PartDesign::Feature','N17_ALL117_BUS_PRIMARY_EXTENT_REFERENCE_NOT_MATERIAL');o.Shape=q;o.ViewObject.Transparency=80;o.ViewObject.ShapeColor=(.4,.7,.45);g.addObject(o)
put('one-distinct-port-layer.json',{'moves':moves,'primaryBoard_holes_local':holes,'primaryBoard_valid':S.isValid(),'primaryBoard_frame':'T(local)=(-44,-11.9,127.5)+Rx(-90)*local; sourcePCBtopZ0 ->Y-11.9, sourcebottom-1.6 ->Y-13.5; holes2.5/39.5,2.5/30.5 map current4completeCB_BUS sets. Actualrevision/safeannulusphysicalFIT.','full117_source_extent':bounds(q),'old_FULL_installation_box_retained':bounds(D.getObject('BUS25514_installed').Shape),'fullsamePi_camera_poses':'7c8 unchanged; no verticalPiscalar experiment','separation_direction':'BUS moduleandfullmountsteel moved to oneverticalfixedcontrolface, DATA remainsrearward upperPi; PCA+E1solderedwholekitunchanged','functional_support_replacement':'oldBUS/E1bridge unbuiltrolewithdrawn only; newcommonremovablecontrolface mustretain E1 topcapture/antirotation andBUS4posts andPi fixedupperplane, beforematerial. Sourcefloor/base/MTA/power/sourceportsnotcut.','no_new_hardware_or_STL':True,'no_catalogue_reselection':True,'wholekit':False,'physicalPASS':False})
D.recompute();D.save();print(json.dumps({'BUS_install':bounds(D.getObject('BUS25514_installed').Shape),'full117':bounds(q),'source_board_holes':holes,'moved':len(moves)}))
