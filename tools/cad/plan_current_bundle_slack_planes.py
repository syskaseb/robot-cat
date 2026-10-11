"""Bounded whole-loop plane allocation for four open constant-length looms.

Do not push60..83mm of motion into the crowded terminal fan-outs. Compare
three complete slack-loop planes, not repeated manual scalar offsets. This is
mathematical preparation only; no native clamp at a virtual join is implied.
"""
import json,copy,math,time
from pathlib import Path
from plan_current_moving_looms import ROOT,OUT,SHA,sub,norm,mul,metrics,curve_length
from plan_current_constant_bundle_sections import double_span

def compact(v):
    fields=('angles','start','flex_start','departure_parts_mm','transition_parts_mm',
            'return_parts_mm','spans_mm','flex_length_mm','body_arrival_axis_mm')
    return {k:copy.deepcopy(v[k]) for k in fields if k in v}

def dimensions(spans,dense=50):
    q=[metrics(s,dense) for s in spans]
    return sum(v[0] for v in q),min(v[1] for v in q)

def allocation(loom,channels):
    side=1 if loom['loom'][1]=='L' else -1
    planes=([0,0,1],[0,side,0],[1 if loom['loom'].startswith('R') else -1,0,0])
    budget=min(850-14-21-loom['initial_land_mm']-r['guide_mm'] for r in channels.values() if r['loom']==loom['loom'])
    attempts=[];best=None
    for outward in planes:
        for factor in (1/3,.5):
            catalog=[]
            for v in loom['poses']:
                original=v['spans_mm'][0];start=original[0];end=loom['body_dock_mm']
                axis=sub(original[1],start);axis=mul(axis,1/norm(axis))
                prefix=sum(q['length_mm'] for q in v['departure_parts_mm']);valid=[]
                for amp in range(0,121,10):
                    spans=double_span(start,axis,end,outward,amp,factor);length,radius=dimensions(spans)
                    if radius>=31 and prefix+length<=budget:valid.append((amp,prefix+length))
                if not valid:break
                catalog.append((v,start,axis,end,prefix,valid))
            if len(catalog)!=len(loom['poses']):
                attempts.append(dict(plane=outward,factor=factor,covered_poses=len(catalog)));continue
            lower=max(min(q[1] for q in row[-1]) for row in catalog)
            upper=min(max(q[1] for q in row[-1]) for row in catalog)
            attempts.append(dict(plane=outward,factor=factor,covered_poses=len(catalog),
                common_length_interval_mm=[lower,upper]))
            if upper<lower:continue
            target=lower+1e-4;poses=[]
            for v,start,axis,end,prefix,valid in catalog:
                chosen=None
                for (a,la),(b,lb) in zip(valid,valid[1:]):
                    if b-a>10 or not min(la,lb)<=target<=max(la,lb):continue
                    lo,hi=a,b
                    for _ in range(26):
                        amp=(lo+hi)/2;spans=double_span(start,axis,end,outward,amp,factor)
                        length=sum(curve_length(s) for s in spans)
                        if (prefix+length<target)==(lb>la):lo=amp
                        else:hi=amp
                    length,radius=dimensions(spans,200)
                    if radius>=31 and abs(prefix+length-target)<1e-4:
                        chosen=dict(compact(v),spans_mm=spans,flex_length_mm=prefix+length,
                            project_sampled_min_radius_mm=radius,slack_amplitude_mm=amp)
                        break
                if chosen is None:break
                poses.append(chosen)
            if len(poses)==len(loom['poses']):
                rank=target
                if best is None or rank<best[0]:best=(rank,target,poses,outward,factor)
    return best,attempts

def run():
    tick=time.monotonic();lf=OUT/'joined-leg-looms-plan.json';basis=json.loads(lf.read_text())
    cf=OUT/'leg-fanout-channels-plan.json';channels=json.loads(cf.read_text())
    previous=OUT/'constant-bundles-plan.json';receipt=json.loads(previous.read_text())
    # This is a new candidate, NOT re-labelling the rejected earlier report.
    # Recompute the individual eight stored mathematical families explicitly.
    old={r['loom']:r for r in receipt['looms']};looms=[];bad=[];attempts={}
    for row in basis['looms']:
        q={k:copy.deepcopy(row[k]) for k in ('loom','motion_stage','body_dock_mm','cores','initial_land_mm')}
        if row['loom'] in ('FL3','RL2','RL3','RR2'):
            selected,attempts[row['loom']]=allocation(row,channels['routes'])
            if selected:
                _,q['fixed_bundle_guide_mm'],q['poses'],q['slack_plane'],q['control_factor']=selected
            else:
                q['poses']=[compact(v) for v in row['poses']]
                bad.append(dict(loom=row['loom'],cause='NO_COMMON_CONSTANT_R31_LENGTH_IN_THREE_LOOP_PLANES'))
        else:
            q['fixed_bundle_guide_mm']=old[row['loom']]['fixed_bundle_guide_mm']
            q['poses']=[compact(v) for v in old[row['loom']]['poses']]
            for v in q['poses']:
                length=sum(curve_length(s) for s in v['spans_mm'])+sum(t['length_mm'] for key in ('departure_parts_mm','transition_parts_mm','return_parts_mm') for t in v.get(key,[]))
                assert abs(length-q['fixed_bundle_guide_mm'])<1e-4,(q['loom'],length)
                assert all(metrics(s,200)[1]>=31 for s in v['spans_mm'])
        looms.append(q);print('Whole slack plane',q['loom'],'fixed',q.get('fixed_bundle_guide_mm'),flush=True)
    result=dict(status='REJECTED_COMMON_BUNDLE_SLACK_PLANES' if bad else 'TWELVE_CONSTANT_BUNDLE_MATH_ONLY',
        looms=looms,rejected=bad,plane_attempts=attempts,worker_seconds=time.monotonic()-tick,
        selected=False,W5_complete=False,physical_pass=False,shared_nominal_material_motion_native_open=True,
        source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in (lf,cf,previous,Path(__file__),ROOT/'tools/cad/plan_current_moving_looms.py',ROOT/'tools/cad/plan_current_constant_bundle_sections.py')})
    (OUT/'bundle-slack-planes-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],rejected=bad,seconds=result['worker_seconds'])),flush=True)
    return result

if __name__=='__main__':run()
