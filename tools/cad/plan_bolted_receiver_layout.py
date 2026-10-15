"""Shared22 receiver restraints; RR_G uses NC-side bolted cap, no Frame cuts.

Reuse unchanged positive domains; changed RR interface includes screw/nut/tool.
Nominal hardware reservations require stock identification and physical trials.
"""
import copy,itertools,json,time
from pathlib import Path
import FreeCAD as A
from build_front_fixed_port_clearance import placement
from low_profile_rail_pressure_bridge import build as triple
from plan_low_profile_receiver_space import material as original_material,land_for
from bolted_rail_pressure_bridge import build as bolted


def material(record):
    if record.get("retainer")!="M2_cap":return original_material(record)
    p=bolted(record["lands"],record["normal"],record["feeds"])
    p["seed"]=P.box([v-2 for v in p["arrival_world_mm"]]+[v+2 for v in p["arrival_world_mm"]])
    return p,{k:p[k] for k in ("body","cap","seed","screw","nut","access_tool")}
from plan_body36_receiver_space import shared_context,P,C,AXES
from csg_bore_clearance import prove as prove_bores


def run():
    tick=time.monotonic()
    files=[P.OUT/n for n in ('low-profile-receiver-space.json','body36-global-receiver-space.json',
        'body36-current-contract.json','retained-body-guides-inventory.json','fixed-native-retained-masks.json')]
    low,prior,contract,inventory,masks=[json.loads(p.read_text()) for p in files]
    for receipt in (low,prior,masks):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,wires,pins,_=shared_context();targets={n:s for n,s in targets.items() if not n.startswith('Receiver_')}
    rows={r['wire']:r for r in contract['rows']};domains={};chosen={};rejections=[];cut_receipts=[]
    checks=0;nodes=0;analytical=0;errors=[];bounds=C.ImmutableBounds()
    cache=C.AtomicMaterial(P.OUT/'bolted-receiver-layout-pairs.json',bounds.near);registry={};memo={}
    def hit(a,b,ra=0,rb=0):
        nonlocal checks,analytical
        if not bounds.near(a,b,ra+rb+.0001):return False
        if not ra and rb and id(a) in registry:
            recipe,kind=registry[id(a)]
            if prove_bores(recipe,kind,b,rb):analytical+=1;return False
        if ra and not rb and id(b) in registry:
            recipe,kind=registry[id(b)]
            if prove_bores(recipe,kind,a,ra):analytical+=1;return False
        if rb and not b.Solids and len(b.Edges)>1:return any(hit(a,e,ra,rb) for e in b.Edges)
        checks+=1
        try:gap,vol=cache.check(a,b,ra,rb)
        except RuntimeError as e:errors.append(str(e));return True
        return vol>1e-5 or ((ra or rb) and gap<ra+rb-1e-6)
    def hydrate(q,name):
        q=copy.deepcopy(q);profile,components=material(q)
        if q['kind']=='triple':
            for kind in ('body','cap'):registry[id(components[kind])]=(profile['recipe'],kind)
        q.update(profile=profile,components=components,identity=(name,len(domains.get(name,[]))),
            prefixes={r['wire']:P.wire(r['receiving_parts']) for r in q['rows']
                if r['wire'] in contract['remaining_wire_ids']})
        return q
    def serial(q):return {k:v for k,v in q.items() if k not in ('components','profile','prefixes','identity')}
    def save(status):
        pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files+[Path(__file__),
            Path(__file__).with_name('low_profile_rail_pressure_bridge.py'),
            Path(__file__).with_name('plan_low_profile_receiver_space.py'),
            Path(__file__).with_name('csg_bore_clearance.py'),Path(__file__).with_name('bolted_rail_pressure_bridge.py')]})
        result=dict(status=status,groups={n:serial(q) for n,q in chosen.items()},
            qualified_options={n:[serial(q) for q in d] for n,d in domains.items()},
            option_counts={n:len(d) for n,d in domains.items()},frame_passages=cut_receipts,
            rejections=rejections,errors=errors,checks=checks,analytical_proofs=analytical,
            search_nodes=nodes,worker_seconds=round(time.monotonic()-tick,3),source_sha256=pins,
            required_cores=36,physical_restraints=22,pressure_caps=7,T18I=21,M2x14=1,M2_nut=1,
            changed_wire_ids=contract['remaining_wire_ids'],replaced_wire_ids=[],
            selected=False,W5_complete=False,physical_pass=False,
            scope='Pinned unchanged domains plus RR bare-wall passage and three independent FL_G saddles; joint clearance only. Full middles, roots, native, stock and sample tightening remain open.')
        p=P.OUT/'bolted-receiver-layout.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(p);cache.save()
    # Removing only printed wall cannot invalidate positive collision domains.
    for name,options in low['qualified_options'].items():
        if name in ('RR_G','FL_G'):continue
        domains[name]=[]
        for q in options:domains[name].append(hydrate(q,name))
    for row in contract['rows']:
        if not row['receiver_role'].startswith('FL_G.'):continue
        name=row['wire'];domains[name]=[]
        for old in prior['qualified_options'][name]:
            if name not in contract['remaining_wire_ids']:
                prior_parts=old['row'].get('receiving_parts',[old['row']['receiving_land']])
                current_parts=row.get('receiving_parts',[row['receiving_land']])
                assert prior_parts==current_parts,name
            q=dict(kind='single',owner=old['owner'],land=old['land'],normal=old['normal'],
                offset=old['offset'],wires=[name],rows=[old['row']])
            domains[name].append(hydrate(q,name))
    group=[r for r in contract['rows'] if r['receiver_role'].startswith('RR_G.')]
    owner=group[0]['existing_fixed_support'];key=owner+'/0/0';original=targets[key]
    lands=[land_for(r) for r in group];centre=[sum(q['centre_world_mm'][i] for q in lands)/3 for i in range(3)]
    feeds=[]
    for wire,guide in inventory['guides'].items():
        if not any(role.split('.')[0]=='RR_G' for role in guide['electrical_roles']):continue
        for point in guide['source_endpoints_mm']:
            if abs(abs(point[0]-centre[0])-9.5)<1e-6 and abs(point[1]-centre[1])<1e-6:
                feeds.append(dict(wire=wire,point_world_mm=point,radius_mm=max(s['radius_mm'] for s in guide['segments'])))
    assert len(feeds)==1
    domains['RR_G']=[]
    for normal in ((0,1,0),(0,-1,0)):
        q=dict(kind='triple',retainer='M2_cap',owner=owner,lands=lands,normal=list(normal),wires=[r['wire'] for r in group],rows=group,feeds=feeds)
        q=hydrate(q,'RR_G');blocked=None
        for kind,s in q['components'].items():
            for n,t in targets.items():
                same=(n==key or n.startswith('Root/'+owner+'/') or n=='Source/'+owner+'/body/0')
                if kind in ('body','seed') and same:continue
                if hit(s,t):blocked=kind+':'+n;break
            if blocked:break
            for n,(w,r) in wires.items():
                if hit(s,w,0,r+.25):blocked=kind+':'+n;break
            if blocked:break
            for row in rows.values():
                if row['wire'] not in contract['remaining_wire_ids']:continue
                if hit(s,P.wire(row['receiving_parts']),0,1.25):blocked=kind+':prefix/'+row['wire'];break
            if blocked:break
        if blocked:rejections.append(dict(group='RR_G',normal=normal,target=blocked));print('RR bolt rejected',blocked,flush=True)
        else:domains['RR_G'].append(q);print('RR bolt clear',normal,flush=True)
        save('BOLTED_RECEIVER_PREFLIGHT_OPEN')
    assert len(domains)==22
    until=time.monotonic()+180
    def fits(q,p):
        k=tuple(sorted((q['identity'],p['identity'])))
        if k in memo:return memo[k]
        for ka,a in q['components'].items():
            for kb,b in p['components'].items():
                if q['owner']==p['owner'] and ka in ('body','seed') and kb in ('body','seed'):continue
                if hit(a,b):memo[k]=False;return False
        for a,b in ((q,p),(p,q)):
            for w in a['prefixes'].values():
                if any(hit(w,s,1.25) for s in b['components'].values()):memo[k]=False;return False
        for a in q['prefixes'].values():
            for b in p['prefixes'].values():
                if hit(a,b,1.25,1):memo[k]=False;return False
        memo[k]=True;return True
    def solve():
        nonlocal nodes
        nodes+=1
        if len(chosen)==22:return True
        if time.monotonic()>until or nodes>20000:return False
        available={n:[q for q in d if all(fits(q,p) for p in chosen.values())] for n,d in domains.items() if n not in chosen}
        name=min(available,key=lambda n:len(available[n]))
        for q in available[name]:
            chosen[name]=q
            if solve():return True
            chosen.pop(name)
        return False
    solved=not low['prefix_contacts'] and solve()
    save('BOLTED36_RECEIVER_LAYOUT_JOINT_CLEAR_MIDDLES_OPEN' if solved else 'BOLTED_RECEIVER_LAYOUT_OPEN')
    print('Mixed receiver joint result',solved,'nodes',nodes,'pairs',checks,'seconds',round(time.monotonic()-tick,3),flush=True)


if __name__=='__main__':run()
