"""Root all36 receiver grips to their real fixed native carrier material.

Includes full current36 curves,4 complete sources,8 source arms and every
band. Only printed material belonging to the SAME physical Frame may union.
Unrooted grips are never used as attachment parents.
"""
import copy,json,math,sys,time
from pathlib import Path
import core_receiver_port as T
from plan_body36_receiver_space import shared_context,P,C,AXES
from current_mixed_receiver_material import material,prepare
from plan_axial_source_supports import arm_box,contained_roots,direct_elbows
from plan_remaining_loom_support_paths import search
from source_arm_reservations import Reservations
from check_main_p0_placement import SavedShapes


def receiver_roots(parent,row,limit=4):
    """Exact4mm attachment cubes in THIS native parent, not old source bounds."""
    goal=row['goal_world_mm'];half=row['arm_half_widths_world_mm']
    points=[row['fallback_root_world_mm']]
    for face in sorted(parent.Faces,key=lambda f:math.dist(list(f.CenterOfMass),goal))[:180]:
        if type(face.Surface).__name__!='Plane':continue
        u,U,v,V=face.ParameterRange;normal=face.normalAt((u+U)/2,(v+V)/2)
        points.extend(list(face.CenterOfMass+normal*(sign*2)) for sign in (-1,1))
    result=[];seen=set()
    for point in sorted(points,key=lambda p:math.dist(p,goal)):
        key=tuple(round(v,6) for v in point)
        if key in seen:continue
        seen.add(key)
        if not parent.isInside(C.A.Vector(*point),1e-7,True):continue
        outside=arm_box(point,point,half).copy().cut(parent.copy()).Volume
        if outside>1e-5:continue
        result.append(dict(point_mm=point,outside_retained_parent_mm3=outside))
        if len(result)>=limit:break
    return result


