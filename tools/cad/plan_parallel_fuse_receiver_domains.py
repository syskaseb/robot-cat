"""Allocate FL1/FL2 fuse exits parallel to the retained FL3 exit.

Old bounded domains chose opposing X-directed lands one millimetre apart.
Use the actual30mm fuse pitch: all three insulation lands point along+Y at
Y40.5, with their own X preserved. No terminal, source or retained wire moves.
"""
import copy,json,time
from pathlib import Path
from plan_body36_receiver_space import shared_context,prefixes,P,C,AXES,T
from plan_bolted_receiver_layout import material
from check_body_fanout_material import mate_names,terminal_trim


def run():
    tick=time.monotonic();parent=P.OUT/'bolted-receiver-layout.json';cf=P.OUT/'body36-current-contract.json'
    old,contract=[json.loads(f.read_text()) for f in (parent,cf)]
    for n,h in old['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,wires,pins,_=shared_context();targets={n:s for n,s in targets.items() if not n.startswith('Receiver_')}
    rows={r['wire']:r for r in contract['rows']};names=('W020','W022');domains={};failures=[];checks=0;errors=[]
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'parallel-fuse-receiver-pairs.json',bounds.near)
    def hit(s,t,rs=0,rt=0):
        nonlocal checks
        if not bounds.near(s,t,rs+rt+.0001):return False
        if rt and not t.Solids and len(t.Edges)>1:return any(hit(s,e,rs,rt) for e in t.Edges)
        checks+=1
        try:gap,volume=cache.check(s,t,rs,rt)
        except RuntimeError as e:errors.append(str(e));return True
        return volume>1e-5 or ((rs or rt) and gap<rs+rt-1e-6)
    def same_owner(name,owner):
        return name==owner+'/0/0' or name.startswith('Root/'+owner+'/') or name=='Source/'+owner+'/body/0'
    for name in names:
        original=rows[name];assert name in contract['remaining_wire_ids'];candidates=[]
        for row,method in prefixes(original):
            if method!='full_land_after_turn' or row['receiver_outward_axis']!=[-1,0,0]:continue
            p=row['receiving_parts'][row['receiving_grip_part_index']]
            axis=[(b-a)/p['length_mm'] for a,b in zip(p['start'],p['end'])]
            centre=[(a+b)/2 for a,b in zip(p['start'],p['end'])]
            if axis!=[0,1,0] or abs(centre[1]-40.5)>1e-6 or abs(centre[2]-56.402)>1e-6:continue
            assert abs(centre[0]-original['receiver_point_mm'][0])<1e-6
            candidates.append(row)
        assert len(candidates)==1,(name,len(candidates))
        row=candidates[0];wire=P.wire(row['receiving_parts']);mouth=P.wire(terminal_trim(row['receiving_parts']))
        for n,s in targets.items():
            test=mouth if n.split('/')[0] in mate_names(row) else wire
            if hit(test,s,1.25):failures.append(dict(wire=name,kind='prefix',target=n));break
        else:
            for n,(w,r) in wires.items():
                if hit(wire,w,1.25,r):failures.append(dict(wire=name,kind='prefix',target=n));break
            else:
                p=row['receiving_parts'][row['receiving_grip_part_index']]
                land=dict(id=name+'/Receiver',centre_world_mm=[(a+b)/2 for a,b in zip(p['start'],p['end'])],
                    start_world_mm=p['start'],end_world_mm=p['end'],axis=[0,1,0],length_mm=9)
                options=[]
                for normal in AXES:
                    if normal[1]:continue
                    for offset in (0,-1.5,1.5):
                        q=dict(kind='single',owner=row['existing_fixed_support'],land=land,normal=list(normal),
                            offset=offset,wires=[name],rows=[row]);profile,components=material(q);blocked=None
                        for kind,s in components.items():
                            for n,t in targets.items():
                                if kind in ('body','seed') and same_owner(n,q['owner']):continue
                                if hit(s,t):blocked=kind+':'+n;break
                            if blocked:break
                            for n,(w,r) in wires.items():
                                if hit(s,w,0,r+.25):blocked=kind+':'+n;break
                            if blocked:break
                            if hit(s,wire,0,1 if kind=='band' else 1.25):blocked=kind+':own_prefix';break
                        if blocked:failures.append(dict(wire=name,normal=list(normal),offset=offset,target=blocked))
                        else:q.update(recipe=profile['recipe'],arrival_world_mm=profile['arrival_world_mm']);options.append(q)
                domains[name]=options
        domains.setdefault(name,[])
        print('Parallel fuse domain',name,len(domains[name]),'pairs',checks,flush=True)
    result=dict(status='PARALLEL_FL_FUSE_DOMAINS_CLEAR_JOINT_OPEN' if all(domains.values()) else 'PARALLEL_FL_FUSE_DOMAINS_OPEN',
        parent_domains=parent.relative_to(P.ROOT).as_posix(),replacement_options=domains,
        changed_prefixes=list(names),retained_FL3_land=rows['W024']['receiving_land'],
        failures=failures,errors=errors,checks=checks,worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (parent,cf,Path(__file__))}},
        selected=False,W5_complete=False,physical_pass=False)
    out=P.OUT/'parallel-fuse-receiver-domains.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save()


if __name__=='__main__':run()
