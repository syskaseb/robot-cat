"""Twenty physical restraints for36 cores:8 triple bridges and12 singles.

Retain all20 received whole routes, including W073. Printed pressure caps
are retained by two off-row bands, not separate crowded6mm heads per core.
Loose prototype fit/tightening remains an explicit unpowered sample gate.
"""
import copy,itertools,json,math,time
from pathlib import Path
import core_receiver_port as T
from mapped_rail_pressure_bridge import build as triple
from csg_bore_clearance import prove as prove_bores
from plan_body36_receiver_space import shared_context,P,C,AXES
from check_body_fanout_material import mate_names,terminal_trim


def land_for(row):
    p=(row['receiving_parts'][row['receiving_grip_part_index']]
       if 'receiving_parts' in row else row['receiving_land'])
    a,b=p['start'],p['end'];assert abs(p['length_mm']-9)<1e-6
    return dict(id=row['wire']+'/Receiver',centre_world_mm=[(x+y)/2 for x,y in zip(a,b)],
        start_world_mm=a,end_world_mm=b,axis=[(y-x)/9 for x,y in zip(a,b)],length_mm=9)


def material(record):
    p=triple(record['lands'],record['normal'],record['feeds']) if record['kind']=='triple' else T.build(record['land'],record['normal'],record['offset'])
    p['seed']=P.box([v-2 for v in p['arrival_world_mm']]+[v+2 for v in p['arrival_world_mm']])
    components={'body':p['body'],'seed':p['seed']}
    if record['kind']=='triple':components.update(cap=p['cap'],band0=p['bands'][0],band1=p['bands'][1])
    else:components['band']=p['band']
    return p,components


