"""Whole current W4 proposal: all three feeds, factory output and load paths.

Do not rebuild retained servo/factory/JR/R9 local geometry or selected E2.
Only changed real interfaces are tested. This plan alone earns no result.
"""
import sys,json,math,time
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A,Part
import plan_current_pwm_branch as P
from plan_current_pwm_east import context
from build_current_pwm_fixture import tube
ROOT,BASE=P.ROOT,P.BASE
OUT=BASE/'tail-wiring-checkpoint'
line,arc,wire,near,box=P.line,P.arc,P.wire,P.near,P.box
def read(p):return json.loads(p.read_text())
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')

def shift(start,axis,direction,delta,r=12.6):
 """Two equal tangent arcs; transverse delta can be less than2R."""
 a=A.Vector(*start);u=A.Vector(*axis);v=A.Vector(*direction)
 theta=math.acos(1-delta/(2*r));dx=r*math.sin(theta);dy=r*(1-math.cos(theta))
 b=a+u*dx+v*dy;c=b+u*dx+v*dy
 return [arc(list(a+v*r),list(a),list(b)),arc(list(b+u*dx-v*(r*math.cos(theta))),list(b),list(c))]

def build():
 n=1.05/math.sqrt(3);zr=92-2*n;zg=92+n
 red=[line([71.5,-59.725,151.49],[4,-59.725,151.49]),
  arc([4,-59.725,138.89],[4,-59.725,151.49],[-8.6,-59.725,138.89]),
  line([-8.6,-59.725,138.89],[-8.6,-59.725,zr+12.6]),
  arc([4,-59.725,zr+12.6],[-8.6,-59.725,zr+12.6],[4,-59.725,zr])]
 red+=shift(red[-1]['end'],[1,0,0],[0,1,0],14.725)
 red+=[line(red[-1]['end'],[68,-45,zr])]
 ground=[line([37.5,-30.25,141],[47,-30.25,141]),
  arc([47,-30.25,153.6],[47,-30.25,141],[59.6,-30.25,153.6]),
  arc([47,-30.25,153.6],[59.6,-30.25,153.6],[47,-30.25,166.2])]
 ground+=shift(ground[-1]['end'],[-1,0,0],[0,-1,0],13.7)
 ground+=[line(ground[-1]['end'],[-5,-43.95,166.2]),
  arc([-5,-43.95,153.6],[-5,-43.95,166.2],[-17.6,-43.95,153.6]),
  line([-17.6,-43.95,153.6],[-17.6,-43.95,zg+12.6]),
  arc([-5,-43.95,zg+12.6],[-17.6,-43.95,zg+12.6],[-5,-43.95,zg]),
  line([-5,-43.95,zg],[68,-43.95,zg])]
 signal=[line([86.51,14.97,79.2],[86.51,28,79.2]),
  arc([73.91,28,79.2],[86.51,28,79.2],[73.91,40.6,79.2]),
  line([73.91,40.6,79.2],[-10,40.6,79.2]),
  arc([-10,28,79.2],[-10,40.6,79.2],[-22.6,28,79.2]),
  line([-22.6,28,79.2],[-22.6,-33.45,79.2]),
  arc([-10,-33.45,79.2],[-22.6,-33.45,79.2],[-10,-46.05,79.2])]
 signal+=shift(signal[-1]['end'],[1,0,0],[0,0,1],zg-79.2)
 signal+=[line(signal[-1]['end'],[68,-46.05,zg])]
 bare=[arc([86.51,14.97,80.2],[86.51,14.97,79.2],[86.51,13.97,80.2]),line([86.51,13.97,80.2],[86.51,13.97,85.8202])]
 factory=[line([77.5,-59.725,99.99],[86.5,-59.725,99.99]),
  arc([86.5,-59.725,105.99],[86.5,-59.725,99.99],[92.5,-59.725,105.99]),
  line([92.5,-59.725,105.99],[92.5,-59.725,145.49]),
  arc([86.5,-59.725,145.49],[92.5,-59.725,145.49],[86.5,-59.725,151.49]),
  line([86.5,-59.725,151.49],[71.5,-59.725,151.49])]
 routes={k:dict(parts=q,radius=r) for k,q,r in [('XB32',red,1.05),('XB33',ground,1.05),('XS33',signal,1.05),('XS33_bare',bare,math.sqrt(.5/math.pi)),('F_TY_factory_out',factory,2)]}
 return dict(status='WHOLE_CURRENT_W4_PROPOSAL_NOT_SELECTED',selected=False,W4_complete=False,physical_pass=False,
  routes=routes,local_shift_mm=[0,0,15],tail_boundary_x_mm=68,
  G_TAIL2=dict(point_mm=[37.5,-30.25,141],entry_axis=[1,0,0],strip_mm=11,basis='E2 EAST frame; same five project4.75mm pitches, current port3 atY-35; NOT delivered manufacturer pin datum'),
  B3=dict(pad_xy_mm=[86.51,13.97],pad_top_z_mm=84.3202,wire_tip_z_mm=85.8202,logical_role='R3.2',copper_group='N$57',not_unknown_U1_pin=True),
  F_TY=dict(body_bounds_mm=[26.5,-69.85,89.99,77.5,-49.6,111.99],retained_output_recipe='branch-output-plan.json',factory_minimum_mm=84.5,required_nominal_blank_mm=83,project_OD_mm=4,project_R_mm=6),
  support_plan=['Single replaceable F_TY cradle anchored to UpperCarrier south edge atX57/72,Y-35,2M3 stacks; holder input remains separateW5.',
   'Two cuttable casing straps below lid seam. Independent factory exit and upper joint insulation grips; no tape-as-strain-relief.',
   'G_TAIL.2 independent east-side insulation seat on E2 fixture, separate from port3; preserve E2 housing/port3 service keepouts.',
   'B3 insulated grip on upper-carrier north edge nearX60,Y40.6 outside PCB; uncut three-wire local tail seat atX70 reused.',
   'Separate three HELU paths; no braid, no new JR, retain local factory250/R9/sleeves and five local ties.'],
  assembly=['Battery/USB/monitor sources absent. Fit captive M3 anchors on bare upper carrier before PCBs.',
   'Bench prepare factory output lap and three custom/JR joins; shrink insulation off PETG; factory250 remains intact.',
   'Install retained stationary tail local interface before root/case closes; avoid bearing/rotor.',
   'Lay B3 route before populated boards. Solder only to knownB3 copper after R3; delivered fit/polarity gates remain.',
   'Fit intact insulation grips then F_TY casing straps and G_TAIL.2 untinned end.',
   'Service with all sources physically removed: free G_TAIL.2, support B3 board, cut designated replaceable ties/unplugJR; never pull soldered wire.'],
  margins={'custom_fixed_radius_mm':12.6,'cut_rule':'Nominal fitted centreline + stripped/lap allowance +30mm each service end; dry fit before cut; procurement+25percent, not a physical length measurement'},
  delivery_gates=['Delivered FHAC tails/OD/insulation/lid trajectory','JR cavity view/servo exit/uncut250mm profile','PETG fit/supports/creep and tie pressure','Unpowered supported movement, insulation/polarity/pull, E3 before energizing'],
  source_sha256={p.relative_to(ROOT).as_posix():P.sha(p) for p in [Path(__file__),BASE/'pwm-branch-checkpoint/manifest.json',BASE/'tail-mount-checkpoint/manifest.json',ROOT/'hardware/manufacturing/one-batch-prototype-r29/tail-wiring-interface.json',BASE/'wiring-checkpoint/branch-output-plan.json']})

