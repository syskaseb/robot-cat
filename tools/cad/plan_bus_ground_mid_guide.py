"""One short integral W003 mid-guide on a measured existing structural beam.

No long root search, no new loose print, no use of a wire pilot as a heavy
bank support. Same project flat-lace profile as other accepted wire lands.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,SCENE,scene,check,sha,box
from plan_remaining25_restraint_space import profile
from check_source_contact_insulation import bounded_distance

CENTRE=[117.98489724483592,27.90408019896401,151]
def material(west=False):
 g=dict(project_radius_mm=1,lateral_half_span_mm=1.2,axis=[0,0,1],centre_world_mm=CENTRE,land_mm=9)
 q=profile(g,[-1,0,0] if west else [0,1,0],1);x,y,z=CENTRE
 foot=[x-5.25,y-1.25,147.81,4,5,1.79] if west else [114.5,y+2.75,147.81,3.5,2.5,1.79]
 stem=[x-5.25,y-1.25,149.4,2.5,2.5,4.6] if west else [x-1.25,y+2.75,149.4,2.5,2.5,4.6]
 body=q['body'].fuse(box(*foot)).fuse(box(*stem)).removeSplitter()
 assert body.isValid() and len(body.Solids)==1 and not body.check(True)
 assert body.common(q['band']).Volume<1e-6
 return body,q['band'],dict(group=g,profile=q['recipe'],foot_xyz_size=foot,stem_xyz_size=stem)

def run(west=False):
 check();tick=time.monotonic();reader,targets,wires=scene();f=OUT/'W003RetainedUpperBypass.json';p=json.loads(f.read_text())
 assert p['status']=='CHANGED_W003_ROUTE_CLEAR_RESTRAINT_SELECTION_OPEN' and not p['contacts']
 oldwire,rad=wires['wire/W003'];new=Part.Shape();new.read(str(ROOT/p['path']));wires['wire/W003']=(new,rad)
 body,band,recipe=material(west);parent=targets['Print_UpperCarrier001'];bearing=body.common(parent).Volume
 assert bearing>1e-5,'No structural-beam attachment'
 result=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],errors=[],pairs=0,recipe=recipe,
  parent='UpperCarrier001',beam_joint_overlap_mm3=bearing,new_print_identities=0,extra_installed_lacing_blanks=1,
  extra_lacing_blank_mm=150,lacing_sku='AlphaWire802534B',retained_end_restraints=['BUS paired source','BUS_G/G2.4'],
  scope='One integral light-wire cradle/root on existing3mm structural beam, not a heavy-bank root. Native final, parameter/STL/reopen and selection remain open.')
 for name,s in [('BUSMidGuideBody',body),('BUSMidGuideLacing',band)]:
  for other,t in targets.items():
   if other=='Print_UpperCarrier001':continue
   if not s.BoundBox.intersect(t.BoundBox):continue
   check();result['pairs']+=1;common=s.copy().common(t.copy())
   assert common.isNull() or common.isValid(),('Invalid common',name,other)
   if common.Volume>1e-5:result['contacts'].append(dict(new=name,other=other,volume_mm3=common.Volume))
  for other,(curve,r) in wires.items():
   b=s.optimalBoundingBox();b.enlarge(r)
   if not b.intersect(curve.BoundBox):continue
   check();result['pairs']+=1;d=bounded_distance(s,curve,r)
   if d<r-1e-6:result['contacts'].append(dict(new=name,wire=other,distance_mm=d,required_mm=r))
  s.exportBrep(str(OUT/(name+('West' if west else '')+'.brep')))
 result['status']='BUS_MID_GUIDE_COMMON_SPACE_CLEAR_NATIVE_PENDING' if not result['contacts'] else 'BUS_MID_GUIDE_REJECTED'
 result['source_sha256']={**reader.hashes,f.relative_to(ROOT).as_posix():sha(f),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
  Path(__file__).with_name('plan_remaining25_restraint_space.py').relative_to(ROOT).as_posix():sha(Path(__file__).with_name('plan_remaining25_restraint_space.py'))}
 result['worker_seconds']=round(time.monotonic()-tick,3)
 result['orientation']='west' if west else 'north_rejected_W061'
 (OUT/('BUS-ground-guide-west-plan.json' if west else 'BUS-ground-guide-plan.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':
 import sys
 assert '--west' in sys.argv,'North pad conflicts with W061; do not repeat unchanged.'
 run(True)
