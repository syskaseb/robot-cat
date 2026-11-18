import FreeCAD as A,FreeCADGui as G,json,datetime,zipfile
from pathlib import Path
from PySide import QtCore
D=A.ActiveDocument;P=Path(D.FileName).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
names=['F2_COMMON_PI_BUS_PCA_RECEIVER','F3_E1_REMOVABLE_EDGE_KEEPER','D18C_TRUE_PITCH_OPTICAL_RECEIVER','F3_HEAD_FRONT','F3_HEAD_BACK','F3_BODY_FORE_NEG','F3_BODY_FORE_POS','F3_BODY_REAR_NEG','F3_BODY_REAR_POS','YAW_FIXED_OUTER_RACE_CAP'];mass=[]
for n in names:
 s=D.getObject(n).Shape;c=V(0,0,0)
 for q in s.Solids:c+=q.CenterOfMass*q.Volume
 mass.append({'object':n,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'PETG_g':s.Volume*.00127,'COM':list(c/s.Volume)})
wr('candidate-selected-material-not-whole-mass.json',{'density_g_cm3':1.27,'parts':mass,'sum_g':sum(r['PETG_g'] for r in mass),'meaning':'UNSELECTED candidate material subtotal including changed bearing cap; not whole robot mass/saving/payload; capacity fields/paint faces excluded','physical_PASS':False})
forms=[D.getObject(n) for n in ['F3_HEAD_FRONT','F3_HEAD_BACK','F3_BODY_FORE_NEG','F3_BODY_FORE_POS','F3_BODY_REAR_NEG','F3_BODY_REAR_POS','F3_PAINT_GOLD_m1','F3_PAINT_GOLD_1','F3_PAINT_DARK_m1','F3_PAINT_DARK_1']]
lines=[o for o in D.Objects if o.Name.startswith(('F3_DATA500_','F3_ToF','D18C_FFC200_OCCUPIED_EDGE_'))]
shots=[('candidate-whole-front.png',(-1,0,.04),False),('candidate-whole-side.png',(0,-1,.04),False),('candidate-whole-three-quarter.png',(-1.4,-1,.55),False),('candidate-whole-interior.png',(-1.2,-1,.9),True)];pins=[]
def step(i):
 if i>=len(shots):
  for o in forms:
   if o:o.ViewObject.Visibility=True
  for o in lines:o.ViewObject.Visibility=False
  D.Label='UNSELECTED_NECK_PARTITION_STEEL_AND_FFC_HOLD';G.runCommand('Std_Save')
  wr('candidate-view-pins.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'same_geometry_all_views':True,'actual_bought_parts_not_hidden':True,'snapshots':pins,'status':'UNSELECTED prototype candidate; full crosspin/occupied FFC guard failure; no STL release'})
  wr('native-idle-receipt.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':D.FileName,'document':D.Name,'objects':len(D.Objects),'modified':False,'pending':None,'owned_compute':'IDLE after normal save callback','geometry_work_finished':True,'physical_PASS':False});return
 name,di,inside=shots[i]
 for o in forms:
  if o:o.ViewObject.Visibility=not inside
 for o in lines:o.ViewObject.Visibility=inside
 v=V(*di);v.normalize();right=V(0,0,1).cross(v);right.normalize();G.activeDocument().activeView().setCameraOrientation(A.Rotation(right,v.cross(right),v,'ZXY').Q);G.activeDocument().activeView().fitAll();G.activeDocument().activeView().redraw()
 def capture():
  G.activeDocument().activeView().saveImage(str(P/name),1800,1250,'White');pins.append({'file':name,'camera':list(G.activeDocument().activeView().getCameraOrientation().Q),'inside':inside});QtCore.QTimer.singleShot(350,lambda:step(i+1))
 QtCore.QTimer.singleShot(600,capture)
A._last_neck_capture=step;step(0);print('FINAL_CANDIDATE_FREEZE_4VIEWS_SCHEDULED_NO_NEW_GEOMETRY')
