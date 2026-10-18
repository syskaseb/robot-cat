"""Generic immutable wire receiver with identity-scoped unchanged-pair reuse."""
import json
import sys
import time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from check_feline_all_current_lands import near


def main():
    tick=time.monotonic()
    src,dest,parentfile=[OUT/n for n in (sys.argv[1:4] if len(sys.argv)==4 else
        ['n01-coupled-clocked-joints.json','n01-clocked-wire-gate.json','n01-coupled-fan-wire-gate.json'])]
    assert not dest.exists();p,shapes,rows=packed(src)
    for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
    parent=json.loads(parentfile.read_text());changed=set(p['changed_part_names'])
    assert all(changed.intersection((r['a'],r['b'])) for r in parent['exact_wire_failures'])
    reusable={tuple(sorted((r['a'],r['b']))):r for r in parent.get('reused_unchanged_pairs',[])+parent['completed_queries']
        if r['gap_mm']>=.2-1e-5 and not changed.intersection((r['a'],r['b']))}
    # Raw shape identity of every reused participant is verified against the
    # pinned parent snapshot, not only an unchanged-name assertion.
    parentplan=json.loads((ROOT/p['source_parent']).read_text());oldrows={r['name']:r for r in parentplan['parts']}
    assert all(rows[n]['sha256']==oldrows[n]['sha256'] for pair in reusable for n in pair)
    wires={n:s for n,s in shapes.items() if rows[n].get('wire_owner')};bounds={n:s.BoundBox for n,s in wires.items()}
    def owner(n):return 'F_PWM.'+n.split(':')[1].split('_')[0] if n.startswith('F_PWM:') else rows[n]['wire_owner']
    result=dict(status='RUNNING_CHANGED_WIRE_SNAPSHOT_GATE',selected=False,N01_complete=False,physical_pass=False,
        exact_wire_failures=[],completed_queries=[],errors=[],pairs=0,reused_unchanged_pairs=list(reusable.values()),
        source_sha256={src.relative_to(ROOT).as_posix():sha(src),parentfile.relative_to(ROOT).as_posix():sha(parentfile),
            (ROOT/p['bundle']).relative_to(ROOT).as_posix():p['bundle_sha256'],Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        whole_world_outline_motion_roots_tools_not_qualified=True)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    try:
        for i,(n,s) in enumerate(wires.items()):
            for m,t in list(wires.items())[i+1:]:
                if owner(n)==owner(m) or tuple(sorted((n,m))) in reusable or not near(bounds[n],bounds[m],.2):continue
                if time.monotonic()-tick>150:raise TimeoutError('150s; keep completed pairs')
                gap=s.distToShape(t)[0];result['pairs']+=1
                r=dict(a=n,b=m,gap_mm=gap,minimum_mm=.2,group_a=rows[n]['group'],group_b=rows[m]['group'])
                result['completed_queries'].append(r)
                if gap<.2-1e-5:result['exact_wire_failures'].append(r)
                if result['pairs']%10==0:save()
            save()
        result['status']='WIRE_SNAPSHOT_REJECTED_NO_WORLD_GATE' if result['exact_wire_failures'] else 'WIRE_SNAPSHOT_CLEAR_WORLD_GATE_OPEN'
    except Exception as e:result['status']='PARTIAL_WIRE_SNAPSHOT_GATE';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],pairs=result['pairs'],reused=len(reusable),
        failures=len(result['exact_wire_failures']),errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