def scene(reader):
 targets,torso=context(reader)
 # Historical native features are not extra physical parts.
 path=BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd';xml=reader.doc(path)
 from check_main_p0_placement import prop
 for o in xml.values():
  if prop(o,'Tip') is not None and prop(o,'Group') is not None:
   for c in prop(o,'Group').findall('.//Link'):targets.pop(c.get('value'),None)
 for n in list(targets):
  if n.startswith('tail/') or n.startswith('P0_') and n[3:] in read(BASE/'tail-mount-checkpoint/tail-assembly-checks.json')['tail_identities']:targets.pop(n)
 tail=BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd';tp=read(BASE/'tail-mount-checkpoint/tail-assembly-checks.json');tx=reader.doc(tail)
 aliases={'TailRoot29':'SupportedRoot34','TailLowerRetainer':'LowerRetainerPETG','MG92BMount29':'RaisedTailSupport','TailBridge29':'RaisedTailBridge'}
 aliases.update({f'TailCartridge{k}{i}':f'Cartridge{k}{i}' for k in ('Bolt','Nut') for i in range(4)})
 for n in tp['tail_identities']:
  actual=aliases.get(n,n if n in tx else 'Current_'+n);targets['tail/'+n]=reader.shape(tail,actual)
 e2=BASE/'pwm-branch-checkpoint/PWMBranchCurrentFinal.FCStd';ex=reader.doc(e2)
 for n in ('UpperCarrier001','E2Fixture','P_REAR','G_TAIL','JPWM','F_PWM_sleeve',*read(BASE/'pwm-branch-checkpoint/final-plan.json')['routes']):targets[n]=reader.shape(e2,n)
 for n in ex:
  if n.startswith(('Band_','TieHead_')) or n.endswith('BoardInsulation'):targets[n]=reader.shape(e2,n)
 # Retained local wiring/R9 and factory reservations, translated with servo.
 local=ROOT/'hardware/electronics/full-cat'
 for folder in ('tail-stationary-local-r3','tail-r9-insulated-r2'):
  for p in sorted((local/folder).glob('*.brep')):
   if any(k in p.stem.upper() for k in ('CENTERLINE','PATH','CURVE')):continue
   s=Part.read(str(p))
   if not s.Solids:continue
   s.translate(A.Vector(0,0,15));targets['local/'+folder+'/'+p.stem]=s
   reader.hashes[p.relative_to(ROOT).as_posix()]=P.sha(p)
 return targets,torso

