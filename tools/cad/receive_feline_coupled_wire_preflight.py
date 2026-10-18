"""Receive frozen shared snapshot: reject self-crossing wires BEFORE world CAD."""
import json
import time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from check_feline_all_current_lands import near


def main():
    tick=time.monotonic();src=OUT/'n01-coupled-allocation-snapshot.json'
    dest=OUT/'n01-coupled-wire-preflight.json';assert not dest.exists()
    p,shapes,rows=packed(src)
    for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
    wires={n:s for n,s in shapes.items() if rows[n].get('wire_owner')}
    def owner(n):
        if n.startswith('F_PWM:'):return 'F_PWM.'+n.split(':')[1].split('_')[0]
        return rows[n]['wire_owner']
    bounds={n:s.BoundBox for n,s in wires.items()}
    result=dict(status='RUNNING_SHARED_WIRE_PROFILE_PREFLIGHT',selected=False,N01_complete=False,physical_pass=False,
        exact_wire_failures=[],completed_queries=[],errors=[],pairs=0,
        source_sha256={src.relative_to(ROOT).as_posix():sha(src),(ROOT/p['bundle']).relative_to(ROOT).as_posix():p['bundle_sha256'],
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        full_world_outline_motion_mounts_not_run=True)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    try:
        for i,(n,s) in enumerate(wires.items()):
            for m,t in list(wires.items())[i+1:]:
                if owner(n)==owner(m) or not near(bounds[n],bounds[m],.2):continue
                if time.monotonic()-tick>150:raise TimeoutError('150s preflight, keep completed results')
                gap=s.distToShape(t)[0];result['pairs']+=1
                row=dict(a=n,b=m,gap_mm=gap,required_mm=.2,group_a=rows[n]['group'],group_b=rows[m]['group'])
                result['completed_queries'].append(row)
                if gap<.2-1e-5:result['exact_wire_failures'].append(row)
                if result['pairs']%10==0:save()
            save()
        result['status']='SHARED_PROFILE_PREFLIGHT_REJECTED_NO_WORLD_GATE' if result['exact_wire_failures'] else 'SHARED_PROFILE_PREFLIGHT_CLEAR_WORLD_GATE_OPEN'
    except Exception as e:result['status']='PARTIAL_SHARED_PROFILE_PREFLIGHT';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],pairs=result['pairs'],failures=len(result['exact_wire_failures']),
        errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