def run():
    tick=time.monotonic();support_first='--support-first' in sys.argv
    lf=P.OUT/('body36-current-contract.json' if support_first else 'body36-current-layout.json');gf=P.OUT/'receiver-joint-selection.json'
    layout=json.loads(lf.read_text())
    if not support_first:
        assert layout['status']=='CURRENT36_CURVES_AND_RECEIVER_GRIPS_EXACT_CLEAR_ROOT_ARMS_NATIVE_OPEN'
        assert len(layout['routes'])==36 and not layout['contacts'] and not layout['errors']
    for n,h in layout['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,old,pins,grips=prepare()
    rows={r['wire']:r for r in layout['rows']};profiles={};parents={};groups=[]
    for q in grips['groups'].values():
        for row in q['rows']:
            if row['wire'] in grips['changed_wire_ids']:rows[row['wire']]=row
    for n,r in layout['inherited_routes' if support_first else 'routes'].items():old['body/'+n]=(P.wire(r['parts']),1)
    if support_first:
        for n in grips['changed_wire_ids']:old['new/'+n+'/receiver']=(P.wire(rows[n]['receiving_parts']),1)
    # Received source-rooted native parents already prove exact equivalence to
    # the retained Frame+source seat+actual source-arm recipe. Read saved BRep,
    # never repeat the costly Boolean reconstruction or borrow a bought board.
    native_receipt=P.OUT/'fixed-source-supports/manifest.json';native=json.loads(native_receipt.read_text())
    assert native['status']=='FOUR_FIXED_SOURCE_SUPPORTS_NATIVE_PREPARED_RECEIVERS_OPEN'
    for n,h in native['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    source_receipt=P.OUT/'current-fixed-receiver-supports/manifest.json';source=json.loads(source_receipt.read_text())
    for f in ('body-axial-rooted-arms-plan.json','body-axial-layout-chosen.json','fixed-native-retained-masks.json'):
        assert source['source_sha256'][(P.OUT/f).relative_to(P.ROOT).as_posix()]==P.SHA(P.OUT/f)
    model=P.OUT/'fixed-source-supports/FixedSourceSupports.FCStd';reader=SavedShapes()
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (native_receipt,source_receipt,model)})
    owners=set(q['owner'] for q in grips['groups'].values())
    for owner in owners:
        record=next(q for q in native['parts'] if q['name']==owner)
        parent=reader.shape(model,record['object'])
        assert abs(parent.Volume-record['volume_mm3'])<1e-4,owner
        include=[n for n in targets if n.startswith('Root/'+owner+'/') or n=='Source/'+owner+'/body/0']
        for n in include:targets.pop(n)
        assert parent.isValid() and len(parent.Solids)==1 and not parent.check(True),owner
        parents[owner]=parent;targets[owner+'/0/0']=parent
    for name,q in grips['groups'].items():
        profile,components=material(q);goal=profile['arrival_world_mm'];profiles[name]=profile
        for kind,s in components.items():targets['Group_'+name+'/'+kind]=s
        groups.append(dict(name=q['owner'],wire=name,group_id=name,kind=q['kind'],core_ids=q['wires'],
            moving=False,code='FL',goal_world_mm=goal,
            fallback_root_world_mm=list(parents[q['owner']].Solids[0].CenterOfMass),
            arm_half_widths_world_mm=[2,2,2],paths=[]))
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'body36-receiver-root-pairs.json',bounds.near)
    checks=0;last=time.monotonic();edges={};rejected=[];mesh_cache={};wire_cache={};additions={};received_owners=set()
    def hit(a,b,r=0):
        nonlocal checks,last
        if not bounds.near(a,b,r+.0001):return False
        if r and not b.Solids and len(b.Edges)>1:
            if id(b) not in edges:edges[id(b)]=(b,list(b.Edges))
            return any(hit(a,e,r) for e in edges[id(b)][1])
        checks+=1;gap,vol=cache.check(a,b,0,r)
        if time.monotonic()-last>20:cache.save();last=time.monotonic()
        return vol>1e-5 or (r and gap<r-1e-6)
    def allowed(row):
        return {n for n in targets if n.startswith('Group_') and n.split('/')[-1] in ('body','seed') and
            grips['groups'][n.split('/')[0].removeprefix('Group_')]['owner']==row['name']}
    def blocked(s,row):
        permitted=allowed(row)
        for n,t in targets.items():
            if n.startswith(row['name']+'/') or n in permitted:continue
            if hit(s,t):return n
        for n,(w,r) in old.items():
            if hit(s,w,r+.25):return n
        return None
    def save():
        result=dict(status=('ALL_GROUPED_RECEIVER_SUPPORT_RESERVATIONS_CLEAR_MIDDLES_OPEN' if support_first else 'ALL_GROUPED_RECEIVER_ROOTS_EXACT_SEGMENTS_CLEAR_NATIVE_OPEN') if all(g['paths'] for g in groups) else 'PARTIAL_GROUPED_RECEIVER_ROOTS',
            groups=groups,rejections=rejected,checks=checks,worker_seconds=round(time.monotonic()-tick,3),
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (lf,gf,Path(__file__))}},
            selected=False,W5_complete=False,physical_pass=False,physical_fit_creep_load_gate_open=True,
            support_first=support_first,
            scope='22physicalrestraints rooted to received4nativeFrames/sourcearms;20wholecurves+16prefixes if support-first, else whole36.21bands/7caps/M2cap+screw/nut/tool. Native/19guides/stock OPEN.')
        out=P.OUT/('body36-receiver-support-reservations.json' if support_first else 'body36-receiver-roots.json');tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save()
        for owner in owners-received_owners:
            subset=[g for g in groups if g['name']==owner]
            if not all(g['paths'] for g in subset):continue
            receipt=dict(result,status='OWNER_RECEIVER_ROOTS_EXACT_CLEAR_NATIVE_OPEN',groups=subset,
                owner=owner,scope='Received complete owner root set; later owners must check this already rooted material. Full36rootproof/native/stock remainOPEN.')
            file=P.OUT/(('body36-receiver-support-' if support_first else 'body36-receiver-roots-')+owner+'.json')
            assert not file.exists(),'Never overwrite received owner root proof'
            file.write_text(json.dumps(receipt,indent=2)+'\n');received_owners.add(owner)
            print('received complete receiver owner',owner,len(subset),flush=True)
    # Short roots first add useful supported material for later long branches.
    groups.sort(key=lambda r:(r['name'],parents[r['name']].distToShape(arm_box(profiles[r['wire']]['arrival_world_mm'],profiles[r['wire']]['arrival_world_mm'],(2,2,2)))[0]))
    for row in groups:
        name=row['wire'];parent=parents[row['name']];goal=row['goal_world_mm']
        receipts=receiver_roots(parent,row,4);row['root_patch_receipts']=receipts
        roots=[r['point_mm'] for r in receipts]
        if not roots:rejected.append(dict(wire=name,reason='No proven contained root cube'));save();continue
        low=[min([goal[i]]+[r[i] for r in roots])-24 for i in range(3)]
        high=[max([goal[i]]+[r[i] for r in roots])+24 for i in range(3)]
        # Frame is fixed; code/axes irrelevant to this owner-relative transform.
        reservations=Reservations(targets,old,{}, {},additions,[],row,low,high,mesh_cache,wire_cache,allowed(row))
        for root in roots:
            if blocked(arm_box(root,root,(2,2,2)),row):continue
            reservations.memo[tuple(round(v,7) for v in root)]=True
            reservations.memo[tuple(round(v,7) for v in goal)]=True
            proposal=None
            for points in direct_elbows(root,goal):
                okay=True
                for a,b in zip(points,points[1:]):
                    steps=max(1,math.ceil(math.dist(a,b)/2))
                    if not all(reservations.clear([x+(y-x)*j/steps for x,y in zip(a,b)]) for j in range(steps+1)) or blocked(arm_box(a,b,(2,2,2)),row):okay=False;break
                if okay:proposal=dict(points_mm=points,method='exact_segments_direct_elbows');break
            if not proposal:proposal=search(root,goal,low,high,reservations.clear)
            points=proposal.get('points_mm');witness=None
            if points:
                for a,b in zip(points,points[1:]):
                    witness=blocked(arm_box(a,b,(2,2,2)),row)
                    if witness:break
            if not points or witness:rejected.append(dict(wire=name,root=root,proposal=proposal,witness=witness));continue
            row['paths']=[dict(points_mm=points,root_parent=row['name'],proposal=proposal)]
            new=parent.copy()
            for a,b in zip(points,points[1:]):new=new.fuse(arm_box(a,b,(2,2,2))).removeSplitter()
            new=new.fuse(profiles[name]['body']).removeSplitter()
            assert new.isValid() and len(new.Solids)==1 and not new.check(True),name
            parents[row['name']]=new;targets[row['name']+'/0/0']=new
            break
        save();print('receiver root',name,bool(row['paths']),'pairs',checks,flush=True)
    save()


if __name__=='__main__':run()
