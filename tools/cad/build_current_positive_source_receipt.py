"""Bind four source guides without pretending nominal S0 is real metal."""
import json,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA

def run():
    tick=time.monotonic()
    files=[OUT/(n+'.json') for n in ('positive-source-plan','positive-source-checks',
                                    's0-in-extension-plan','s0-in-extension-checks')]
    p,g,i,j=[json.loads(f.read_text()) for f in files]
    assert g['status']=='THREE_POSITIVE_SOURCE_GUIDES_SAMPLED_CLEAR_IN_EXTENSION_OPEN'
    assert j['status']=='OUTWARD_S0_IN_SAMPLED_CLEAR_TERMINAL_CASE_FIT_OPEN'
    assert not g['contacts'] and not j['contacts'] and not g['errors'] and not j['errors']
    pins=set(files)|{Path(__file__),ROOT/'tests/test_current_positive_source.py'}
    for v in (g,i,j):
        for n,h in v['source_sha256'].items():assert SHA(ROOT/n)==h,n;pins.add(ROOT/n)
    routes={n:dict(p['routes'][n]) for n in g['checked_guides']}
    routes.update(i['routes'])
    for n,r in routes.items():
        r['nominal_blank_mm']=r['guide_mm']+r.get('termination_allowance_mm',0)
        r['actual_cut_mm']=None
    report=dict(status='FOUR_SOURCE_GUIDES_CLEAR_NATIVE_AND_S0_FIT_OPEN',selected=False,
      W5_complete=False,M4_complete=False,physical_pass=False,native_parts_changed=0,
      routes=routes,source_change=i['source_change'],post_F0=i['post_F0'],
      rejected_embedded_IN_in_positive_plan='SUPERSEDED by separate outward IN plan, never selected',
      worker_seconds=[g['worker_seconds'],j['worker_seconds']],pairs=g['pairs']+j['pairs'],
      contacts=0,unique_leg_stage_poses_each=156,head_poses_each=9,
      S0_nominal_case_lug_overlap_mm3=j['S0_nominal_case_lug_overlap_mm3'],
      caveat='Nominal S0 opaque cylinder is not measured metal. Stud/bay/tool/insulation remain delivery gates; no clearance waiver or physical short inferred.',
      open=['Native independent insulation grips and receiving structure','Full12moving looms and BUS interfaces',
            'Current S0 bay/guard representation','Whole materials, assembly/service, selection and W5'],
      result_count=11,fixed_total=20,result_percent=55,change_pp=0,
      source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins})
    report['verification_seconds']=time.monotonic()-tick
    (OUT/'positive-source-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(pins=len(pins),seconds=report['verification_seconds'],cuts={n:r['nominal_blank_mm'] for n,r in routes.items()})))

if __name__=='__main__':run()
