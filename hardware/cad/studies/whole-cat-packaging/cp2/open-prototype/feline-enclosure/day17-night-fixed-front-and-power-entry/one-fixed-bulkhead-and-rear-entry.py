import FreeCAD as A, FreeCADGui as G, Part, json, math, datetime, time
from pathlib import Path
D=A.ActiveDocument; V=A.Vector; P=Path(__file__).parent
def put(n,x): (P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bb(s):
 b=s.BoundBox; return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def low(a,b):
 a=bb(a); b=bb(b); return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def run():
 t=time.perf_counter(); before={}; after={}
 m=A.Matrix(); m.A11=0;m.A12=0;m.A13=-1;m.A21=1;m.A22=0;m.A23=0;m.A31=0;m.A32=-1;m.A33=0
 tr=A.Placement(V(-94.88,81.5,5),A.Rotation(m))
 for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating']:
  o=D.getObject(n);before[n]={'b':bb(o.Shape),'v':o.Shape.Volume};o.Placement=tr.multiply(o.Placement);after[n]={'b':bb(o.Shape),'v':o.Shape.Volume,'valid':o.Shape.isValid()}
 # Complete rear units rotate rigidly, retaining their original volumes.
 for n,ang,target in [('F0_FHAC0002_30A',-90,[103,-17.5,52.52]),('XT60H_mated_with_boots',90,[119.5,-70,80]),('PBAY_POST_F0',0,[144,20,55.52])]:
  o=D.getObject(n);before[n]={'b':bb(o.Shape),'v':o.Shape.Volume};rot=A.Placement(V(),A.Rotation(V(0,0,1),ang));o.Placement=rot.multiply(o.Placement);b=bb(o.Shape);o.Placement.Base=o.Placement.Base+V(*[target[i]-b[i] for i in range(3)]);after[n]={'b':bb(o.Shape),'v':o.Shape.Volume,'valid':o.Shape.isValid()}
 # Historical routes/old Pi fasteners are retained as source references only.
 retired=[]
 for o in D.Objects:
  if o.Name.startswith(('FORE_PI_','CF_')) or o.Name in ['HN_FFC_NEUTRAL_ALLOCATED_FULL_PROFILE']:
   if o.ViewObject.Visibility:retired.append(o.Name)
   o.ViewObject.Visibility=False
 D.Label='NIGHT FIXED FRONT BULKHEAD AND REAR ENTRY - UNSELECTED';D.recompute();D.save()
 put('one-whole-placement-before-gate.json',{'input':'01a1e724-51b3-79f1-9426-4349d401c970','source':'cb0fcc8c2b78a8086b1b72e4d28ed3f09f126e30','before':before,'after':after,'retired_visibility_only':retired,'status':'ONE_PLACEMENT_PRE_SUPPORT_GATE','Pi_CSI_project_endpoint':[-155.5,-3,52.5],'Pi_board_top_interval':[96.77,97.75],'interval_basis':'source rigid WAVEGO maxZ39.52 plus1.25 below PCB; neutral head sidearm minZ108 minus GPIO9 plus1.25 gives top<=97.75. This is NECESSARY only; actual moving gate follows.','Pi_board_top_chosen':97,'Pi_contacts':'primary4mounts map Y[-19,39],Z[44.5,93.5]; physical annulus/revision FIT3. No hardware/support implemented before whole gate.','rear_function':'whole F0 longX at central rear, outside negative-Y XA01 bay; full source70x35x26 retained as installation allowance; POST separate +Y and full XT60+boots field above F0.','changed_interfaces':['Pi all GPIO/USB_DATA/USB_AUDIO/CSI/power/cooling/support/assembly','F0 input/output/free leads and POST_F0/XT60/BAT/S0 protection entry','P11/rear common receiver and body rump dependent UNREALIZED'],'whole_kit':False,'physical_pass':False})
 checks=[]; first=None
 fixed=['MG92B_Head_yaw','RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER','NIGHT_YTAIL_FIXED_RECEIVER_ROOT','MG92B_Tail','PBAY_F_PI','PBAY_P_SYS','PBAY_P_REAR','PBAY_F_AUX','S0_body','S0_key','S1_NKK_S821_installed','Monitor_MOD05015','Battery_GEA223S30X6GT','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed','BNO085','Speaker']
 fixed += [o.Name for o in D.Objects if o.Name.startswith('Motor_ATO4A') and o.ViewObject.Visibility]
 def check(n,s,other,q,phase):
  nonlocal first
  l=low(s,q);r={'part':n,'neighbor':other,'phase':phase,'bbox_lower':l,'required_foreign':1.25}
  if l>=1.25:r.update(method='qualified_actual_bounds',clear_scoped=True)
  else:
   good=s.isValid() and q.isValid();d=s.distToShape(q)[0] if good else None;r.update(method='actual_named_shape',valid=good,gap=d,clear_scoped=good and d>=1.25-1e-7)
   if not r['clear_scoped']:
    if good:
     c=s.common(q);r.update(common_volume=c.Volume,common_valid=c.isValid())
    if first is None:first=r
  checks.append(r);put('one-whole-cheap-gate.json',{'checks':checks,'first_falsifier':first,'accepted_whole':False,'seconds':time.perf_counter()-t})
  return r['clear_scoped']
 # Whole fixed-unit neighbors first. No global 126compound or old matrix.
 for n in after:
  s=D.getObject(n).Shape
  for qn in fixed:
   if qn==n:continue
   q=D.getObject(qn)
   if q and not check(n,s,qn,q.Shape,'fixed changed module'):
    break
  if first:break
 # One selected front orientation: bounded correlated head samples only.
 if first is None:
  for yaw,pitch in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]:
   for hn,kind in [('MG92B_Head_pitch','yaw'),('HEAD_YAW_FORK_FIXED_PITCH_HOUSING','yaw'),('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','pitch')]:
    q=D.getObject(hn).Shape.copy()
    if kind=='pitch':q.rotate(V(-135,0,121),V(0,1,0),pitch)
    q.rotate(V(-106,0,127),V(0,0,1),yaw)
    for pn in ['Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating','Pi4B_actual_PCB']:
     if not check(pn,D.getObject(pn).Shape,hn,q,{'yaw':yaw,'pitch':pitch}):break
    if first:break
   if first:break
 # Independent changed F0 against unchanged chosen XA01 stock field.
 q=D.getObject('CF_XA01_raw84p5_ALLOCATED_OD3p1_PLUSp4')
 if q:check('F0_FHAC0002_30A',D.getObject('F0_FHAC0002_30A').Shape,q.Name,q.Shape,'independent rear fixed fullstock delta')
 put('one-whole-cheap-gate.json',{'checks':checks,'first_falsifier':first,'accepted_whole':False,'seconds':time.perf_counter()-t,'scope':'ONE whole fixedPi/rear entry architecture; no alternate pose after first failure; rear source classification preserved. No continuous motion acceptance from nine samples.'})
 D.save();print(json.dumps({'first':first,'checks':len(checks),'seconds':time.perf_counter()-t,'objects':len(D.Objects)}))
run()
