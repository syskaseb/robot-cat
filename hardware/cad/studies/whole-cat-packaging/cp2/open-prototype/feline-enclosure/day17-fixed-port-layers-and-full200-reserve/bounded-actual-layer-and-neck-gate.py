import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;rows=[];t0=time.perf_counter()
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def lo(a,b):
 a=a.BoundBox;b=b.BoundBox;return sum(max(0,getattr(a,'XYZ'[i]+'Min')-getattr(b,'XYZ'[i]+'Max'),getattr(b,'XYZ'[i]+'Min')-getattr(a,'XYZ'[i]+'Max'))**2 for i in range(3))**.5
def gate(n,a,m,b,kind):
 l=lo(a,b);r={'part':n,'neighbor':m,'bound':l,'required':1.25,'kind':kind}
 if l>=1.25:r['scopedclear']=True
 else:
  d=a.distToShape(b)[0];r.update(gap=d,valid=a.isValid() and b.isValid(),scopedclear=d>=1.25-1e-7)
  if d<1.25:r['common']=a.common(b).Volume
 rows.append(r);put('one-whole-delta-gate.json',{'rows':rows,'allreplays':False,'wholekit':False})
ns=['BUS25514_installed','N17_ALL117_BUS_PRIMARY_EXTENT_REFERENCE_NOT_MATERIAL']+[o.Name for o in D.Objects if o.Name.startswith('CB_BUS_')]
for n in ns:
 for m in ['Pi_USB_DATA_Delock_mating','Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','PBAY_F_PI','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','Battery_GEA223S30X6GT','Motor_ATO4A__1_0','Motor_ATO4A_1_0']:
  gate(n,D.getObject(n).Shape,m,D.getObject(m).Shape,'movedwholeBUS/fullsteel/sourceprimaryextent vs currentrigid/installation; sourcefieldsnotliteralplastic')
# Actual named local pinch: fullcamera departure and matching movingcarrier.
for fn,y,p in [('N17_FFC200_OCCUPIED_0_0',0,0),('N17_FFC200_OCCUPIED_m20_10',-20,10),('N17_FFC200_OCCUPIED_20_10',20,10)]:
 s=D.getObject(fn).Shape;roi=Part.makeBox(29,36,48,V(-212,-18,150))
 frame=D.getObject('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE').Shape.copy()
 if p:frame.rotate(V(-135,0,121),V(0,1,0),p);roi.rotate(V(-135,0,121),V(0,1,0),p)
 if y:frame.rotate(V(-106,0,127),V(0,0,1),y);roi.rotate(V(-106,0,127),V(0,0,1),y)
 local=s.common(roi)
 if not local.isNull():gate(fn+'camera_local',local,'posed_sensorcarrier',frame,'fullprofile edge/twist at realcarrier; regionbox cannot proveactualwallgap; correlatedpose')
# One current neck wall gate; required newpassage/guard is not existingclearance.
s=D.getObject('N17_FFC200_OCCUPIED_0_0').Shape;roi=Part.makeBox(8,120,50,V(-132,-60,165));local=s.common(roi)
for m in ['HC_BACK_UPPER','FC_F_NEG','FC_F_POS']:
 if not local.isNull():gate('neutral_FFC_at_neckplane',local,m,D.getObject(m).Shape,'actualprofile through currentownwall; intentionalfunctionalpassage notimplemented yet, noOWNwaiver')
put('one-whole-delta-gate.json',{'rows':rows,'failures':[r for r in rows if r['scopedclear'] is False],'changed_BUS_pairs':len(ns)*10,'globalmatrix_replayed':False,'sourcefull169_cursor':'FROZEN7','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t0})
# Actual changedinterface view. Keep full boughtparts; only covers hidden.
for o in D.Objects:
 if o.Name.startswith(('HC_FRONT_HOLLOW','HC_BACK_LOWER','HC_BACK_UPPER','HC_BLACK_PAINT','HC_GOLD_PAINT','FC_')):o.ViewObject.Visibility=False
 if o.Name.startswith('AFT_'):o.ViewObject.Visibility=False
D.getObject('N17_FFC200_OCCUPIED_0_0').ViewObject.Visibility=True
v=G.activeDocument().activeView();d=V(-1.1,-1,.8);d.normalize();r=V(0,0,1).cross(d);r.normalize();v.setCameraOrientation(A.Rotation(r,d.cross(r),d,'ZXY').Q);v.fitAll();v.redraw();D.save();print(json.dumps({'checks':len(rows),'fails':[r for r in rows if not r['scopedclear']],'seconds':time.perf_counter()-t0}))
