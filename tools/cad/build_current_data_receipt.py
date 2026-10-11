"""Pin three complete DATA guides; no native or whole-W5 credit."""
import json,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA

def run():
    tick=time.monotonic();pf=OUT/'data-bridges-plan.json';gf=OUT/'data-bridges-checks.json'
    p=json.loads(pf.read_text());g=json.loads(gf.read_text())
    assert g['status']=='THREE_DATA_BRIDGES_SAMPLED_CLEAR_NATIVE_OPEN'
    assert not p['rejected'] and not g['contacts'] and not g['errors']
    assert g['cached_leg_stage_poses']==156
    pins={Path(__file__),ROOT/'tests/test_current_data_bridges.py',pf,gf}
    for source in (p,g):
        for n,h in source['source_sha256'].items():assert SHA(ROOT/n)==h,n;pins.add(ROOT/n)
    r=dict(status='THREE_DATA_GUIDES_QUALIFIED_NATIVE_OPEN',selected=False,W5_complete=False,physical_pass=False,
      routes={n:dict(physical_roles=v['endpoints'],guide_mm=v['guide_mm'],
        nominal_blank_mm=v['guide_mm']+sum(v['strip_mm']),strip_each_mm=11,actual_cut_mm=None,
        material=v['SKU'],static_R_mm=5.2) for n,v in p['routes'].items()},
      physical_port_reassignment=p['physical_port_reassignment'],
      current_pairs=g['pairs'],contacts=0,worker_seconds=g['worker_seconds'],unique_leg_stage_poses=156,head_poses=9,
      scope='Static DATA guides only. Sampled project +/-15 leg stages/head grid not approved travel or continuous sweep. Unknown moving factory looms remain open.',
      native_parts_changed=0,result_count=11,fixed_total=20,result_percent=55,change_pp=0,
      lessons=['Rear port1 needs complete west/south departure before rising: tail guard arm x136..144 remains unchanged.',
        'Rear port5 bridge goes behind BOTH complete MTA factory exits, not just their cases.',
        'Use free same-net port for whole departure topology, never merge DATA/GROUND or alter qualified upstream wires.'],
      open=['Independent restraints and actual lever/service access','Native receiving/bank interfaces',
        'Positive source, BUS and12moving looms; complete materials, selected export and W5'],
      source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins})
    r['verification_seconds']=time.monotonic()-tick
    (OUT/'data-bridges-manifest.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(pins=len(pins),seconds=r['verification_seconds'],pairs=r['current_pairs'],guides=3)))

if __name__=='__main__':run()
