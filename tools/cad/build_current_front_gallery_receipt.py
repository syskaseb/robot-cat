"""Reuse unchanged geometry from the exact rejected prior, no false PASS."""
import json,time
from pathlib import Path
from plan_current_front_gallery import ROOT,OUT,SHA

def run():
    tick=time.monotonic();f=OUT/'front-gallery-plan.json';g=OUT/'front-gallery-checks.json';ref=OUT/'leg-gallery-motion-rejection.json'
    p,gate,old=[json.loads(q.read_text()) for q in (f,g,ref)]
    assert gate['status']=='COUPLED_FRONT_GALLERY_SAMPLED_CLEAR_NATIVE_OPEN' and not gate['contacts'] and not gate['errors']
    replaced={'FL_P','FR_P','W026_CUSTOM','W037_CUSTOM'}
    assert set(c['a'] for c in old['reference_gate']['contacts'])<=replaced
    pins={Path(__file__),f,g,ref,ROOT/'tests/test_current_front_gallery.py'}
    for source in (p,gate):
        for n,h in source['source_sha256'].items():assert SHA(ROOT/n)==h,n;pins.add(ROOT/n)
    report=dict(status='CURRENT_GALLERY_STATIC_AND_SAMPLED_MOTION_ONLY_NATIVE_OPEN',selected=False,W5_complete=False,physical_pass=False,
      retained_score=dict(count=11,total=20,percent=55,change_pp=0),
      all_cases=12,all_output_guides=4,all_input_guides=12,
      changed=dict(cases=2,curves=8,pairs=gate['pairs'],worker_seconds=gate['worker_seconds'],contacts=0,
        unique_leg_stage_poses=gate['cached_leg_stage_poses'],head_poses=9),
      reuse='Exact unchanged10cases, two rear outputs and six rear inputs from prior leg-gallery-motion-rejection. Its45contacts were exclusively4replaced owners. Unchanged static receipts remain pinned separately; no unchanged full sweep rerun.',
      actual_front_centres_mm={n:s['centre_mm'] for n,s in p['stations'].items()},
      metadata_note='Actual stations above supersede the provisional symmetric Y75 wording in plan.reason; SOUTH isY-93 to stay outside the retained USB U-return. No frame/P0/neck-wall cut.',
      rejected_causes=['Old outerX-60 cases conflict with sampled front knees.',
        'CentralX-60/Y15 whole family enters front mounts/neck risers:309pairs/133.047s/11contacts.',
        'X40/Y50 enters actual P0 side-wall material:246pairs/96.640s/10contacts.',
        'OuterX40Y75/-93 whole family avoids those causes and the retained USB crossing; power input uses common-rail physical5 outside WEST fan flow.'],
      open=['Project angle grid is not approved drive limits or continuous sweep',
        'Native registered bank, all receiving mounts, independent grips and installed service',
        'Remaining body/source/data guides and12factory moving looms; whole stock/E3/selection'],
      source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins})
    report['verification_seconds']=round(time.monotonic()-tick,6)
    (OUT/'front-gallery-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(pins=len(pins),cases=12,output_guides=4,input_guides=12,seconds=report['verification_seconds'])))

if __name__=='__main__':run()
