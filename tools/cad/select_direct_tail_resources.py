"""Reconcile one4piece direct-frame riser replacement, no extra hardware."""
import json,copy,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from phase1_filament_budget import volume
from current_work_guard import check
from release_check import verify
OUT=BASE/'functional-protection'
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',newline='\n')
def run():
 check();tick=time.monotonic();pf=OUT/'direct-frame-tail-risers-native.json';p=json.loads(pf.read_text());assert p['status']=='DIRECT_FRAME_TAIL_RISERS_NATIVE_PARAMETER_REOPEN_STL_COMPLETE'
 new=p['part'];assert SHA(ROOT/new['path'])==new['sha256'];extra=dict(p['source_sha256']);extra[pf.relative_to(ROOT).as_posix()]=SHA(pf);extra[new['path']]=new['sha256'];extra[p['native']]=p['native_sha256'];extra[Path(__file__).relative_to(ROOT).as_posix()]=SHA(Path(__file__))
 before=json.loads((BASE/'phase1-current-print-selection-r2.json').read_text());old=next(r for r in before['prints'] if r['identity']=='CP2:TailRiser');delta=4*(volume((ROOT/new['path']).read_bytes())-volume((ROOT/old['path']).read_bytes()))*.001*1.3*1.35
 for result,name,oldrev,newrev in [('K1','phase1-current-print','r2','r4'),('K3','phase1-material','r2','r4'),('A2','phase1-assembly','r3','r5')]:
  mf=BASE/(name+'-manifest-'+oldrev+'.json');m=json.loads(mf.read_text());assert verify(ROOT,m)['integrity_ok'];q=json.loads((ROOT/m['selection']).read_text());q=copy.deepcopy(q)
  if result=='K1':
   q['prints']=[new if r['identity']=='CP2:TailRiser' else r for r in q['prints']];assert len(q['prints'])==84 and sum(r['quantity'] for r in q['prints'])==117
  elif result=='K3':
   r=next(r for r in q['materials'] if r['sku']=='Sunlu PETG black1.75mm Botland24167');r['updated_solid_upper_with35percent_and200g']+=delta;assert r['updated_solid_upper_with35percent_and200g']<3000
   r['direct_frame_tail_riser_delta_g']=delta
  else:q['source_protection_sequence'].insert(0,'Four20.5mm TailRisers bear directly on actual FrameRear top37.02 and retain top57.52; same fourM2x30/nuts/washers. Do NOT install old P0 TopBottomCover038/005 or old19mm risers. Missing1.5mm root plate must not be recreated under electronics.')
  q['scope']+=' Four direct-frame20.5mm TailRisers replace19mm+obsolete1.5mmrootplate; same upper tail and metal datums. No old topplate selected.'
  sf=BASE/(name+'-selection-'+newrev+'.json');save(sf,q);pins={r['path']:r['sha256'] for r in m['files']};pins.update(extra);pins[sf.relative_to(ROOT).as_posix()]=SHA(sf)
  m.update(selection=sf.relative_to(ROOT).as_posix(),scope=q['scope'],files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())]);assert verify(ROOT,m)['integrity_ok'];save(BASE/(name+'-manifest-'+newrev+'.json'),m)
 print(json.dumps(dict(status='DIRECT_FRAME_TAIL_K1_K3_A2_RECONCILED',identities=84,installed_prints=117,seconds=round(time.monotonic()-tick,3))))
if __name__=='__main__':run()
