import FreeCAD as A,FreeCADGui as G,pathlib,json,datetime
from PySide import QtCore
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
forms=[o for o in D.Objects if o.Name.startswith(('F3_BODY_','F3_HEAD_','F3_PAINT_'))]
lines=[o for o in D.Objects if o.Name.startswith(('F3_DATA500_','D18C_FFC200_OCCUPIED_EDGE_'))]
shots=[('WIP-whole-opaque-front.png',(-1,0,.04),False),('WIP-whole-opaque-side.png',(0,-1,.04),False),('WIP-whole-opaque-three-quarter.png',(-1.4,-1,.55),False),('WIP-whole-interior.png',(-1.2,-1,.9),True)]
pins=[]
def step(i):
 if i>=len(shots):
  D.Label='DAY18_WORKING_CLOSED_WHOLE_ASSEMBLY';G.runCommand('Std_Save');(P/'early-whole-view-checkpoint.json').write_bytes((json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),snapshots=pins,scope='WORKING WHOLE CHECKPOINT before further holders; no commit/final/whole acceptance',DATA_R=40.86332592634959,DATA_total=500,actual_bought_parts_not_hidden=True,physical_PASS=False),indent=2)+'\n').encode());return
 name,di,inside=shots[i]
 for o in forms:o.ViewObject.Visibility=not inside
 for o in lines:o.ViewObject.Visibility=inside
 v=V(*di);v.normalize();right=V(0,0,1).cross(v);right.normalize();G.activeDocument().activeView().setCameraOrientation(A.Rotation(right,v.cross(right),v,'ZXY').Q);G.activeDocument().activeView().fitAll();G.activeDocument().activeView().redraw()
 def capture():
  G.activeDocument().activeView().saveImage(str(P/name),1800,1250,'White');pins.append(dict(file=name,camera=list(G.activeDocument().activeView().getCameraOrientation().Q),inside=inside));QtCore.QTimer.singleShot(450,lambda:step(i+1))
 QtCore.QTimer.singleShot(650,capture)
A._f3_whole_capture=step;step(0);print('EARLY FOUR WORKING WHOLE VIEWS SCHEDULED; continue same task after capture')
