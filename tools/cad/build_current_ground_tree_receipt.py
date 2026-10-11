"""Pin the seven complete return guides, without selecting incomplete W5."""
import json,time
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,SHA

def run():
    tick=time.monotonic();files=[OUT/(n+'.json') for n in ('ground-tree-plan','ground-tree-screen','ground-tree-checks')]
    p,screen,gate=[json.loads(f.read_text()) for f in files]
    assert gate['status']=='COUPLED_GROUND_TREE_SAMPLED_CLEAR_NATIVE_OPEN'
    assert not gate['contacts'] and not gate['errors'] and not screen['rejected']
    pins={Path(__file__),ROOT/'tests/test_current_ground_tree.py',*files}
    for source in (p,screen,gate):
        for n,h in source['source_sha256'].items():assert SHA(ROOT/n)==h,n;pins.add(ROOT/n)
    # Historical logical aliases in routing inputs are NOT the new actual
    # common-rail cavity numbers. Bind selected ends by the map below.
    current={'W001':['BAT.minus','G1.2'],'W025':['FL_G.1','G1.5'],
      'W036':['FR_G.5','G1.3'],'W061':['G1.4','G2.1'],'W062':['G2.2','RL_G.4'],
      'W063':['G2.3','RR_G.4'],'W060':['G1.1','MAIN.GND']}
    r=dict(status='SEVEN_GROUND_GUIDES_STATIC_AND_SAMPLED_MOTION_ONLY_NATIVE_OPEN',
      selected=False,W5_complete=False,physical_pass=False,retained_score=dict(count=11,total=20,percent=55,change_pp=0),
      guides={n:dict(current_physical_roles=current[n],historical_input_aliases=v['endpoints'],
        point_mm=[v['parts'][0]['start'],v['parts'][-1]['end']],nominal_guide_mm=v['guide_mm'],
        termination_allowance_mm=sum(v['strip_mm']),actual_cut_mm=None) for n,v in p['routes'].items()},
      frame_correction={'BAT.plus/BAT.minus/F0.in/F0.out/POST_F0':'OpenPrototypePlan.FCStd contains the canonical source objects; RetentionMountsAssembly attribution in earlier endpoint register was incorrect'},
      source_native= (BASE/'OpenPrototypePlan.FCStd').relative_to(ROOT).as_posix(),
      changed_cases=6,changed_pairs=gate['pairs'],contacts=0,worker_seconds=gate['worker_seconds'],
      unique_leg_stage_poses=gate['cached_leg_stage_poses'],head_poses=9,
      limits='Project leg grid+/-15 and head samples are not approved travel limits or a continuous sweep. Static wire radii only; unknown moving factory looms not accepted.',
      selection_supersedes=['Old G1 pose and historical physical cavity aliases','FR_G originalY-79/Z99','Rear D/G central below-deck receiver poses','Only W060 guide from the earlier MAIN/Pi receipt; W1 intact'],
      rejection_lessons=['Do not send rear returns through populated carrier/PCBs: relocate whole receiving gallery.',
        'No north-transfer FR family cleared its complete fixed wire span; change receiving rail and its G1 arrival together.',
        'FR_G whole lower70mm level avoids source column; source exit itself retained after its clear gate.',
        'FlatE rear DATA case crossed W045_CUSTOM; preserve UP case and fan data EAST below MTA instead.'],
      native_parts_changed=0,open=['Independent restraints, native receiving loads and bank, lever/service access',
        'Remaining source/data/BUS and12moving factory looms, whole stock/E3/export/selection'],
      source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins})
    r['verification_seconds']=round(time.monotonic()-tick,6)
    (OUT/'ground-tree-manifest.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(pins=len(pins),pairs=gate['pairs'],seconds=r['verification_seconds'])))

if __name__=='__main__':run()
