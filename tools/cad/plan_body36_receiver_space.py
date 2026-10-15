"""Remaining16 receiver prefixes/full grips in the received shared scene.

Reuses20 accepted routes/grips and8 rooted source arms. Only same physical
printed Frame bodies/seeds may union; bands, wires and bought parts never do.
This is a spatial plan, not native selection, stock approval or physical PASS.
"""
import copy,itertools,json,math,time
from pathlib import Path
import core_receiver_port as T
import check_near_axis_hip_sources as C
from current_axial_receiver_material import prepare_context
from plan_axial_source_supports import arm_box
from plan_body_fanout_layout import AXES,reverse_part
from plan_current_moving_looms import add,mul,exact_quarter
from plan_current_mta_interfaces import line
from check_body_fanout_material import mate_names,terminal_trim
P=C.P


def shared_context():
    sourcefile=P.OUT/'body-axial-layout-chosen.json'
    rootfile=P.OUT/'body-axial-rooted-arms-plan.json'
    source,roots=[json.loads(f.read_text()) for f in (sourcefile,rootfile)]
    assert roots['status']=='EIGHT_ROOTED_SOURCE_ARMS_EXACT_SEGMENTS_CLEAR_UNION_NATIVE_OPEN'
    for n,h in roots['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,wires,pins,family,axes,own,bare,files,subsets=prepare_context(source)
    unions={n:q['owner'] for n,q in json.loads((P.OUT/'receiver-relief-approach-plan.json').read_text())['grips'].items()}
    for row in source['hips']:
        code=row['cad_code'];leg=row['physical_leg']
        for moving in (False,True):
            _,profile=C.make_port(row,moving)
            owner=leg+('HipExtension' if moving else 'FixedCarrier')
            for kind in ('body','band'):
                for h in C.ANGLES if moving else (0,):
                    s=C.moved(profile[kind],C.transform(axes,code,h,0,'Hip')) if moving else profile[kind]
                    targets['Source/'+owner+'/'+kind+'/'+str(h)]=s
        for pose in row['poses']:
            h=pose['angle']
            if h in C.ANGLES:
                wires['chosen/'+row['loom']+'/'+str(h)]=(P.wire(pose['parts']+C.B.moved_parts(row['source_parts'],row['source'],h,0,axes)),3)
        for core in row['source_fans']:wires['fan/'+row['loom']+'/'+core['core']]=(P.wire(core['parts']),1)
    for row in roots['groups']:
        for i,(a,b) in enumerate(zip(row['paths'][0]['points_mm'],row['paths'][0]['points_mm'][1:])):
            for h in C.ANGLES if row['moving'] else (0,):
                s=arm_box(a,b,row['arm_half_widths_world_mm'])
                if row['moving']:s=C.moved(s,C.transform(axes,row['code'],h,0,'Hip'))
                targets['Root/'+row['name']+'/'+str(i)+'/'+str(h)]=s
    return targets,wires,{**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[sourcefile,rootfile]}},unions


def prefixes(row):
    yield copy.deepcopy(row),'received_prefix'
    end=row['receiver_point_mm'];last=row['receiving_parts'][-1]
    axis=[(a-b)/last['length_mm'] for a,b in zip(last['start'],last['end'])]
    for entry_mm,direction in itertools.product((9,3),AXES):
        if abs(sum(a*b for a,b in zip(axis,direction)))>1e-8:continue
        entry=line(end,add(end,mul(axis,entry_mm)))
        arc=exact_quarter(entry['end'],axis,direction,10)
        land=line(arc['end'],add(arc['end'],mul(direction,9)))
        for departure in AXES:
            if abs(sum(a*b for a,b in zip(direction,departure)))>1e-8:continue
            exitpart=exact_quarter(land['end'],direction,departure,10)
            parts=[reverse_part(p) for p in reversed([entry,arc,land,exitpart])]
            yield dict(row,receiving_parts=parts,receiving_land=parts[1],receiving_grip_part_index=1,
                free_end=parts[0]['start'],receiver_outward_axis=list(departure)), 'full_land_after_turn'


def run():
    tick=time.monotonic();contractfile=P.OUT/'body36-current-contract.json'
    plan=json.loads(contractfile.read_text());targets,wires,pins,unions=shared_context()
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'body36-receiver-space-pairs.json',bounds.near)
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
            if hit(s,w,wire_radius,r if wire_radius else r+.25):return name
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
            scope='Remaining16prefixes/fullgrips vs current20routes/grips,4sources/12fans/8rootedarms, retainedmaterial; middle16/rootedreceiverarms/native/stock OPEN.')
        out=P.OUT/'body36-receiver-space.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save()
    for original in plan['rows']:
        name=original['wire']
        if name not in plan['remaining_wire_ids']:continue
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
        if len(selected)==16:return True
        if time.monotonic()>until or nodes>20000:return False
        available={n:[q for q in d if all(fits(q,p) for p in selected.values())] for n,d in domains.items() if n not in selected}
        name=min(available,key=lambda n:len(available[n]))
        for q in available[name]:
            selected[name]=q
            if solve():return True
            selected.pop(name)
        return False
    solved=solve();save('BODY36_RECEIVER_PREFIX_GRIPS_JOINT_CLEAR_16MIDDLES_OPEN' if solved else 'BODY36_RECEIVER_SHARED_ALLOCATION_OPEN')
    print('body36 receiver shared',solved,'seconds',round(time.monotonic()-tick,3),flush=True)


if __name__=='__main__':run()
