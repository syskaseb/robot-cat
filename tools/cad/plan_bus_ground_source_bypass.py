"""One complete W003 middle-branch bypass, fixed ends and R10 retained.

Eliminate the unnecessary low U and high free loop, do not shrink insulation
to make a test green. New routed branch only; existing endpoint proofs reused.
"""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,SCENE,scene,check,sha
from check_source_contact_insulation import bounded_distance,bare_ring,GROUPS

def quarter(p,u,v,R=10):
 u=A.Vector(*u);v=A.Vector(*v);p=A.Vector(*p)
 mid=p+u*(R/math.sqrt(2))+v*(R*(1-1/math.sqrt(2)))
 end=p+(u+v)*R
 return Part.Arc(p,mid,end).toShape(),end
def candidate(old,compact=True):
 edges=list(old.Edges[:9]);p=edges[-1].valueAt(edges[-1].LastParameter);new=[]
 for u,v in [((1,0,0),(0,1,0)),((0,1,0),(0,0,1))]:
  e,p=quarter(p,u,v);new.append(e)
 z=125 if compact else 175;q=A.Vector(p.x,p.y,z);new.append(Part.makeLine(p,q));p=q
 if compact:
  end=A.Vector(120.5,48.75,145);h=A.Vector(end.x-p.x,end.y-p.y,0);length=h.Length;h.normalize()
  assert length>20
  e,p=quarter(p,(0,0,1),h);new.append(e);q=p+h*(length-20);new.append(Part.makeLine(p,q));p=q
  e,p=quarter(p,h,(0,0,1));new.append(e);assert (p-end).Length<1e-6
  e,p=quarter(p,(0,0,1),(-1,0,0));new.append(e)
  new.append(old.Edges[-1])
 else:new.extend(old.Edges[16:])
 wire=Part.Wire(edges+new);assert wire.isValid()
 # Last9mm is identical endpoint material, not a new interface. With the
 # retained upper route, the vertical119..175 segment is also an exact subset
 # of the old89..175 segment. Check only the genuinely new two quarter-arcs.
 return wire,Part.Wire(new[:-1] if compact else new[:2]),edges

def run(compact=True):
 check();tick=time.monotonic();reader,targets,wires=scene();old,radius=wires.pop('wire/W003');new,changed,kept=candidate(old,compact)
 assert (old.Vertexes[0].Point-new.Vertexes[0].Point).Length<1e-5
 assert (old.Edges[-1].valueAt(old.Edges[-1].LastParameter)-new.Edges[-1].valueAt(new.Edges[-1].LastParameter)).Length<1e-5
 report=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],errors=[],pairs=0,
  wire='W003',source='BUS.G',target='G2.4',nominal_radius_mm=1,project_curve_radius_mm=10,
  old_guide_mm=old.Length,new_guide_mm=new.Length,project_termination_allowance_mm=35.05,
  nominal_new_blank_mm=5*math.ceil((new.Length+35.05)/5),old_nominal_blank_mm=395,
  first_nine_edges_retained=True,last9mm_land_retained=True,
  stock='Same one SR900 BUS_DG factory cable; no new wire SKU or physical cable. Actual trim remains unpowered fit gate.',
  restraints='BUS paired source and G2.4 fixed native end restraints unchanged. Intermediate lacing/support and selection not inferred from free analytic curve.')
 for n in ('S0MountFoundation','PostF0Dock','S1MountCurrent'):
  s=Part.Shape();s.read(str(OUT/(n+'.brep')));targets['NewMount/'+n]=s
 for name,s in targets.items():
  b=changed.optimalBoundingBox();b.enlarge(radius)
  if not b.intersect(s.BoundBox):continue
  check();report['pairs']+=1;d=bounded_distance(changed,s,radius)
  if d<radius-1e-6:report['contacts'].append(dict(other=name,distance_mm=d,required_mm=radius))
 for name,(curve,r) in wires.items():
  b=changed.optimalBoundingBox();b.enlarge(radius+r)
  if not b.intersect(curve.BoundBox):continue
  check();report['pairs']+=1;d=bounded_distance(changed,curve,radius+r)
  if d<radius+r-1e-6:report['contacts'].append(dict(wire=name,distance_mm=d,required_mm=radius+r))
 for gid,(prefix,ids,nets) in GROUPS.items():
  names=[n for n in targets if any(n.startswith(prefix+v+'/') for v in ids)]
  for mouth in ([False,True] if gid.startswith('S1') else [False]):
   group=Part.makeCompound([bare_ring(targets[n],gid,mouth) if 'ring_' in n else targets[n] for n in names])
   d=bounded_distance(new,group,radius+1);report['pairs']+=1
   if d<radius+1-1e-6:report['contacts'].append(dict(insulation_group=gid,mouth=mouth,distance_mm=d,required_mm=radius+1))
 name='W003CompactBypass' if compact else 'W003RetainedUpperBypass';f=OUT/(name+'.brep');new.exportBrep(str(f))
 report.update(status='CHANGED_W003_ROUTE_CLEAR_RESTRAINT_SELECTION_OPEN' if not report['contacts'] else 'W003_BYPASS_REJECTED',
  path=f.relative_to(ROOT).as_posix(),sha256=sha(f),source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 (OUT/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':
 import sys
 assert '--retained-upper' in sys.argv,'Compact below-G2 approach rejected; do not repeat it unchanged.'
 run(False)
