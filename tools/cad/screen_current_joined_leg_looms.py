"""Cheap COMMON12bundle/36core planning, not another partial CAD receipt."""
import json,math,time,itertools
from pathlib import Path
from plan_current_moving_looms import ROOT,OUT,SHA
from screen_current_moving_looms import pose_row,only_new_pairs
from screen_current_remaining_routes import route_rows

def rows_for(looms,angles=None):
    rows=[];joins={};counts={};owners={};starts={}
    for r in looms:
        chosen=([angles[0]] if r['loom'].endswith('1') else list(angles)) if angles else ([0] if r['loom'].endswith('1') else [0,0])
        v=next(v for v in r['poses'] if v['angles']==chosen)
        bundle=pose_row(r,v);rows.append(bundle);joins[bundle['wire']]=r['body_dock_mm']
        # Remaining actual centreline length, not an assumed last6samples.
        suffix=[];remaining=0
        for segment in reversed(bundle['segments']):
            suffix.append(remaining);remaining+=segment['length_mm']
        counts[bundle['wire']]=(bundle['segments'],list(reversed(suffix)))
        for n,f in v['fanouts'].items():
            rows.append(dict(wire=n,OD_mm=2,segments=f['parts']));owners[n]=bundle['wire'];starts[n]=f['parts'][0]['start']
    return rows,joins,counts,owners,starts

def screen_rows(old,new,metadata):
    joins,counts,owners,starts=metadata
    def final_five(owner,index,point):
        parts,suffix=counts[owner]
        q=parts[index]
        # The bundle ends in short linear Bézier chords (front Knee ends
        # in a straight land). Reject any non-final return crossing too.
        return q['kind']=='line' and suffix[index]+math.dist(point,q['end'])<=5+1e-8
    def skip(a,b,ia,ib,pa,pb):
        # Exact intended transition between an aggregate3core envelope and
        # its three own component cores only. Never skip an entire owner pair
        # or a later return crossing; no exemption between separate cores.
        if owners.get(b)==a:
            return final_five(a,ia,pa) and ib==0 and math.dist(pb,starts[b])<=5
        if owners.get(a)==b:
            return final_five(b,ib,pb) and ia==0 and math.dist(pa,starts[a])<=5
        return False
    return only_new_pairs(old,new,skip=skip)

def run():
    tick=time.monotonic();f=OUT/'joined-leg-looms-plan.json';p=json.loads(f.read_text())
    assert p['status']=='JOINED_12_LOOMS_36_FANOUTS_LENGTH_ONLY'
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    old,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in ('ground-tree','data-bridges','positive-source','s0-in-extension')))
    hf=OUT/'head-wire-screen-reference.json';heads=json.loads(hf.read_text())
    for n,h in heads['source_sha256'].items():assert SHA(ROOT/n)==h,n
    fixed=list(old.values())+heads['rows'];nominal,*meta=rows_for(p['looms'])
    near=screen_rows(fixed,nominal,meta);bad=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY']
    result=dict(status='REJECTED_WHOLE_LEG_HARNESS_PROXIMITY' if bad else 'WHOLE_LEG_HARNESS_PROXIMITY_ONLY',
        nominal_near_pairs=near,rejected=bad,selected=False,W5_complete=False,physical_pass=False,
        bundle_paths=12,core_paths=36,project_breakout_aggregate_overlap_mm=5,
        scope='Full nominal12bundles/36cores against one retained route/head reference. Only own aggregate/core5mm join overlap is intentional. Real material/motion/native/access OPEN.',
        screen_seconds=time.monotonic()-tick,
        source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins|{f,hf,Path(__file__),ROOT/'tools/cad/screen_current_moving_looms.py'}})
    (OUT/'joined-leg-looms-screen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    from collections import Counter
    print(json.dumps(dict(status=result['status'],rejected_count=len(bad),near_count=len(near),
        rejected_owners=dict(Counter(q['a'].split('/')[0] for q in bad)),seconds=result['screen_seconds'])),flush=True)
    return result

if __name__=='__main__':run()
