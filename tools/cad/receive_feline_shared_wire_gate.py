"""Source-pinned generic receiver for the saved all-station fan snapshot."""
import json
import time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from check_feline_all_current_lands import near


def main():
    tick=time.monotonic();src=OUT/'n01-coupled-fan-family.json';dest=OUT/'n01-coupled-fan-wire-gate.json'
    assert not dest.exists();p,shapes,rows=packed(src)
    for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
    parentfile=OUT/'n01-coupled-wire-preflight.json';parent=json.loads(parentfile.read_text())
    changed=set(p['changed_part_names'])
    assert all(changed.intersection((r['a'],r['b'])) for r in parent['exact_wire_failures']), 'An inherited failure was not addressed'
    reusable={tuple(sorted((r['a'],r['b']))):r for r in parent['completed_queries'] if r['gap_mm']>=.2-1e-5 and not changed.intersection((r['a'],r['b']))}
    wires={n:s for n,s in shapes.items() if rows[n].get('wire_owner')}
    bounds={n:s.BoundBox for n,s in wires.items()}
    result=dict(status='RUNNING_SHARED_FAN_PROFILE_GATE',selected=False,N01_complete=False,physical_pass=False,
        exact_wire_failures=[],completed_queries=[],errors=[],pairs=0,reused_unchanged_pairs=list(reusable.values()),
        source_sha256={src.relative_to(ROOT).as_posix():sha(src),(ROOT/p['bundle']).relative_to(ROOT).as_posix():p['bundle_sha256'],
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},whole_world_motion_tools_not_qualified=True)
    def owner(n):return 'F_PWM.'+n.split(':')[1].split('_')[0] if n.startswith('F_PWM:') else rows[n]['wire_owner']
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    try:
        for i,(n,s) in enumerate(wires.items()):
            for m,t in list(wires.items())[i+1:]:
                if owner(n)==owner(m) or tuple(sorted((n,m))) in reusable or not near(bounds[n],bounds[m],.2):continue
                if time.monotonic()-tick>150:raise TimeoutError('150s gate; completed pairs kept')
                gap=s.distToShape(t)[0];result['pairs']+=1
                r=dict(a=n,b=m,gap_mm=gap,minimum_mm=.2,group_a=rows[n]['group'],group_b=rows[m]['group'])
                result['completed_queries'].append(r)
                if gap<.2-1e-5:result['exact_wire_failures'].append(r)
                if result['pairs']%10==0:save()
            save()
        result['status']='SHARED_FAN_WIRE_GATE_REJECTED_NO_WORLD_GATE' if result['exact_wire_failures'] else 'SHARED_FAN_WIRE_GATE_CLEAR_WORLD_SCOPE_OPEN'
    except Exception as e:result['status']='PARTIAL_SHARED_FAN_GATE';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],pairs=result['pairs'],failures=len(result['exact_wire_failures']),
        errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