def run():
    tick=time.monotonic();cf=P.OUT/'body36-current-contract.json';pf=P.OUT/'body36-global-receiver-space.json'
    contract,prior=[json.loads(f.read_text()) for f in (cf,pf)]
    inventoryfile=P.OUT/'retained-body-guides-inventory.json';inventory=json.loads(inventoryfile.read_text())['guides']
    for n,h in prior['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,wires,pins,unions=shared_context();targets={n:s for n,s in targets.items() if not n.startswith('Receiver_')}
    rows={r['wire']:r for r in contract['rows']};missing=set(contract['remaining_wire_ids']);domains={};prefixes={};prefix_contacts=[]
    for n,row in rows.items():
        if row['core']!='V' and n in missing:prefixes[n]=P.wire(row['receiving_parts'])
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'mapped-rail-receiver-space-pairs.json',bounds.near)
    checks=0;last=time.monotonic();edges={};failures=[];selected={};nodes=0;memo={};kernel_errors=[];analytic={};analytic_proofs=0
    def hit(a,b,ra=0,rb=0):
        nonlocal checks,last,analytic_proofs
        if not bounds.near(a,b,ra+rb+.0001):return False
        if rb and not ra and id(a) in analytic:
            _,recipe,kind=analytic[id(a)]
            if prove_bores(recipe,kind,b,rb):analytic_proofs+=1;return False
        if ra and not rb and id(b) in analytic:
            _,recipe,kind=analytic[id(b)]
            if prove_bores(recipe,kind,a,ra):analytic_proofs+=1;return False
        if rb and not b.Solids and len(b.Edges)>1:
            if id(b) not in edges:edges[id(b)]=(b,list(b.Edges))
            try:return any(hit(a,e,ra,rb) for e in edges[id(b)][1])
            except RuntimeError:pass # Retry the same exact geometry as a whole wire.
        checks+=1
        try:gap,vol=cache.check(a,b,ra,rb)
        except RuntimeError as error:
            kernel_errors.append(str(error));return True # Conservative option rejection, never acceptance.
        if time.monotonic()-last>20:cache.save();last=time.monotonic()
        return vol>1e-5 or ((ra or rb) and gap<ra+rb-1e-6)
    def printed_owner(n):
        if n.startswith('Root/'):return n.split('/')[1]
        if n.startswith('Source/') and n.split('/')[2]=='body':return n.split('/')[1]
        return n.split('/')[0]
    def clear(s,row,kind,radius=0):
        mouth=P.wire(terminal_trim(row['receiving_parts'])) if radius else None
        for n,t in targets.items():
            if kind in ('body','seed') and printed_owner(n)==row['existing_fixed_support']:continue
            q=mouth if radius and n.split('/')[0] in mate_names(row) else s
            if hit(q,t,radius):return n
        for n,(w,r) in wires.items():
            if hit(s,w,radius,r if radius else r+.25):return n
        return None
    for name,wire in prefixes.items():
        witness=clear(wire,rows[name],'prefix',1.25)
        if witness:prefix_contacts.append(dict(wire=name,target=witness))
    for (a,s),(b,t) in itertools.combinations(prefixes.items(),2):
        if hit(s,t,1.25,1):prefix_contacts.append(dict(wire=a,target=b))
    rails={}
    for row in rows.values():
        if row['core']!='V':rails.setdefault(row['receiver_role'].split('.')[0],[]).append(row)
    assert len(rails)==8 and all(len(v)==3 for v in rails.values())
    def serial(q):return {k:v for k,v in q.items() if k not in ('components','profile','prefixes','identity')}
    def save(status='PARTIAL_GROUPED_RECEIVER_SPACE'):
        result=dict(status=status,groups={n:serial(q) for n,q in selected.items()},
            qualified_options={n:[serial(q) for q in d] for n,d in domains.items()},
            option_counts={n:len(d) for n,d in domains.items()},prefix_contacts=prefix_contacts,
            failures=failures,kernel_errors=kernel_errors,analytical_clearance_proofs=analytic_proofs,checks=checks,search_nodes=nodes,worker_seconds=round(time.monotonic()-tick,3),
            inherited_routes=20,changed_wire_ids=contract['remaining_wire_ids'],replaced_wire_ids=[],
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in
                (cf,pf,inventoryfile,Path(__file__),Path(__file__).with_name('mapped_rail_pressure_bridge.py'),Path(__file__).with_name('csg_bore_clearance.py'))}},
            required_cores=36,physical_restraints=20,pressure_caps=8,T18I=28,selected=False,W5_complete=False,physical_pass=False,
            physical_insulation_measurement_tightening_creep_gate_open=True)
        out=P.OUT/'mapped-rail-receiver-space.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save()
    for rail,group in rails.items():
        lands=[land_for(row) for row in group];options=[];owner=group[0]['existing_fixed_support']
        centre=[sum(q['centre_world_mm'][i] for q in lands)/3 for i in range(3)]
        feed_matches=[]
        for wire,guide in inventory.items():
            if not any(role.split('.')[0]==rail for role in guide['electrical_roles']):continue
            for point in guide['source_endpoints_mm']:
                if abs(abs(point[0]-centre[0])-9.5)<1e-6 and abs(point[1]-centre[1])<1e-6 and abs(abs(point[2]-centre[2])-4.5)<1e-6:feed_matches.append(dict(wire=wire,point_world_mm=point,radius_mm=max(segment['radius_mm'] for segment in guide['segments'])))
        assert 1<=len(feed_matches)<=2,(rail,feed_matches)
        assert len({tuple(q['point_world_mm']) for q in feed_matches})==len(feed_matches)
        print('actual rail feeds',rail,[(q['wire'],q['radius_mm']) for q in feed_matches],flush=True)
        assert all(row['existing_fixed_support']==owner for row in group)
        span=[lands[1]['centre_world_mm'][i]-lands[0]['centre_world_mm'][i] for i in range(3)]
        for normal in AXES:
            if abs(sum(a*b for a,b in zip(normal,lands[0]['axis'])))>1e-6 or abs(sum(a*b for a,b in zip(normal,span)))>1e-6:continue
            record=dict(kind='triple',owner=owner,lands=lands,normal=list(normal),wires=[r['wire'] for r in group],rows=group,
                feeds=feed_matches)
            profile,components=material(record);witness=None
            for kind in ('body','cap'):analytic[id(components[kind])]=(components[kind],profile['recipe'],kind)
            for kind,s in components.items():
                witness=clear(s,group[0],kind)
                if witness:break
                for name,wire in prefixes.items():
                    if hit(s,wire,0,1.25):witness='prefix/'+name;break
                if witness:break
            if witness:failures.append(dict(group=rail,normal=normal,target=witness,kind=kind));continue
            record.update(recipe=profile['recipe'],arrival_world_mm=profile['arrival_world_mm'],profile=profile,
                components=components,prefixes={n:prefixes[n] for n in record['wires'] if n in prefixes},identity=(rail,len(options)))
            options.append(record)
        domains[rail]=options;save();print('grouped rail',rail,'options',len(options),'pairs',checks,flush=True)
    for name,row in rows.items():
        if row['core']!='V':continue
        options=[]
        for old in prior['qualified_options'][name]:
            record=dict(kind='single',owner=old['owner'],land=old['land'],normal=old['normal'],offset=old['offset'],wires=[name],rows=[old['row']])
            profile,components=material(record)
            record.update(recipe=profile['recipe'],arrival_world_mm=profile['arrival_world_mm'],profile=profile,components=components,
                prefixes={name:P.wire(old['row']['receiving_parts'])} if name in missing else {},identity=(name,len(options)))
            options.append(record)
        domains[name]=options
    until=time.monotonic()+180
    def fits(q,p):
        key=tuple(sorted((q['identity'],p['identity'])))
        if key in memo:return memo[key]
        for ka,a in q['components'].items():
            for kb,b in p['components'].items():
                if q['owner']==p['owner'] and ka in ('body','seed') and kb in ('body','seed'):continue
                if hit(a,b):memo[key]=False;return False
        for a,b in ((q,p),(p,q)):
            for wire in a['prefixes'].values():
                if any(hit(wire,s,1.25) for s in b['components'].values()):memo[key]=False;return False
        for a in q['prefixes'].values():
            for b in p['prefixes'].values():
                if hit(a,b,1.25,1):memo[key]=False;return False
        memo[key]=True;return True
    def solve():
        nonlocal nodes
        nodes+=1
        if len(selected)==20:return True
        if time.monotonic()>until or nodes>20000:return False
        available={n:[q for q in d if all(fits(q,p) for p in selected.values())] for n,d in domains.items() if n not in selected}
        name=min(available,key=lambda n:len(available[n]))
        for q in available[name]:
            selected[name]=q
            if solve():return True
            selected.pop(name)
        return False
    solved=not prefix_contacts and solve()
    save('GROUPED36_RECEIVER_LAYOUT_JOINT_CLEAR_MIDDLES_OPEN' if solved else 'GROUPED_RECEIVER_SHARED_LAYOUT_OPEN')
    print('grouped receiver set',solved,'seconds',round(time.monotonic()-tick,3),flush=True)


if __name__=='__main__':run()
