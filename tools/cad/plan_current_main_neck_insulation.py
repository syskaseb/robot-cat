"""Current four MAIN solder/pin necks, not a stock-only or old shared boot claim.

Four individual flexible RNF3/32 sleeves follow the existing routes; no shared
Y-boot or converter enclosure.13mm raw,0..-10% longitudinal recovery, nominal
bare neck<=3mm and>=6mm intact overlap. Delivered recovery/fillet/coverage are
explicit unpowered phase2 gates, never manufacturer PCB data inferred here.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,SCENE,scene,check,sha
from check_source_contact_insulation import bounded_distance

NAMES={'W079':'MAIN.VOUT','W080':'MAIN.GND_OUT','W060':'MAIN.GND','W078':'MAIN.VIN'}
def covered_path(old,reverse=False,total=13):
 if reverse:
  line,arc=old.Edges[-1],old.Edges[-2];p=line.valueAt(line.LastParameter);end=line.valueAt(line.FirstParameter)
 else:
  line,arc=old.Edges[0],old.Edges[1];p=line.valueAt(line.FirstParameter);end=line.valueAt(line.LastParameter)
 assert abs(p.z-51.0948)<1e-5 and abs(p.y-21.289)<1e-5 and end.z>p.z
 # Current PCB upper plane48.0948 measured from the supplied model datum.
 lower=A.Vector(p.x,p.y,48.0948);required=total-(end-lower).Length;assert required>0
 radius=arc.Curve.Radius;theta=required/radius
 start=arc.LastParameter if reverse else arc.FirstParameter;sign=-1 if reverse else 1
 a=arc.valueAt(start);mid=arc.valueAt(start+sign*theta/2);b=arc.valueAt(start+sign*theta)
 assert (a-end).Length<1e-5
 return Part.Wire([Part.makeLine(lower,end),Part.Arc(a,mid,b).toShape()]),list(lower),list(p)
def tube(curve,outer=1.75,inner=1.05):
 start=curve.Edges[0].valueAt(curve.Edges[0].FirstParameter)
 def swept(r):return curve.makePipeShell([Part.Wire([Part.makeCircle(r,start,A.Vector(0,0,1))])],True,False)
 s=swept(outer).cut(swept(inner));assert s.isValid() and len(s.Solids)==1 and not s.check(True)
 return s
def run():
 check();tick=time.monotonic();reader,targets,wires=scene();sleeves={};paths={};rows=[]
 for n,role in NAMES.items():
  curve,r=wires['wire/'+n];assert abs(r-1.05)<1e-7
  path,lower,jacket=covered_path(curve,n in ('W060','W078'));s=tube(path);sleeves[n]=s;paths[n]=path
  rows.append(dict(wire=n,role=role,raw_blank_mm=13,sku='RNF100-3/32-0',project_jacket_OD_mm=2.1,
   expanded_ID_min_mm=2.4,recovered_ID_max_mm=1.2,nominal_recovered_wall_mm=.5,wall_tolerance_mm=.2,
   conservative_outer_radius_mm=1.75,current_PCB_plane_mm=48.0948,covered_start_world_mm=lower,jacket_start_world_mm=jacket,
   project_bare_neck_max_mm=3,intact_overlap_min_mm=6,minimum_recovered_length_mm=11.7,
   delivered_fit_gate='Nominal current pin/neck construction only. Do not pretend supplier exposes exactly3mm of copper. Actual joint must fit expandedID, fully cover actual exposed metal and>=6mm intact jacket; verify wall/formation/temperature and modify before any power if not met.'))
 result=dict(status='PENDING',selected=False,M4_complete=False,physical_pass=False,contacts=[],errors=[],pairs=0,rows=rows,
  replaced_legacy='Old MAIN inner7/4 and shared20 RNF3/8 recipe not qualified for changed CP2 four independent necks. Replace with four13mm RNF3/32; no sleeve around hot converter body.',
  basis={'product':'https://www.te.com/en/product-5052942064.html','expandedIDmin':2.4,'recoveredIDmax':1.2,'wallnominal':.5,'walltolerance':.2,
         'axial_shrinkage':'0to-10% fullrecovery in TE RNF100 EMEA standard-sizes drawing; no blank-shrinks-to-exact-placement claim'})
 for n,s in sleeves.items():
  for name,t in targets.items():
   if not s.BoundBox.intersect(t.BoundBox):continue
   check();result['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid(),name
   if q.Volume>1e-5:result['contacts'].append(dict(sleeve=n,part=name,volume_mm3=q.Volume))
  for name,(curve,r) in wires.items():
   if name=='wire/'+n:continue
   b=s.BoundBox;b.enlarge(r)
   if not b.intersect(curve.BoundBox):continue
   check();result['pairs']+=1;d=bounded_distance(s,curve,r)
   if d<r-1e-6:result['contacts'].append(dict(sleeve=n,wire=name,distance_mm=d,required_mm=r))
  for other,t in sleeves.items():
   if other<=n or not s.BoundBox.intersect(t.BoundBox):continue
   result['pairs']+=1;q=s.copy().common(t.copy())
   if q.Volume>1e-5:result['contacts'].append(dict(sleeve=n,other_sleeve=other,volume_mm3=q.Volume))
  s.exportBrep(str(OUT/('MAINNeckSleeve_'+n+'.brep')))
  print(n,'checked',len(result['contacts']),'unresolved',flush=True)
 result['status']='FOUR_CURRENT_MAIN_NECK_SLEEVES_NOMINAL_SPACE_CLEAR' if not result['contacts'] else 'CURRENT_MAIN_NECK_SLEEVES_REJECTED'
 result['source_sha256']={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))};result['worker_seconds']=round(time.monotonic()-tick,3)
 (OUT/'MAIN-neck-insulation-plan.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':run()
