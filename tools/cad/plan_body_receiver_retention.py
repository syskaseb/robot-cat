"""One shared allocation of independent receiver grips on received body routes.

Keeps routes/endpoints unchanged. Actual existing solids/wires and all twenty
new grips are considered together. Rooted arms and native export remain open.
"""
import argparse,itertools,json,math,subprocess,time
from pathlib import Path
import core_receiver_port as T
import check_near_axis_hip_sources as C
from plan_body_fanout_layout import AXES
from body_receiver_lands import candidates as earlier_lands
P=C.P


def land_for(row,route):
    part=(row['receiving_parts'][row['receiving_grip_part_index']]
          if 'receiving_parts' in row else row['receiving_land'])
    assert part['kind']=='line' and abs(part['length_mm']-9)<1e-6
    assert part in route['parts'],'Receiving land no longer on actual route'
    a,b=part['start'],part['end'];axis=[(y-x)/9 for x,y in zip(a,b)]
    return dict(id=row['wire']+'/Receiver',centre_world_mm=[(x+y)/2 for x,y in zip(a,b)],
        start_world_mm=a,end_world_mm=b,axis=axis,length_mm=9)


def run(resume_commit=None):
    tick=time.monotonic();file=P.OUT/'body-fanout-layout.json';plan=json.loads(file.read_text())
    previous=None
    if resume_commit:
        relative=(P.OUT/'body-receiver-retention-plan.json').relative_to(P.ROOT).as_posix()
        previous=json.loads(subprocess.check_output(['git','show',resume_commit+':'+relative],cwd=P.ROOT))
        for name,digest in previous['source_sha256'].items():
            if name!=Path(__file__).relative_to(P.ROOT).as_posix():assert P.SHA(P.ROOT/name)==digest,('Changed receiver baseline input',name)
    targets,old,pins=C.load();rows={r['wire']:r for r in plan['rows']}
    wires={n:P.wire(r['parts']) for n,r in plan['routes'].items()}
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'receiver-retention-pairs.json',bounds.near)
    candidates={};rejections=[];checks=0;last=time.monotonic()
    def hit(a,b,ra=0,rb=0):
        nonlocal checks,last
        if not bounds.near(a,b,ra+rb+.0001):return False
        checks+=1;gap,vol=cache.check(a,b,ra,rb)
        if time.monotonic()-last>20:cache.save();last=time.monotonic()
        return vol>1e-5 or ((ra or rb) and gap<ra+rb-1e-6)
    for name,route in plan['routes'].items():
        row=rows[name];choices=[]
        lands=([q for q in earlier_lands(row,route) if not q['primary_terminal_land']]
               if previous and previous['option_counts'][name]==0 else [land_for(row,route)])
        for land in lands:
            for normal in AXES:
                if abs(sum(a*b for a,b in zip(normal,land['axis'])))>1e-6:continue
                for offset in (0,-1.5,1.5):
                    profile=T.build(land,normal,offset);witness=None
                    goal=profile['arrival_world_mm'];seed=P.box([x-d for x,d in zip(goal,(2,2,2))]+[x+d for x,d in zip(goal,(2,2,2))])
                    if hit(seed,profile['band']):continue
                    for kind,shape in (('body',profile['body']),('band',profile['band']),('arm_seed',seed)):
                        for target,s in targets.items():
                            if hit(shape,s):witness=dict(kind=kind,target=target);break
                        if witness:break
                        for target,(w,r) in old.items():
                            if hit(shape,w,0,r+.25):witness=dict(kind=kind,target=target);break
                        if witness:break
                        for other,w in wires.items():
                            # Own tie intentionally tightens only its own core.
                            radius=1 if other==name and kind=='band' else 1.25
                            if hit(shape,w,0,radius):witness=dict(kind=kind,target='body/'+other);break
                        if witness:break
                    if witness:rejections.append(dict(wire=name,normal=normal,offset=offset,land=land,**witness));continue
                    choices.append(dict(normal=list(normal),offset=offset,land=land,profile=profile,seed=seed))
        candidates[name]=choices;cache.save()
        print('receiver options',name,len(choices),'pairs',checks,flush=True)
    selected={};nodes=0;deadline=time.monotonic()+60
    def solve():
        nonlocal nodes
        nodes+=1
        if time.monotonic()>deadline or nodes>20000:return False
        if len(selected)==len(candidates):return True
        domains={}
        for name,choices in candidates.items():
            if name in selected:continue
            domains[name]=[q for q in choices if all(not hit(a,b) for oldq in selected.values()
                for a in (q['profile']['body'],q['profile']['band'],q['seed'])
                for b in (oldq['profile']['body'],oldq['profile']['band'],oldq['seed']))]
        name=min(domains,key=lambda n:len(domains[n]))
        for choice in domains[name]:
            selected[name]=choice
            if solve():return True
            selected.pop(name)
        return False
    solved=solve()
    result=dict(status='RECEIVER20_JOINT_GRIP_ALLOCATIONS_CLEAR_ROOT_ARMS_NATIVE_OPEN' if solved else 'RECEIVER_SHARED_ALLOCATION_OPEN',
        grips={n:dict(land=q['land'],normal=q['normal'],offset=q['offset'],recipe=q['profile']['recipe'],arrival_world_mm=q['profile']['arrival_world_mm']) for n,q in selected.items()},
        qualified_options={n:[dict(land=q['land'],normal=q['normal'],offset=q['offset'],recipe=q['profile']['recipe'],arrival_world_mm=q['profile']['arrival_world_mm']) for q in choices] for n,choices in candidates.items()},
        option_counts={n:len(q) for n,q in candidates.items()},rejections=rejections,checks=checks,search_nodes=nodes,
        reused_exact_pairs=cache.reused,computed_exact_pairs=cache.computed,
        resume_commit=resume_commit,unchanged_baseline_inputs_verified=bool(previous),
        source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (file,Path(__file__),Path(T.__file__),Path(__file__).with_name('body_receiver_lands.py'))}},
        scope='Only20receivednonHip1bodyroutes. Independent9mmreceivergrips/tieenvelopes/armseeds, allretainedmaterial/wires andmutualallocation. Complete rootedarms/native/remaining16cores/19guides/stockW5 OPEN.',
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    cache.save();(P.OUT/'body-receiver-retention-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','checks','search_nodes','worker_seconds')}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume-commit')
    run(parser.parse_args().resume_commit)
