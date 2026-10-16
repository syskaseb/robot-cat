"""Plan one physical current assembly map before native full composition."""
import json,re,time
from pathlib import Path
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'functional-protection'
MODEL=OUT/'CurrentW5Protected.FCStd'
P0=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'

def label(o):return prop(o,'Label')[0].get('value')
def run():
 tick=time.monotonic();r=SavedShapes();x=r.doc(MODEL);k=json.loads((BASE/'phase1-current-print-selection-r2.json').read_text())
 refs={label(o):n for n,o in x.items() if n.startswith(('Ref_','Print_'))};p=r.doc(P0)
 children={n:label(o) for n,o in p.items() if 'Rigid_'+n in p}
 bindings=[];missing=[];extra_add=[]
 aliases={'head:UpperFork':'head/0/0/Fork/0/0','head:YawRetainer':'head/0/0/Retainer/0/0','head:PitchCarrier':'head/0/0/Carrier/0/0',
  'RightRiser':'neck/RightRiser/0/0','RetainerBar':'U1_RetainerBar/0/0','AnchorLeft':'U1_AnchorLeft/0/0','AnchorRight':'U1_AnchorRight/0/0'}
 for q in k['prints']:
  n=q['identity'];names=[]
  if n in refs:names=[n]
  elif n.startswith('head:'):names=[aliases.get(n,'head/0/0/'+n.split(':')[1]+'/0/0')]
  elif n.startswith(('tail support:','tail segments:')):names=['tail/'+n.split(':')[1]+'/0/0']
  elif n=='drive:MG92BPrintedHorn20T-R2':names=['head/0/0/YawPrintedHorn/0/0','head/0/0/HornProvisional/0/0','tail/PrintedHornR2/0/0']
  elif n in aliases:names=[aliases[n]]
  elif n=='UpperSpacer':names=['Spacer'+str(i)+'/0/0' for i in range(1,5)]
  elif n in ('LowerClampJaw','TopClampPad'):names=[n+str(i)+'/0/0' for i in range(1,5)]
  elif n.startswith('P0-BASE-'):
   proto=q['native_object'];base_label=children[proto]
   if n.endswith('ANKLE-SPACER'):group=[a for a,b in children.items() if b.startswith('LegSpacer')]
   elif n.endswith('LEG-LINK'):group=[a for a,b in children.items() if b.startswith('LegLink')]
   elif n.endswith('FOOT-BRACKET'):group=[a for a,b in children.items() if b.startswith('Bracket_')]
   elif n.endswith('HIP-COUPLER'):group=[a for a,b in children.items() if re.sub(r'\d+$','',b)==re.sub(r'\d+$','',base_label)]
   else:group=[proto]
   for a in group:
    matches=[name for name in refs if name.startswith('P0_'+a+'/')]
    if len(matches)==1:names+=matches
    else:extra_add.append(dict(identity=n,source=P0.relative_to(ROOT).as_posix(),object=a,world_wrapper='Rigid_'+a))
  elif n=='CP2:TailRiser':extra_add.append(dict(identity=n,source=q['source'],objects='Inspect actual TailRiser installed links, not prototype atorigin',quantity=4))
  elif n.startswith('P0-BATTERY'):extra_add.append(dict(identity=n,source=q['native'],object=q['native_object'],quantity=q['quantity'],placement='Retained R4/R6 battery assembly datums, not prototype origin'))
  else:names=[n+'/0/0']
  found=[dict(object=refs[name],label=name) for name in names if name in refs]
  if not extra_add or extra_add[-1]['identity']!=n:
   if len(found)!=q['quantity']:missing.append(dict(identity=n,required=q['quantity'],found=found,requested=names))
  bindings.append(dict(identity=n,quantity=q['quantity'],instances=found))
 result=dict(status='FULL_COMPOSITION_BINDINGS_PLAN_NOT_A3',selected=False,physical_pass=False,bindings=bindings,missing=missing,additions=extra_add,
  p0_component_labels=children,source_sha256={**r.hashes,(BASE/'phase1-current-print-selection-r2.json').relative_to(ROOT).as_posix():sha(BASE/'phase1-current-print-selection-r2.json'),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'full-composition-plan.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(missing=missing,additions=extra_add,hip_prototype=children['Part__Feature039'],seconds=result['worker_seconds'])),flush=True)
if __name__=='__main__':run()
