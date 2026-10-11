"""Check the COMPLETE48-path nominal candidate, including all breakout pairs."""
import json,time
from pathlib import Path
from collections import Counter
from route_current_leg_fanouts import ROOT,OUT,SHA,route_rows,pose_row,sampling_parts
from screen_current_joined_leg_looms import screen_rows

def rows_for(looms,routes,pose_angles=None):
    rows=[];joins={};counts={};owners={};starts={}
    for loom in looms:
        angles=pose_angles.get(loom['loom']) if pose_angles else None
        pose=next(v for v in loom['poses'] if v['angles']==angles) if angles is not None else next(v for v in loom['poses'] if not any(v['angles']))
        bundle=pose_row(loom,pose);rows.append(bundle);name=bundle['wire']
        joins[name]=loom['body_dock_mm'];suffix=[];remaining=0
        for segment in reversed(bundle['segments']):
            suffix.append(remaining);remaining+=segment['length_mm']
        counts[name]=(bundle['segments'],list(reversed(suffix)))
        for core in loom['cores'].values():
            wire=core['wire'];parts=routes[wire]['parts']
            rows.append(dict(wire=wire,OD_mm=2,segments=sampling_parts(parts)));owners[wire]=name;starts[wire]=parts[0]['start']
    return rows,(joins,counts,owners,starts)

def run():
    tick=time.monotonic();f=OUT/'leg-fanout-channels-plan.json';p=json.loads(f.read_text())
    assert p['status']=='COMMON_FANOUT_NOMINAL_CHANNELS_ONLY' and len(p['routes'])==36
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    lf=OUT/'joined-leg-looms-plan.json';basis=json.loads(lf.read_text())
    fixed,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in ('ground-tree','data-bridges','positive-source','s0-in-extension')))
    hf=OUT/'head-wire-screen-reference.json';heads=json.loads(hf.read_text())
    for n,h in heads['source_sha256'].items():assert SHA(ROOT/n)==h,n
    rows,meta=rows_for(basis['looms'],p['routes'])
    near=screen_rows(list(fixed.values())+heads['rows'],rows,meta)
    bad=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY']
    result=dict(status='REJECTED_COMMON_NOMINAL_48_PATHS' if bad else 'COMMON_NOMINAL_48_PATHS_PROXIMITY_ONLY',
        near_pairs=near,rejected=bad,screen_seconds=time.monotonic()-tick,
        selected=False,W5_complete=False,physical_pass=False,motion_qualified=False,
        scope='12bundles+36whole fanouts jointly. Only exact final5mm of an aggregate and first5mm of its own core are intended overlap; no whole-pair or separate-core waiver.',
        source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins|{f,lf,hf,Path(__file__),ROOT/'tools/cad/screen_current_joined_leg_looms.py',ROOT/'tools/cad/screen_current_moving_looms.py'}})
    (OUT/'leg-fanout-channels-screen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],near=len(near),reject_count=len(bad),
        owners=dict(Counter(q['a'].split('/')[0] for q in bad)),seconds=result['screen_seconds'])),flush=True)
    return result

if __name__=='__main__':run()
