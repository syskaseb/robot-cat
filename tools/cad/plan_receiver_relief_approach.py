"""Allocate the W024 approach AND full clamp before routing its middle.

Nineteen unchanged wire routes/qualified receiver domains are retained. One
shared twenty-grip solve includes the changed approach, seats, bands and arm
seeds. It does not qualify the absent W024 middle or native/rooted supports.
"""
import copy,itertools,json,math,time
from pathlib import Path
import core_receiver_port as T
import check_near_axis_hip_sources as C
from check_body_fanout_material import mate_names,terminal_trim
from plan_body_fanout_layout import AXES,reverse_part
from plan_current_moving_looms import add,mul,exact_quarter
from plan_current_mta_interfaces import line
P=C.P


def run():
    tick=time.monotonic();file=P.OUT/'body-fanout-layout.json';baseline=P.OUT/'body-receiver-retention-plan.json'
    plan,receipt=[json.loads(f.read_text()) for f in (file,baseline)]
    for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    rows={r['wire']:r for r in plan['rows']};row=copy.deepcopy(rows['W024'])
    targets,old,pins=C.load()
    for name,r in plan['routes'].items():
        if name!='W024':old['body/'+name]=(P.wire(r['parts']),1)
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'receiver-relief-approach-pairs.json',bounds.near)
    checks=0;failures=[];last=time.monotonic()
    def hit(s,t,rs=0,rt=0):
        nonlocal checks,last
        if not bounds.near(s,t,rs+rt+.0001):return False
        checks+=1;gap,vol=cache.check(s,t,rs,rt)
        if time.monotonic()-last>20:cache.save();last=time.monotonic()
        return vol>1e-5 or ((rs or rt) and gap<rs+rt-1e-6)
    def clear(shape,radius=0,terminal=False):
        for name,s in targets.items():
            q=shape
            if terminal and name.split('/')[0] in mate_names(row):q=trimmed
            if hit(q,s,radius):return name
        for name,(w,r) in old.items():
            if hit(shape,w,radius,r+.25 if not radius else r):return name
        return None
    domains={}
    for name,options in receipt['qualified_options'].items():
        if name=='W024':continue
        domains[name]=[]
        for record in options:
            q=copy.deepcopy(record);profile=T.build(q['land'],q['normal'],q['offset']);goal=profile['arrival_world_mm']
            q.update(profile=profile,seed=P.box([v-2 for v in goal]+[v+2 for v in goal]),owner=rows[name]['existing_fixed_support'])
            domains[name].append(q)
    options=[];end=row['receiver_point_mm'];lastpart=plan['routes']['W024']['parts'][-1]
    axis=[(a-b)/lastpart['length_mm'] for a,b in zip(lastpart['start'],lastpart['end'])]
    side=1 if end[1]>0 else -1
    for entry_mm,direction in itertools.product((9,3),((0,-side,0),(1,0,0),(-1,0,0))):
        if abs(sum(a*b for a,b in zip(axis,direction)))>1e-8:continue
        entry=line(end,add(end,mul(axis,entry_mm)));arc=exact_quarter(entry['end'],axis,direction,10)
        landpart=line(arc['end'],add(arc['end'],mul(direction,9)))
        land=dict(id='W024/Receiver',centre_world_mm=[(a+b)/2 for a,b in zip(landpart['start'],landpart['end'])],
            start_world_mm=landpart['end'],end_world_mm=landpart['start'],axis=[-v for v in direction],length_mm=9)
        for departure in AXES:
            if abs(sum(a*b for a,b in zip(direction,departure)))>1e-8:continue
            exitpart=exact_quarter(landpart['end'],direction,departure,10)
            parts=[reverse_part(p) for p in reversed([entry,arc,landpart,exitpart])]
            wire=P.wire(parts);trimmed=P.wire(terminal_trim(parts))
            witness=clear(wire,1.25,True)
            if witness:failures.append(dict(entry_mm=entry_mm,direction=direction,departure=departure,kind='approach',target=witness));continue
            for normal in AXES:
                if abs(sum(a*b for a,b in zip(normal,land['axis'])))>1e-8:continue
                for offset in (0,-1.5,1.5):
                    profile=T.build(land,normal,offset);goal=profile['arrival_world_mm'];seed=P.box([v-2 for v in goal]+[v+2 for v in goal])
                    witness=None
                    if hit(seed,profile['band']):continue
                    for kind,s in (('body',profile['body']),('band',profile['band']),('arm_seed',seed)):
                        witness=clear(s)
                        if not witness and hit(s,wire,0,1 if kind=='band' else 1.25):witness='own_approach'
                        if witness:break
                    if witness:failures.append(dict(entry_mm=entry_mm,direction=direction,departure=departure,kind=kind,target=witness));continue
                    changed=dict(row,receiving_parts=parts,receiving_grip_part_index=1,
                        receiving_land=parts[1],receiver_profile='independent_land_after_turn_with_full_grip',
                        entry_straight_project_mm=entry_mm,free_end=parts[0]['start'],receiver_outward_axis=list(departure))
                    options.append(dict(land=land,normal=list(normal),offset=offset,profile=profile,seed=seed,
                        owner=row['existing_fixed_support'],row=changed,approach=wire))
        print('receiver relief prefix',entry_mm,direction,'options',len(options),'pairs',checks,flush=True)
    domains['W024']=options;selected={};nodes=0;until=time.monotonic()+60
    def fits(q,p):
        for ka,a in (('body',q['profile']['body']),('band',q['profile']['band']),('seed',q['seed'])):
            for kb,b in (('body',p['profile']['body']),('band',p['profile']['band']),('seed',p['seed'])):
                if q['owner']==p['owner'] and ka!='band' and kb!='band':continue # Same physical native part union; no band/wire waiver.
                if hit(a,b):return False
        for q,p in ((q,p),(p,q)):
            if 'approach' in q and any(hit(q['approach'],s,1.25) for s in (p['profile']['body'],p['profile']['band'],p['seed'])):return False
        return True
    def solve():
        nonlocal nodes
        nodes+=1
        if time.monotonic()>until or nodes>20000:return False
        if len(selected)==20:return True
        available={n:[q for q in d if all(fits(q,p) for p in selected.values())] for n,d in domains.items() if n not in selected}
        name=min(available,key=lambda n:len(available[n]))
        for q in available[name]:
            selected[name]=q
            if solve():return True
            selected.pop(name)
        return False
    solved=solve()
    def serial(q):
        result=dict(land=q['land'],normal=q['normal'],offset=q['offset'],owner=q['owner'],recipe=q['profile']['recipe'],arrival_world_mm=q['profile']['arrival_world_mm'])
        if 'row' in q:result['row']=q['row']
        return result
    result=dict(status='JOINT20_RECEIVER_GRIPS_AND_W024_PREFIX_CLEAR_MIDDLE_ROOT_ARMS_NATIVE_OPEN' if solved else 'RECEIVER_RELIEF_SHARED_PLAN_OPEN',
        grips={n:serial(q) for n,q in selected.items()},W024_options=[serial(q) for q in options],
        failures=failures,checks=checks,search_nodes=nodes,option_counts={n:len(d) for n,d in domains.items()},
        inherited_receiver_domains_commit='ffead52',source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (file,baseline,Path(__file__),Path(T.__file__))}},
        scope='ActualchangedW024prefix/completegrip andtwentyjointgripdomains. Existing19wholebodycurves unchanged; obsoleteW024middle omitted only for its own replacement. NewwholeW024route/rootedarms/native/stockW5 OPEN.',
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    out=P.OUT/'receiver-relief-approach-plan.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save()
    print(json.dumps({k:result[k] for k in ('status','checks','search_nodes','worker_seconds','option_counts')}),flush=True)


if __name__=='__main__':run()
