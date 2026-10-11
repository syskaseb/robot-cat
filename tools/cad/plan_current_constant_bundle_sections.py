"""Keep motion slack in complete3core bundles, not crowded terminal fanouts.

Virtual split stations are NOT outboard hardware clamps or new printed wings.
All36 previously whole-screened nominal fanouts remain unchanged. Only the
ten variable bundle spans are reallocated; front Knee returns are retained.
"""
import copy,json,math,time
from pathlib import Path
from plan_current_moving_looms import ROOT,OUT,SHA,sub,norm,best_span,add,mul,dot,metrics

def double_span(start,axis,end,outward,amplitude,factor):
    mid=add(mul(add(start,end),.5),mul(outward,amplitude));direction=sub(end,start)
    direction=mul(direction,1/norm(direction));a=math.dist(start,mid)*factor;b=math.dist(mid,end)*factor
    return [[start,add(start,mul(axis,a)),add(mid,mul(direction,-a)),mid],
            [mid,add(mid,mul(direction,b)),add(end,[0,0,-b]),end]]

def metrics2(spans):
    q=[metrics(s,60) for s in spans]
    return sum(v[0] for v in q),min(v[1] for v in q)

def double_family(loom,channels):
    side=1 if loom['loom'][1]=='L' else -1
    outward=[0,side,0] if loom['loom'].endswith('1') else [(-1 if loom['loom'] in ('FL3','RR3') else 1),0,0]
    budget=min(850-14-21-loom['initial_land_mm']-r['guide_mm'] for r in channels['routes'].values() if r['loom']==loom['loom'])
    for factor in (1/3,.45,.6):
        catalog=[]
        for v in loom['poses']:
            original=v['spans_mm'][0];axis=sub(original[1],original[0]);axis=mul(axis,1/norm(axis))
            start,end=original[0],loom['body_dock_mm'];prefix=sum(q['length_mm'] for q in v['departure_parts_mm'])
            feasible=[]
            for amp in range(0,101,5):
                spans=double_span(start,axis,end,outward,amp,factor);length,radius=metrics2(spans)
                if radius>=31 and prefix+length<=budget:feasible.append((amp,prefix+length))
            if not feasible:break
            catalog.append((v,start,axis,end,prefix,feasible))
        if len(catalog)!=len(loom['poses']):continue
        target=max(min(q[1] for q in row[-1]) for row in catalog)+1e-4
        if target>min(max(q[1] for q in row[-1]) for row in catalog):continue
        poses=[]
        for v,start,axis,end,prefix,feasible in catalog:
            chosen=None
            for (a,la),(b,lb) in zip(feasible,feasible[1:]):
                if b-a>5 or not min(la,lb)<=target<=max(la,lb):continue
                lo,hi=a,b
                for _ in range(24):
                    amp=(lo+hi)/2;spans=double_span(start,axis,end,outward,amp,factor);length,radius=metrics2(spans)
                    if (prefix+length<target)==(lb>la):lo=amp
                    else:hi=amp
                if radius>=31 and abs(prefix+length-target)<1e-4:
                    chosen=dict(v,spans_mm=spans,flex_length_mm=prefix+length,
                        project_sampled_min_radius_mm=radius,whole_bundle_slack_amplitude_mm=amp)
                    break
            if chosen is None:break
            poses.append(chosen)
        if len(poses)==len(loom['poses']):return target,poses
    return None

def run():
    tick=time.monotonic();f=OUT/'joined-leg-looms-plan.json';basis=json.loads(f.read_text())
    cf=OUT/'leg-fanout-channels-plan.json';channels=json.loads(cf.read_text())
    sf=OUT/'leg-fanout-channels-screen.json';screen=json.loads(sf.read_text())
    assert screen['status']=='COMMON_NOMINAL_48_PATHS_PROXIMITY_ONLY'
    for source in (basis,channels,screen):
        for n,h in source['source_sha256'].items():assert SHA(ROOT/n)==h,n
    looms=copy.deepcopy(basis['looms']);bad=[]
    for loom in looms:
        if loom['loom'] in ('FL2','FR2'):
            loom['fixed_bundle_guide_mm']=loom['maximum_bundle_section_mm'];continue
        selected=None
        for gain in (0,10,30,60):
            target=loom['maximum_bundle_section_mm']+gain;poses=[];okay=True
            nominal=next(v for v in loom['poses'] if not any(v['angles']))
            if any(loom['initial_land_mm']+target+r['guide_mm']+14+21>850 for r in channels['routes'].values() if r['loom']==loom['loom']):continue
            for v in loom['poses']:
                prefix=sum(q['length_mm'] for q in v['departure_parts_mm']);original=v['spans_mm'][0]
                tangent=sub(original[1],original[0]);tangent=[x/norm(tangent) for x in tangent]
                span=best_span(original[0],tangent,loom['body_dock_mm'],[0,0,-1],target=target-prefix)
                if span is None:okay=False;break
                _,length,radius,bounds,poles=span
                assert abs(prefix+length-target)<1e-4 and radius>=31
                poses.append(dict(v,spans_mm=[poles],flex_length_mm=prefix+length,
                    project_sampled_min_radius_mm=radius,planned_bounds_mm=bounds))
            if okay:selected=(target,poses);break
        if selected is None:
            # One cubic has no extra lateral degree of freedom. The next
            # architecture is a whole two-span outboard slack bow, not a
            # different scalar length/tangent at the same failed interface.
            selected=double_family(loom,channels)
        if selected:
            loom['fixed_bundle_guide_mm'],loom['poses']=selected
            loom['body_fanout_routes_and_native_grips']='Static whole fanouts retained; actual material/shared motion/native OPEN'
            print('Constant whole bundle',loom['loom'],round(selected[0],3),flush=True)
        else:bad.append(dict(loom=loom['loom'],cause='NO_BOUNDED_R31_FIXED_BUNDLE_FAMILY_WITH_FACTORY_CAPACITY'))
    result=dict(status='REJECTED_CONSTANT_BUNDLE_FAMILIES' if bad else 'CONSTANT_12_BUNDLE_MATH_ONLY',
        looms=looms,rejected=bad,worker_seconds=time.monotonic()-tick,
        selected=False,W5_complete=False,physical_pass=False,
        scope='All36nominal terminal fanouts retained. Motion slack belongs to12whole factory3core bundles. Virtual joins NOT printed/clamped outsidebody. Real geometry/motion/native still OPEN.',
        source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in (f,cf,sf,Path(__file__),ROOT/'tools/cad/plan_current_moving_looms.py')})
    (OUT/'constant-bundles-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],rejected=bad,seconds=result['worker_seconds'])),flush=True)
    return result

if __name__=='__main__':run()
