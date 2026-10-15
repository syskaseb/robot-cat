"""Joint36 receiver allocation; received20 routes stay geometrically fixed.

Change the cause of conflicts: allow qualified old grip orientations to join
one shared solve, instead of treating the first20 picks as fixed obstacles.
"""
from plan_body36_receiver_space import *


def run():
    tick=time.monotonic();contractfile=P.OUT/'body36-current-contract.json'
    plan=json.loads(contractfile.read_text());targets,wires,pins,unions=shared_context()
    # Existing20 grip geometries enter domains, not immovable obstacles.
    targets={n:s for n,s in targets.items() if not n.startswith('Receiver_')}
    oldrecords=json.loads((P.OUT/'body-receiver-retention-plan.json').read_text())['qualified_options']
    chosen=json.loads((P.OUT/'receiver-relief-approach-plan.json').read_text())['grips']
    current=json.loads((P.OUT/'body-receiver-relief-layout.json').read_text())
    partialfile=P.OUT/'body36-receiver-space.json';partial=json.loads(partialfile.read_text())
    for n,h in partial['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    for file in (partialfile,P.OUT/'body-receiver-retention-plan.json',
                 P.OUT/'receiver-relief-approach-plan.json',P.OUT/'body-receiver-relief-layout.json',
                 Path(__file__).with_name('plan_body36_receiver_space.py'),Path(T.__file__)):
        pins[file.relative_to(P.ROOT).as_posix()]=P.SHA(file)
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'body36-global-receiver-pairs.json',bounds.near)
    edges={};checks=0;last=time.monotonic();domains={};failures=[];selected={};nodes=0
    def hit(a,b,ra=0,rb=0):
        nonlocal checks,last
        if not bounds.near(a,b,ra+rb+.0001):return False
        # Exact minimum to a wire is the minimum over its actual edges. The
        # broad phase only removes edges whose bounding boxes cannot be close.
        if rb and not b.Solids and len(b.Edges)>1:
            if id(b) not in edges:edges[id(b)]=(b,list(b.Edges))
            return any(hit(a,e,ra,rb) for e in edges[id(b)][1])
        checks+=1;gap,vol=cache.check(a,b,ra,rb)
        if time.monotonic()-last>20:cache.save();last=time.monotonic()
        return vol>1e-5 or ((ra or rb) and gap<ra+rb-1e-6)
    def printed_owner(name):
        if name.startswith('Receiver_') and name.split('/')[-1] in ('body','seed'):
            return unions[name.split('/')[0].removeprefix('Receiver_')]
        if name.startswith('Root/'):return name.split('/')[1]
        if name.startswith('Source/') and name.split('/')[2]=='body':return name.split('/')[1]
        return name.split('/')[0]
    def environment(s,row,kind,wire_radius=0,terminal=False):
        for name,t in targets.items():
            if kind in ('body','seed') and printed_owner(name)==row['existing_fixed_support']:continue
            q=P.wire(terminal_trim(row['receiving_parts'])) if terminal and name.split('/')[0] in mate_names(row) else s
            if hit(q,t,wire_radius):return name
        for name,(w,r) in wires.items():
            required=r if wire_radius else r+.25
            if name=='body/'+row['wire'] and kind=='band':required=1
            if hit(s,w,wire_radius,required):return name
        return None
    def pack(q):
        return {k:v for k,v in q.items() if k not in ('profile','seed','wire')}
    def save(status='PARTIAL_BODY36_RECEIVER_SPACE'):
        result=dict(status=status,qualified_options={n:[pack(q) for q in d] for n,d in domains.items()},
            grips={n:pack(q) for n,q in selected.items()},option_counts={n:len(d) for n,d in domains.items()},
            retained_routes=20,retained_grips=20,remaining_required=16,checks=checks,search_nodes=nodes,
            failures=failures,source_sha256={**pins,contractfile.relative_to(P.ROOT).as_posix():P.SHA(contractfile),
                Path(__file__).relative_to(P.ROOT).as_posix():P.SHA(Path(__file__))},
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            scope='All36 grip domains jointly with16 changed prefixes and20 retained routes,4sources/12fans/8rootedarms. No old grip obstacle waiver: chosen grip material is pair checked by CSP. Native/middle16/stock OPEN.')
        out=P.OUT/'body36-global-receiver-space.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save()
    for original in plan['rows']:
        name=original['wire']
        if name in plan['remaining_wire_ids'] and partial['qualified_options'].get(name):
            # These positives passed a STRICTER scene with20 old grips fixed.
            # Removing those grip obstacles cannot invalidate the static gate;
            # new mutual choices remain checked by the36-domain solve below.
            options=[]
            for record in partial['qualified_options'][name]:
                q=copy.deepcopy(record);profile=T.build(q['land'],q['normal'],q['offset'])
                goal=profile['arrival_world_mm']
                q.update(profile=profile,seed=P.box([v-2 for v in goal]+[v+2 for v in goal]),
                         wire=P.wire(q['row']['receiving_parts']))
                options.append(q)
            domains[name]=options;save();print('reused stricter receiver domain',name,len(options),flush=True);continue
        if name not in plan['remaining_wire_ids']:
            records=[chosen[name]]+[q for q in oldrecords[name] if q['land']==chosen[name]['land']]
            options=[];seen=set();wire=P.wire(current['routes'][name]['parts'])
            for record in records:
                key=(tuple(record['normal']),record['offset'])
                if key in seen:continue
                seen.add(key);profile=T.build(record['land'],record['normal'],record['offset'])
                goal=profile['arrival_world_mm'];seed=P.box([v-2 for v in goal]+[v+2 for v in goal])
                witness='own_band' if hit(seed,profile['band']) else None
                for kind,s in (('body',profile['body']),('band',profile['band']),('seed',seed)):
                    if witness:break
                    witness=environment(s,original,kind)
                if witness:continue
                options.append(dict(row=original,land=record['land'],normal=record['normal'],offset=record['offset'],
                    owner=original['existing_fixed_support'],method='retained_route_joint_grip_domain',
                    profile=profile,seed=seed,wire=wire,recipe=profile['recipe'],arrival_world_mm=goal))
            domains[name]=options;save();print('global retained receiver',name,len(options),checks,flush=True);continue
        options=[]
        for row,method in prefixes(original):
            wire=P.wire(row['receiving_parts']);witness=environment(wire,row,'approach',1.25,True)
            if witness:
                failures.append(dict(wire=name,method=method,kind='prefix',target=witness));continue
            part=row['receiving_parts'][row['receiving_grip_part_index']]
            a,b=part['start'],part['end'];axis=[(y-x)/9 for x,y in zip(a,b)]
            land=dict(id=name+'/Receiver',centre_world_mm=[(x+y)/2 for x,y in zip(a,b)],start_world_mm=a,end_world_mm=b,axis=axis,length_mm=9)
            for normal,offset in itertools.product(AXES,(0,-1.5,1.5)):
                if abs(sum(a*b for a,b in zip(normal,axis)))>1e-8:continue
                profile=T.build(land,normal,offset);goal=profile['arrival_world_mm'];seed=P.box([v-2 for v in goal]+[v+2 for v in goal])
                witness='own_band' if hit(seed,profile['band']) else None
                for kind,s in (('body',profile['body']),('band',profile['band']),('seed',seed)):
                    if witness:break
                    witness=environment(s,row,kind)
                    if not witness and hit(s,wire,0,1 if kind=='band' else 1.25):witness='own_prefix'
                if witness:continue
                options.append(dict(row=row,land=land,normal=list(normal),offset=offset,owner=row['existing_fixed_support'],
                    method=method,profile=profile,seed=seed,wire=wire,recipe=profile['recipe'],arrival_world_mm=goal))
            # Keep a small qualified domain rather than generate all variants.
            if len(options)>=6:break
        domains[name]=options;save();print('body36 receiver',name,'options',len(options),'pairs',checks,flush=True)
    def fits(q,p):
        for ka,a in (('body',q['profile']['body']),('band',q['profile']['band']),('seed',q['seed'])):
            for kb,b in (('body',p['profile']['body']),('band',p['profile']['band']),('seed',p['seed'])):
                if q['owner']==p['owner'] and ka!='band' and kb!='band':continue
                if hit(a,b):return False
        if hit(q['wire'],p['wire'],1.25,1):return False
        for a,b in ((q,p),(p,q)):
            if any(hit(s,a['wire'],0,1.25) for s in (b['profile']['body'],b['profile']['band'],b['seed'])):return False
        return True
    until=time.monotonic()+60
    def solve():
        nonlocal nodes
        nodes+=1
        if len(selected)==36:return True
        if time.monotonic()>until or nodes>20000:return False
        available={n:[q for q in d if all(fits(q,p) for p in selected.values())] for n,d in domains.items() if n not in selected}
        name=min(available,key=lambda n:len(available[n]))
        for q in available[name]:
            selected[name]=q
            if solve():return True
            selected.pop(name)
        return False
    solved=solve();save('GLOBAL36_RECEIVER_PREFIX_GRIPS_JOINT_CLEAR_16MIDDLES_OPEN' if solved else 'BODY36_RECEIVER_SHARED_ALLOCATION_OPEN')
    print('body36 receiver shared',solved,'seconds',round(time.monotonic()-tick,3),flush=True)


if __name__=='__main__':run()
