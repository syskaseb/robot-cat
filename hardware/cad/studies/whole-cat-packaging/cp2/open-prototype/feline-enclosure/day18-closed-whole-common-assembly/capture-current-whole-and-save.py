import FreeCAD as A,FreeCADGui as G,json,datetime
from pathlib import Path
from PySide import QtCore
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
forms=[D.getObject(n) for n in ['F3_HEAD_FRONT','F3_HEAD_BACK','F3_BODY_FORE_NEG','F3_BODY_FORE_POS','F3_BODY_REAR_NEG','F3_BODY_REAR_POS','F3_PAINT_GOLD_m1','F3_PAINT_GOLD_1','F3_PAINT_DARK_m1','F3_PAINT_DARK_1']]
lines=[o for o in D.Objects if o.Name.startswith(('F3_DATA500_','F3_ToF','D18C_FFC200_OCCUPIED_EDGE_'))]
shots=[('CURRENT-whole-opaque-front.png',(-1,0,.04),False),('CURRENT-whole-opaque-side.png',(0,-1,.04),False),('CURRENT-whole-opaque-three-quarter.png',(-1.4,-1,.55),False),('CURRENT-whole-interior.png',(-1.2,-1,.9),True)];pins=[]
def step(i):
 if i>=len(shots):
  for o in forms:
   if o:o.ViewObject.Visibility=True
  for o in lines:o.ViewObject.Visibility=False
  D.Label='DAY18_CURRENT_COMMON_MOUNTS_AND_REAL_SKIN_JOINTS';G.runCommand('Std_Save')
  (P/'current-whole-view-pins.json').write_bytes((json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'snapshots':pins,'native':D.FileName,'same_geometry':True,'actual_bought_parts_not_hidden':True,'geometry_status':'WORKING actual material, selected cosmetic form not appearance accepted, neck/tail and body seams still incomplete','physical_PASS':False},indent=2)+'\n').encode());return
 name,di,inside=shots[i]
 for o in forms:
  if o:o.ViewObject.Visibility=not inside
 for o in lines:o.ViewObject.Visibility=inside
 v=V(*di);v.normalize();right=V(0,0,1).cross(v);right.normalize();G.activeDocument().activeView().setCameraOrientation(A.Rotation(right,v.cross(right),v,'ZXY').Q);G.activeDocument().activeView().fitAll();G.activeDocument().activeView().redraw()
 def capture():
  G.activeDocument().activeView().saveImage(str(P/name),1800,1250,'White');pins.append({'file':name,'camera':list(G.activeDocument().activeView().getCameraOrientation().Q),'inside':inside});QtCore.QTimer.singleShot(350,lambda:step(i+1))
 QtCore.QTimer.singleShot(600,capture)
A._f3_current_capture=step;step(0);print('CURRENT_SAME_GEOMETRY_4VIEWS_SCHEDULED')
