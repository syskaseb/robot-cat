import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def fu(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def low(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def run():
 t=time.perf_counter()
 # Finish sourcegrid receivingstack: lower module plane>=48.52+1.25.
 # Choose50 once from49.77 bound, not a case/angle grid or R/range reduction.
 for o in D.Objects:
  if o.Name in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating'] or o.Name.startswith('FS_PI_'):o.Placement.Base+=V(0,0,7.5)
 centres=sorted(set((round(f.Surface.Center.x,4),round(f.Surface.Center.z,4)) for f in D.getObject('Pi4B_actual_PCB').Shape.Faces if hasattr(f.Surface,'Radius') and abs(f.Surface.Radius-1.375)<1e-6))
 source=Part.Shape();source.read(str(P/'source88-RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER.brp'))
 ribs=[bx(x-3,-74,45.52,6,3,64.48) for x in [-102.5,-44.5]]+[bx(-108,-74,z,69,3,6) for z in [50,99.5]]
 posts=[Part.makeCylinder(3.5,3,V(x,-71,z),V(0,1,0)) for x,z in centres];arms=[bx(x,-74,45.52,6,52,3) for x in [-100,-45]]
 bores=fu([Part.makeCylinder(1.4,10,V(x,-76,z),V(0,1,0)) for x,z in centres]);planned=fu(ribs+posts+arms).cut(bores);front=source.fuse(planned).cut(bores);D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER').Shape=front
 D.recompute();D.save()
 put('final-material-source-coverage.json',{'PCB_lower50_reason':'actualsharedgridtop48.52+1.25=49.77, selected50; fullmodule+allsteel+4posts move together, sourceports retained','actual_primary_axes':centres,'front_valid':front.isValid(),'front_solids':len(front.Solids),'sourcefront_missing_exceptfunctionalbores':source.cut(front).cut(bores).Volume,'planned_missing':planned.cut(front).Volume,'frontcool_gap':front.distToShape(D.getObject('Pi_components_and_cooling').Shape)[0],'bounds':bb(front),'wholeFFC_end':[-86.5,-60.9,61.5],'wholeacceptance':False})
 rows=[]
 def check(n,s,qn,q,scope,own=False):
  l=low(s,q);r={'part':n,'neighbor':qn,'scope':scope,'lower':l,'threshold':1.25,'matched_function':own}
  if l>=1.25 and not own:r.update(clear_scoped=True,method='actualbounds')
  else:
   d=s.distToShape(q)[0];r.update(gap=d,valid=s.isValid() and q.isValid(),clear_scoped=(d>=1.25-1e-7) if not own else None)
   if own or d<1.25:
    c=s.common(q);r.update(common=c.Volume,common_valid=c.isValid())
  rows.append(r);put('finite-current-interface-gates.json',{'rows':rows,'failures':[r for r in rows if r['clear_scoped'] is False],'wholePASS':False,'seconds':time.perf_counter()-t})
 # Named moving pinches only. Samples are finite, never continuous acceptance.
 for yaw,pitch in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]:
  for hn,kind in [('MG92B_Head_pitch','yaw'),('HEAD_YAW_FORK_FIXED_PITCH_HOUSING','yaw'),('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','pitch')]:
   q=D.getObject(hn).Shape.copy()
   if kind=='pitch':q.rotate(V(-135,0,121),V(0,1,0),pitch)
   q.rotate(V(-106,0,127),V(0,0,1),yaw)
   for pn in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating']:
    check(pn,D.getObject(pn).Shape,hn,q,{'yaw':yaw,'pitch':pitch})
 # Changed fixed module/stock and printdelta against finite current nearparts.
 names=['PBAY_P_SYS','PBAY_P_REAR','PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','PBAY_P_AUX','PBAY_POST_F0','F0_FHAC0002_30A','XT60H_mated_with_boots','Battery_GEA223S30X6GT','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed','MAIN_Pololu4853','MAIN_UNSHRUNK_FAMILY_SCOPE','AUX_FULL9p5_POPULATED_SCOPE','BNO085','MAX98357A_amp','Speaker','S1_NKK_S821_installed','Monitor_MOD05015','MG92B_Tail','NIGHT_YTAIL_FIXED_RECEIVER_ROOT']
 names += [o.Name for o in D.Objects if o.Name.startswith(('S0_','Motor_ATO4A','WAGO415_','WAGO615_','NIGHT_INLINE_')) and o.ViewObject.Visibility and hasattr(o,'Shape')]
 targets=['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER']
 for n in targets:
  s=D.getObject(n).Shape
  for qn in names:
   q=D.getObject(qn)
   if not q or qn==n:continue
   own=n.startswith('RG_REAR') and qn in ['F0_FHAC0002_30A','PBAY_POST_F0']
   check(n,s,qn,q.Shape,'changed fixed/fullselectedcontext',own)
 # Cachedsource shapes individually: only sourceBBoxcandidates exact, notwholecompound.
 for n in targets[:4]+[o.Name for o in D.Objects if o.Name.startswith('FS_PI_')]:
  s=D.getObject(n).Shape
  for i,q in enumerate(D.getObject('WAVEGO_complete_126_source_solids').Shape.Solids):
   if low(s,q)<1.25:check(n,s,'WAVEGOsolid'+str(i),q,'actual cached source candidate only')
 pcb=D.getObject('Pi4B_actual_PCB').Shape
 for o in D.Objects:
  if o.Name.startswith('FS_PI_') and o.Name.endswith('_M2p5x12_full'):check(o.Name,o.Shape,pcb.Name if hasattr(pcb,'Name') else 'actualPCB_primarybores',pcb,'primary shaft/PCB interface',True)
 print(json.dumps({'gates':len(rows),'failures':[r for r in rows if r['clear_scoped'] is False],'seconds':time.perf_counter()-t}))
run()
