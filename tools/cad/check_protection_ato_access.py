"""Changed M4 material/wire versus retained routine fuse/jaw corridors only."""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,SCENE,check,sha
from check_main_p0_placement import SavedShapes,prop
from current_bank_datums import datums,nominal_sweep
from check_source_contact_insulation import bounded_distance

def run():
 check();tick=time.monotonic();reader=SavedShapes();objects=reader.doc(SCENE);targets={}
 for n,o in objects.items():
  if not n.startswith('Ref_'):continue
  label=prop(o,'Label')[0].get('value')
  if label.startswith(('F_L','F_R')) and '_CP2_' in label:targets[label]=reader.shape(SCENE,n)
 placed=datums(targets);access={}
 for r in placed:
  access[r['id']+'/ATO']=nominal_sweep(r);x,y=r['centre_xy_mm'];z=r['flange_top_z_mm']
  for sign in (-1,1):
   lo,hi=(-5.55,-2.55) if sign==-1 else (2.55,5.55)
   access[r['id']+'/jaw'+str(sign)]=Part.makeBox(21.1,hi-lo,47,A.Vector(x-10.55,y+lo,z+11))
 parts={}
 for n in ['S0MountFoundation','S1MountCurrent','PostF0Dock','BUSMidGuideBodyWest','BUSMidGuideLacingWest','MAINGripInsulated','MAINBandInsulated',
  'S1SharedFrameScrew',*['S0'+p+'_'+x+s for x in ('96','58') for p,s in [('M6',''),('Washer','top'),('Washer','lower'),('Nut','')]],
  'Sleeve_W079','Sleeve_W080','Sleeve_W060','Sleeve_W078']:
  f=OUT/(n+'.brep');s=Part.Shape();s.read(str(f));parts[n]=s
 route=Part.Shape();route.read(str(OUT/'W003RetainedUpperBypass.brep'))
 result=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],pairs=0,
  scope='Only new protection/source hardware/BUSmidguide/MAINsleeves and revisedW003 versus CURRENT12fuse35mmnominalwithdrawal and both jaw corridors. Existing unrelated service qualification retained. Nominal tools/travel, not delivered force or continuous motion approval.')
 for n,s in parts.items():
  for m,t in access.items():
   if not s.BoundBox.intersect(t.BoundBox):continue
   check();result['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid()
   if q.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=q.Volume))
 for m,t in access.items():
  b=t.BoundBox;b.enlarge(1)
  if not b.intersect(route.BoundBox):continue
  check();result['pairs']+=1;distance=bounded_distance(t,route,1)
  if distance<1-1e-6:result['contacts'].append(dict(a='W003',b=m,distance_mm=distance,required_mm=1))
 result.update(status='CHANGED_PROTECTION_PRESERVES_NOMINAL_ROUTINE_ATO_ACCESS' if not result['contacts'] else 'CHANGED_PROTECTION_ATO_ACCESS_REJECTED',
  source_sha256={**reader.hashes,**{(OUT/(n+'.brep')).relative_to(ROOT).as_posix():sha(OUT/(n+'.brep')) for n in parts},
   (OUT/'W003RetainedUpperBypass.brep').relative_to(ROOT).as_posix():sha(OUT/'W003RetainedUpperBypass.brep'),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
  holders=12,access_corridors=len(access),worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'changed-ATO-access.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)
if __name__=='__main__':run()
