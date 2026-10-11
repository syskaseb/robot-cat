"""Preserve the actually executed shared gallery before one topology change."""
import base64,json
from plan_current_harness_interfaces import ROOT,OUT,SHA

def run():
    gf=OUT/'leg-gallery-motion-checks.json';g=json.loads(gf.read_text())
    assert g['status']=='REJECTED_PROJECT_LEG_GALLERY_MOTION' and g['poses']==108
    assert g['contacts'] and not g['errors']
    assert {c['a'] for c in g['contacts']}=={'FL_P','FR_P','W026_CUSTOM','W037_CUSTOM'}
    sources=g['source_sha256']
    for n,h in sources.items():assert SHA(ROOT/n)==h,n
    names=[OUT/(n+'.json') for n in ('leg-stations-plan','leg-stations-checks','bank-input-plan','bank-input-checks')]
    names += [ROOT/'tools/cad'/n for n in ('check_current_leg_gallery_motion.py','plan_current_leg_stations.py','plan_current_bank_inputs.py')]
    p=dict(reference_gate=g,reference_gate_sha256=SHA(gf),
      previous_receipts={f.relative_to(ROOT).as_posix():json.loads(f.read_text()) for f in names if f.suffix=='.json'},
      scripts_base64={f.relative_to(ROOT).as_posix():base64.b64encode(f.read_bytes()).decode() for f in names if f.suffix=='.py'},
      source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in names},
      scope='Executed108sampledposes: all45contacts ONLY2front power cases/2outputs. All other current cases/curves unchanged clear in this sampled allowance, NOT approved full sweep.',
      selected=False,W5_complete=False,physical_pass=False)
    (OUT/'leg-gallery-motion-rejection.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(poses=108,contacts=len(g['contacts']),frozen_inputs=len(names))))

if __name__=='__main__':run()
