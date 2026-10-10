"""Restore W2 only after its receiving side and native extended arm pass."""
import json,copy,time,math
from pathlib import Path
from datetime import datetime,timezone
from package_current_head_wiring import ROOT,BASE,sha,read,save,verify,REQUIRED_GATES
OLD=BASE/'head-wiring-checkpoint';OUT=BASE/'head-wiring-access-checkpoint'
def ready(a,n):
 return (a['status']=='CURRENT_HEAD_ACCESS_SPACE_CLEAR' and not a['contacts']
  and n['status']=='CURRENT_NATIVE_HEAD_ACCESS_PREPARED' and not n['contacts']
  and n['native_parameter_restore'] and n['fresh_relocated_reopen']
  and min(v['minimum_sampled_radius_mm'] for v in a['poses'])>=31.5
  and min(v['minimum_radius_mm'] for v in a['receiving_approaches'])>=12.6)
def run():
 tick=time.monotonic();a=read(OUT/'space-checks.json');n=read(OUT/'native-checks.json');assert ready(a,n)
 b=read(OUT/'boundary-checks.json');assert b['status']=='CURRENT_ACCESS_BOUNDARIES_CLEAR'
 model=OUT/'HeadWiringAccess.FCStd';assert sha(model)==n['model_sha256']
 pins={OUT/'space-checks.json',OUT/'native-checks.json',model,
  OUT/'selection.json',OUT/'boundary-checks.json',OUT/'README.md',OUT/'.gitattributes',OLD/'manifest.json',OLD/'selection.json'}
 for q in (a,n):
  for p,digest in q['source_sha256'].items():assert sha(ROOT/p)==digest,p;pins.add(ROOT/p)
 for name in ('plan_current_head_access.py','receive_current_head_access.py','build_current_head_access.py','package_current_head_access.py','qualify_current_head_access_boundary.py'):
  pins.add(ROOT/'tools/cad'/name)
 pins.add(ROOT/'tests/test_current_head_access.py')
 # Old nominal local tails, both factory/JR fit gates, receiver/root/hardware
 # and unchanged carrier remain selected dependencies, not rerun claims.
 for row in read(OLD/'manifest.json')['files']:
  p=ROOT/row['path'];assert sha(p)==row['sha256'],p;pins.add(p)
 selection=copy.deepcopy(read(OLD/'selection.json'))
 selection.update(status='CURRENT_W2_ACCESSIBLE_NOMINAL_PROTOTYPE_SELECTED',native=model.relative_to(ROOT).as_posix(),
  model_sha256=sha(model),prints=[selection['prints'][0]]+n['exports'],
  fixed_tail_boundary_y_mm=85,fixed_tail_y_mm=[85,94],band_y_mm=[91,93.5],boundaries=b['boundaries'],
  minimum_sampled_moving_radius_mm=min(v['minimum_sampled_radius_mm'] for v in a['poses']),
  receiving_approaches=a['receiving_approaches'],functional_neck=a['functional_neck'],
  supersedes='OldY67 boundary cannot receive fixedR12.6 leads pastATO. Current arm/9constant moving paths and three real opposite approaches replace it; old local factory/JR geometry retained, not reselected blindly.',
  stock_rule='Continuous HELU must be aggregated with W3, no extra joint atY85. Same oneT18I replacement, same2M3x10 kit, twoJR300 and six individual local sleeves; no old/new-anchor double counting.',
  assembly=[v.replace('Y67','Y85') for v in selection['assembly']],
  load_path='Unchanged carrier receiver/twoM3x10/captive nuts -> extended native neck arm ->9mm intact tailsY85..94. External neck material stays within200mm functional width; no upper cosmetic torso shell installed.',
  checked_utc=datetime.now(timezone.utc).isoformat())
 for row in selection['length_stock_rows']:
  if row['wire'] in ('XB22','XB23','XS23'):
   row['moving_HELU_mm']=max(v['length_mm'] for v in a['poses'] if v['wire']==row['wire'])
   amount=5*math.ceil((row['local_mixed_JR_HELU_guide_mm']+row['moving_HELU_mm']+9+60)/5)
   row['conservative_local_HELU_fit_allowance_mm']=amount;row['local_procurement_contribution_mm']=5*math.ceil(amount*1.25/5)
 for row in n['exports']:pins.add(ROOT/row['path'])
 for p in OUT.glob('*.brep'):pins.add(p)
 save(OUT/'selection.json',selection)
 manifest=dict(schema_version=1,readiness='prototype',result_id='W2',physical_pass=False,
  files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(pins)],
  gates={g:dict(status='open',reason='Unpowered delivered fit/phase2 trials, not physical approval.') for g in REQUIRED_GATES})
 manifest['gates']['geometry']=dict(status='pass',reason='New terminal arm,9constant moving paths and three receiving approaches beyondATO, native parameter/reopen/closedSTL. Unchanged local factory/JR proof inherited with explicit fit budgets.',evidence=[(OUT/'space-checks.json').relative_to(ROOT).as_posix(),(OUT/'native-checks.json').relative_to(ROOT).as_posix()])
 assert verify(ROOT,manifest)['integrity_ok'];save(OUT/'manifest.json',manifest)
 score=read(BASE/'current-phase1-score.json');assert score['fixed_total']==20
 if 'W2' not in score['confirmed_result_ids']:score['confirmed_result_ids'].append('W2')
 score.update(result_count=len(score['confirmed_result_ids']),result_percent=5*len(score['confirmed_result_ids']),change_pp=5,new_result='W2',
  evidence=(OUT/'manifest.json').relative_to(ROOT).as_posix(),evidence_sha256=sha(OUT/'manifest.json'),checked_utc=datetime.now(timezone.utc).isoformat())
 score.pop('withdrawn_result',None);score.pop('withdrawal_reason',None);save(BASE/'current-phase1-score.json',score)
 print(json.dumps(dict(percent=score['result_percent'],pins=len(pins),seconds=time.monotonic()-tick)))
if __name__=='__main__':run()