def run():
 OUT.mkdir(exist_ok=True);assert not (OUT/'space-checks.json').exists(),'Receive existing result first'
 tick=time.monotonic();p=build();save('plan.json',p)
 reader=P.SavedShapes();targets,torso=scene(reader);r=dict(status='PENDING',contacts=[],pairs=0,errors=[],outside=[],selected=False,physical_pass=False)
 curves={n:wire(q['parts']) for n,q in p['routes'].items()}
 # Known single assigned pad hole, not a blanket bare-wire exception.
 targets['PWM1608NominalPCB']=targets['PWM1608NominalPCB'].cut(Part.makeCylinder(.6,3,A.Vector(86.51,13.97,82.5)))
 for n,c in curves.items():
  radius=p['routes'][n]['radius']
  for m,s in targets.items():
   if not near(c,s,radius):continue
   assert s.isValid() and s.Solids,(n,m,'invalid source')
   d=min(c.distToShape(a)[0] for a in s.Solids);r['pairs']+=1
   if d<radius-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=radius))
  t=tube(p['routes'][n]['parts'],radius);assert t.isValid()
  v=t.cut(torso).Volume
  if v>1e-5:r['outside'].append(dict(name=n,volume_mm3=v))
 for i,n in enumerate(curves):
  for m in list(curves)[i+1:]:
   if {n,m}=={'XS33','XS33_bare'} or {n,m}=={'XB32','F_TY_factory_out'}:continue
   req=p['routes'][n]['radius']+p['routes'][m]['radius']
   if near(curves[n],curves[m],req):
    d=curves[n].distToShape(curves[m])[0];r['pairs']+=1
    if d<req-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=req))
 r.update(status='REJECTED_SHARED_W4_PLAN' if r['contacts'] or r['outside'] else 'CURRENT_W4_ROUTE_SPACE_CANDIDATE',
  source_sha256={**p['source_sha256'],**reader.hashes},worker_seconds=round(time.monotonic()-tick,3),
  lengths_mm={n:c.Length for n,c in curves.items()},finished_utc=datetime.now(timezone.utc).isoformat())
 save('space-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','outside','worker_seconds')}),flush=True)
if __name__=='__main__':run()
