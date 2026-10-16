"""One shared MAIN insulation/restraint allocation; not catalog recovered OD.

RNF full recovery wall cannot be applied as the wall on a larger constrained
substrate. Polymer-area estimate is a PROJECT nominal allocation with a
mandatory delivered OD<=3.2mm fit gate, not a certified tolerance maximum.
The rigid grip and band independently allow3.5mm diameter plus0.05 clearance.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,scene,check,sha
from plan_current_main_neck_insulation import covered_path,tube,NAMES
from plan_u1_power_grips import allocation,material,AXES
from plan_u1_grouped_grips import thin_tie_z
from check_source_contact_insulation import bounded_distance

def grip_recipe():
 p=allocation();rows=[dict(r) for r in p['pads'] if r['owner']=='MAINGrip']
 for r in rows:
  if r['name']=='InsulationSeat':
   r['bounds_mm']=list(r['bounds_mm']);r['bounds_mm'][1]=23.089
 band,_=thin_tie_z(52.5948,-51.48,-35.38,18.489,25.839)
 return rows,band,p['bands']['MAINHead']

def grip_shape():
 rows,band,head=grip_recipe();s=material(rows[0]).multiFuse([material(r) for r in rows[1:]])
 for x,y in AXES:s=s.cut(Part.makeCylinder(1.2,15,A.Vector(x,y,45)))
 return s.removeSplitter(),band,head

def run():
 check();tick=time.monotonic();reader,targets,wires=scene();grip,band,head=grip_shape()
 old=targets.pop('MAINGrip/0/0');targets.pop('Power/MAINBand/0/0')
 # Head is unchanged and remains in targets. Never exempt the actual PCB.
 assert old.copy().cut(grip.copy()).Volume>0 and grip.copy().cut(old.copy()).Volume<1e-5
 sleeves={n:tube(covered_path(wires['wire/'+n][0],n in ('W060','W078'))[0],1.6,1.05) for n in NAMES}
 changed={'MAINGripInsulated':grip,'MAINBandInsulated':band,**{'Sleeve/'+n:s for n,s in sleeves.items()}}
 result=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],errors=[],pairs=0,
  formed_OD_project_mm=3.2,rigid_grip_reserved_OD_mm=3.5,raw_blank_mm=13,individual_sleeves=4,
  polymer_area_estimated_OD_mm=2*math.sqrt(1.05**2+(1.2/2+.7)**2-(1.2/2)**2),
  fit_gate='Project formed OD<=3.2mm, actual bare neck<=3mm and >=6mm intact overlap, no crushed conductor or sleeve. Manufacturer full-recovery wall is NOT a constrained-recovery OD guarantee. Verify unplugged before any power; adjust assembly if failed.',
  changed_interfaces=['MAIN grip seat and whole band','four individual pin/jacket sleeves'],
  preserved=['All four whole wire routes','Two MAIN bolt axes and metal stacks','MAIN body placement46.52','MAIN locking head'])
 for n,s in changed.items():
  assert s.isValid() and not s.check(True),n
  for m,t in [*targets.items(),*[(m,t) for m,t in changed.items() if m<n]]:
   if not s.BoundBox.intersect(t.BoundBox):continue
   check();result['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid(),(n,m)
   if q.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=q.Volume))
  for m,(c,r) in wires.items():
   if n=='Sleeve/'+m.removeprefix('wire/'):continue
   b=s.BoundBox;b.enlarge(r)
   if not b.intersect(c.BoundBox):continue
   check();result['pairs']+=1;d=bounded_distance(s,c,r)
   if d<r-1e-6:result['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=r))
  s.exportBrep(str(OUT/(n.replace('/','_')+'.brep')))
  print(n,'checked',len(result['contacts']),'contacts',flush=True)
 result['status']='MAIN_INSULATED_RESTRAINT_NOMINAL_SPACE_CLEAR_NATIVE_PENDING' if not result['contacts'] else 'MAIN_INSULATED_RESTRAINT_REJECTED'
 result['source_sha256']={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
  'tools/cad/plan_current_main_neck_insulation.py':sha(ROOT/'tools/cad/plan_current_main_neck_insulation.py')}
 result['worker_seconds']=round(time.monotonic()-tick,3)
 (OUT/'MAIN-insulated-restraint-plan.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)
if __name__=='__main__':run()
