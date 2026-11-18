import FreeCAD as A,FreeCADGui as G,json,pathlib
from PySide import QtCore
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
forms=[o for o in D.Objects if o.Name in ['D18B_BODY_FORM','D18C_HEAD_FACE_CLOCK_BOUND_FORM','D18C_LOCAL_NECK_RECEIVING_FORM_NOT_PRINT'] or o.Name.startswith(('D18C_GOLD_RIM_','D18C_DARK_EYE_'))]
lines=[o for o in D.Objects if o.Name.startswith(('D18C_FFC200_OCCUPIED_EDGE_','D18C_DATA500_CONNECTED_STATIC_BAY'))]
shots=[('whole-opaque-front.png',(-1,0,.04),False),('whole-opaque-side.png',(0,-1,.04),False),('whole-opaque-front-three-quarter.png',(-1.4,-1,.55),False),('whole-interior.png',(-1.2,-1,.9),True)]
pins=[]
def orient(direction):
 v=V(*direction);v.normalize();right=V(0,0,1).cross(v);right.normalize();G.activeDocument().activeView().setCameraOrientation(A.Rotation(right,v.cross(right),v,'ZXY').Q);G.activeDocument().activeView().fitAll();G.activeDocument().activeView().redraw()
def step(i):
 if i>=len(shots):
  D.Label='DAY18_CONNECTED_STORAGE_TRUE_PITCH_CONDITIONAL';G.activeDocument().activeView().redraw();G.runCommand('Std_Save');(P/'snapshot-camera-pins.json').write_bytes((json.dumps(pins,indent=2)+'\n').encode());return
 name,direction,inside=shots[i]
 for o in forms:o.ViewObject.Visibility=not inside
 for o in lines:o.ViewObject.Visibility=inside
 orient(direction)
 def capture():
  G.activeDocument().activeView().saveImage(str(P/name),1800,1250,'White');pins.append(dict(file=name,camera_quaternion=list(G.activeDocument().activeView().getCameraOrientation().Q),direction=direction,geometry_status='same current CAD; coarse outer forms PROPOSED_NOT_PRINT_NOT_MASS; all bought parts preserved, protrusions not hidden',interior=inside));QtCore.QTimer.singleShot(500,lambda:step(i+1))
 QtCore.QTimer.singleShot(700,capture)
A._d18c_capture_step=step
step(0)
print('FOUR_ACTUAL_CAD_VIEWS_SCHEDULED; separate redraw/capture; final normal GUI save')
