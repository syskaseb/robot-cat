import FreeCAD as A,Part,json,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def lo(s,q):
 a=s.BoundBox;b=q.BoundBox;return sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ')**.5
def run():
 t=time.perf_counter();D.save();rfile=P/'current-only-functional-neighbor-gate.json';data=json.loads(rfile.read_text()) if rfile.exists() else {'rows':[],'cursor':0,'scope':'New cowl/head/operator/audio deltas only vs current selected actualparts/wholeallocatedports; no sourceglobalmatrix replay.','wholePASS':False,'physicalPASS':False}
 ns=['Battery_GEA223S30X6GT','F0_FHAC0002_30A','XT60H_mated_with_boots','PBAY_POST_F0','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed','BNO085','MAX98357A_amp','MAIN_Pololu4853','AUX_FULL9p5_POPULATED_SCOPE','ReSpeakerLite_on_REMOVABLE_back','TTP223_touch','Speaker','Monitor_MOD05015','PBAY_F_PI','PBAY_P_SYS','PBAY_F_AUX','PBAY_P_REAR','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating','MG92B_Tail','Tail608','TAIL_FIXED_BEARING_CARTRIDGE','HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','OP_S1_PRIMARY_CASE_CONSERVATIVE','OP_S1_PRIMARY_STEM','OP_S1_LEVER_NOMINAL']
 ns +=[o.Name for o in D.Objects if hasattr(o,'Shape') and o.ViewObject.Visibility and o.Name.startswith(('S0_','Motor_ATO4A','WAGO415_','WAGO615_','NIGHT_INLINE_','Camera','CAM3','ToF','MG92B_','P01','P04','P05','P06'))]
 targets=[(n,D.getObject(n).Shape) for n in ['FC_F_NEG','FC_F_POS','FC_R_NEG','FC_R_POS','HC_FRONT_HOLLOW_MASK','HC_BACK_LOWER','HC_BACK_UPPER','OP_COMMON_REMOVABLE_OPERATOR_PANEL','OP_MONITOR_REMOVABLE_TOPKEEPER','TOUCH_REMOVABLE_SAFE_EDGE_TRAY','SPEAKER_REMOVABLE_BASKET_RIM_TRIAL_KEEPER']]
 for n,src in [('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','source-N1-before-operator-receiver.brep'),('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER','source-N5-before-operator-receiver.brep'),('FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER','source-MTA-before-register-relief.brep')]:
  ff=P/(n+'_current_delta.brep')
  if ff.exists():ss=Part.Shape();ss.read(str(ff))
  else:
   old=Part.Shape();old.read(str(P/src));ss=D.getObject(n).Shape.cut(old);ss.exportBrep(str(ff))
  targets.append((n+'_DELTA',ss))
 tasks=[];boundsclear=0
 for n,s in targets:
  for qn in dict.fromkeys(ns):
   o=D.getObject(qn)
   if not o or not o.Shape.Vertexes:continue
   if lo(s,o.Shape)>=1.25:boundsclear+=1;continue
   tasks.append((n,s,qn,o.Shape))
 # Printed interfaces and head sensors are specific distinct functionalcontacts, never nameOwn.
 for n,q in [('FC_F_NEG','FC_F_POS'),('FC_F_NEG','FC_R_NEG'),('FC_F_POS','FC_R_POS'),('FC_R_NEG','FC_R_POS'),('HC_FRONT_HOLLOW_MASK','HC_BACK_UPPER'),('HC_BACK_LOWER','HC_BACK_UPPER')]:tasks.append((n,D.getObject(n).Shape,q,D.getObject(q).Shape))
 for i in range(data['cursor'],len(tasks)):
  n,s,qn,q=tasks[i];valid=s.isValid() and q.isValid();matched=(n.startswith('OP_') and qn in ['Monitor_MOD05015','OP_S1_PRIMARY_STEM']) or (n.startswith('HC_BACK') and qn=='HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE') or (n=='TOUCH_REMOVABLE_SAFE_EDGE_TRAY' and qn=='TTP223_touch') or (n.startswith('SPEAKER_') and qn=='Speaker') or (n=='FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER_DELTA' and qn=='Speaker') or (qn.startswith(('FC_','HC_')))
  row={'part':n,'neighbor':qn,'valid':valid,'scope':'nominalfixturecontact_FIT3' if matched else 'foreignfullcase_or_allocatedport','required_foreign_mm':1.25}
  if valid:
   g=s.distToShape(q)[0];row['gap']=g
   if g<1.25:row['common']=s.common(q).Volume
   row['clear_scoped']=row.get('common',0)<1e-7 if matched else g>=1.25-1e-6
  else:row['clear_scoped']=None
  data['rows'].append(row);data['cursor']=i+1
  if time.perf_counter()-t>43:break
 data.update({'tasks':len(tasks),'bounds_clear':boundsclear,'completed':data['cursor']==len(tasks),'fails':[r for r in data['rows'] if r['clear_scoped'] is False],'unknown':[r for r in data['rows'] if r['clear_scoped'] is None],'seconds_last_call':time.perf_counter()-t})
 put('current-only-functional-neighbor-gate.json',data);D.save();print(json.dumps({'cursor':data['cursor'],'tasks':len(tasks),'fails':data['fails'],'seconds':time.perf_counter()-t}))
run()
