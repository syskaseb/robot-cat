"""Shared space for nominal removable source-contact insulation, not dielectric PASS.

Two half-lapped passes plus a folded end cushion allocate at most1mm locally
for0.15mm Temflex165. Application/cut-through/heat/creep are delivery/E3 gates.
Rigid full boxes were rejected; never cut established wires to fit them.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,scene,SCENE,check,sha

GROUPS={'S0_IN':('S0_',['ring_IN','stud_IN','washer_IN','nut_IN'],['W076_FACTORY','W076_EXTENSION']),
        'S0_OUT':('S0_',['ring_OUT','stud_OUT','washer_OUT','nut_OUT'],['W066']),
        **{'S1_'+str(t):('current/S1_',['ring_'+str(t),'screw_'+str(t)],[net]) for t,net in [(2,'W067'),(3,'W064'),(5,'W068'),(6,'W065')]}}

def bare_ring(saved,gid):
 """Primary rounded eye, NOT the historical rectangular whole-product box.

 Keep the FULL possible neck length conservatively, including metal that may
 be beneath factory nylon. Do not infer the undisclosed nylon-mouth position.
 Existing eye centre, normal and barrel axis are measured from saved faces.
 """
 cylinders=[f.Surface for f in saved.Faces if isinstance(f.Surface,Part.Cylinder)]
 s0=gid.startswith('S0');hole=next(c for c in cylinders if abs(c.Radius-(5.02 if s0 else 2.667))<1e-5)
 barrel=next(c for c in cylinders if abs(c.Radius-(3.2 if s0 else 3.175))<1e-5)
 normal=hole.Axis;axis=barrel.Axis
 eye=hole.Center+normal*((barrel.Center-hole.Center).dot(normal))
 thickness=1.05 if s0 else 1.042;width=13.7 if s0 else 9.605;length=26.9 if s0 else 22.123
 origin=eye-normal*thickness;cross=normal.cross(axis)
 pts=[origin+axis*u+cross*v for u,v in [(0,-width/2),(length,-width/2),(length,width/2),(0,width/2)]]
 neck=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(normal*thickness)
 tongue=Part.makeCylinder(width/2,thickness,origin,normal).fuse(neck)
 tongue=tongue.cut(Part.makeCylinder(5.02 if s0 else 2.591,thickness+.2,origin-normal*.1,normal))
 assert tongue.isValid() and len(tongue.Solids)==1
 return tongue

def bounded_distance(s,t,limit):
 """Exact threshold test with local clipping, never sampled clearance.

 Material omitted outside s's actual bounding box expanded by limit cannot
 be within limit of s. This reduces OCC face/edge distance work, not the gate.
 """
 b=s.optimalBoundingBox();b.enlarge(limit+1e-5)
 if not b.intersect(t.BoundBox):return limit+1e-5
 clip=Part.makeBox(b.XLength,b.YLength,b.ZLength,A.Vector(b.XMin,b.YMin,b.ZMin))
 q=t.copy().common(clip)
 if q.isNull() or not q.Vertexes:return limit+1e-5
 assert q.isValid(),'Invalid clipped distance operand'
 return s.distToShape(q)[0]
def run():
 check();tick=time.monotonic();r,targets,wires=scene();groups={};members={};own={};reserve=1.0
 for gid,(prefix,ids,nets) in GROUPS.items():
  names=[n for n in targets if any(n.startswith(prefix+v+'/') for v in ids)];assert len(names)==len(ids),(gid,names)
  members[gid]=names;groups[gid]=Part.makeCompound([bare_ring(targets[n],gid) if 'ring_' in n else targets[n] for n in names]);own[gid]=nets
 for n in ('S0MountFoundation','PostF0Dock','S1MountCurrent'):
  s=Part.Shape();s.read(str(OUT/(n+'.brep')));targets['NewMount/'+n]=s
 out=dict(status='PENDING',selected=False,physical_pass=False,insulation_reserve_each_mm=reserve,groups=[],contacts=[],errors=[],pairs=0,
  supplier_interface_gates=[],not_a_dielectric_or_touch_safety_test=True)
 for gid,s in groups.items():
  b=s.optimalBoundingBox();b.enlarge(reserve);nearest=[]
  skip=set(members[gid]);supplier=('S0_body_CP2/','S0_neck_CP2/','S0_key_CP2/') if gid.startswith('S0') else ('current/S1_body_CP2/','current/S1_control_CP2/')
  for name,t in targets.items():
   if name in skip or not b.intersect(t.BoundBox):continue
   if name.startswith(supplier):
    out['supplier_interface_gates'].append(dict(group=gid,reference=name,reason='Own nominal casing/neck overlaps its own terminals; actual delivered flange/terminal recess not inferred. No internal physical clearance claimed.'));continue
   check();out['pairs']+=1;d=bounded_distance(s,t,reserve)
   if d<reserve-1e-6:out['contacts'].append(dict(group=gid,other=name,distance_mm=d,required_mm=reserve))
   nearest.append((d,name))
  for name,(curve,rad) in wires.items():
   if name in ['wire/'+net for net in own[gid]] or name in ['body/'+net for net in own[gid]]:continue
   bb=A.BoundBox(b);bb.enlarge(rad)
   if not bb.intersect(curve.BoundBox):continue
   check();out['pairs']+=1;d=bounded_distance(s,curve,reserve+rad)
   if d<reserve+rad-1e-6:out['contacts'].append(dict(group=gid,wire=name,distance_mm=d,required_mm=reserve+rad))
  for other,t in groups.items():
   if other<=gid:continue
   check();out['pairs']+=1;d=bounded_distance(s,t,2*reserve)
   if d<2*reserve-1e-6:out['contacts'].append(dict(group=gid,other_group=other,distance_mm=d,required_mm=2*reserve))
  out['groups'].append(dict(id=gid,metal_reference_members=members[gid],same_net_wire_exclusions=own[gid],candidate_threshold_checks=sorted(nearest)[:4],
   tape_blank_mm=750 if gid.startswith('S0') else 500,width_mm=15,
   procedure='With every source absent: deburr/clean per supplier, torque terminals on bench first. Fully cap exposed stud/screw tip, nut/washer/tongue and transitions to intact factory nylon/jacket. Two complete half-lapped passes and folded end cushion, finish with relaxed lap. Do not bridge adjacent terminals, obstruct toggle/key, claim strain relief, or cover hot dissipating components. Replace disturbed tape after service.'))
  (OUT/'contact-insulation-progress.json').write_text(json.dumps(out,indent=2)+'\n')
  print(gid,'checked',len(out['contacts']),'unresolved',flush=True)
 out['status']='NOMINAL_EXTERNAL_INSULATION_SPACE_CLEAR' if not out['contacts'] and not out['errors'] else 'INSULATION_SPACE_OPEN'
 out['worker_seconds']=round(time.monotonic()-tick,3)
 out['source_sha256']={**r.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))}
 out['material']='Existing3MTemflex165 LAPP61721030 roll15x10000mm;3500mm new nominal blanks plus1000mm practice. Actual trim/layer coverage/tolerance unpowered gate; tape not an energizing authorization.'
 out['bare_metal_basis']='TE130171 B4 rounded eyeW9.525+0.08,thicknessmax1.042/holemin5.182; TE130207 rounded eye plus13.7 project width margin/thickness1.05, retained smaller5.02hole is conservative. Entire possible neck remains included; factory nylon barrel NOT declared exposed metal. Primary shapes are envelopes, not supplier STEP or measured delivered parts.'
 out['primary_tds']='https://multimedia.3m.com/mws/media/2145173O/3m-temflex-vinyl-electrical-tape-165-datasheet-en-ner.pdf'
 (OUT/'contact-insulation-space.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
if __name__=='__main__':run()
