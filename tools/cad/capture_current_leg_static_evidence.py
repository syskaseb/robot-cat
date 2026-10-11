"""Freeze executed static evidence before changing the sole rejected output."""
import json,base64,hashlib
from pathlib import Path
from plan_current_leg_stations import ROOT,OUT,SHA

def main():
    f=OUT/'leg-stations-plan.json';gfile=OUT/'leg-stations-checks.json'
    p=json.loads(f.read_text());g=json.loads(gfile.read_text())
    assert g['status']=='REJECTED_LEG_OUTPUT_SHARED_LAYOUT' and not g['errors']
    assert g['contacts'] and all(r['a']=='W037_CUSTOM' for r in g['contacts'])
    sources={**p['source_sha256'],**g['source_sha256']}
    for n,h in sources.items():assert SHA(ROOT/n)==h,n
    scripts={n:base64.b64encode((ROOT/n).read_bytes()).decode() for n in sources
             if n in ('tools/cad/plan_current_leg_stations.py','tools/cad/check_current_leg_stations.py')}
    v=dict(reference_plan=p,reference_gate=g,reference_plan_sha256=SHA(f),
           reference_gate_sha256=SHA(gfile),reference_scripts_base64=scripts,
           scope='12cases/fouroutputs processed statically; onlyFR rejected. No head poses executed, no native/selection/W5.',
           creator_sha256=SHA(Path(__file__)))
    (OUT/'leg-current-static-evidence.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(cases=12,unchanged_outputs=3,head_poses=0,pins=len(sources))))

if __name__=='__main__':main()
