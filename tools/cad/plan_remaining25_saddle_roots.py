"""Root the frozen54 saddles together, without repeating their domain search.

This is an independent candidate contribution, NOT acceptance of the unresolved
bank/service layout. Any later changed bank or source part must recheck affected
arms. Current36 wires,13 native source lands and all54 saddle bodies/bands enter
the same reservations. Actual segments, not the meshes, accept each path.
"""
import argparse
import json
import math
import time
from pathlib import Path
import FreeCAD as A
import Part
from remaining25_shared_context import load, P
from current_source_retention_context import C, same_parent
from plan_remaining25_restraint_space import profile
from plan_local_source_retention_roots import patches
from plan_axial_source_supports import arm_box, direct_elbows
from source_arm_reservations import Reservations
from plan_remaining_loom_support_paths import search
from current_work_guard import check

HALF=[1.4,1.4,1.4]  # Insulation-lacing support only, NOT a bank load support.


def printable(parent,body,points):
    bounds=A.BoundBox(parent.BoundBox)
    bounds.add(body.BoundBox)
    for p in points:
        bounds.add(arm_box(p,p,HALF).BoundBox)
    return sorted([bounds.XLength+10,bounds.YLength+10,bounds.ZLength+10])[-1]<=256+1e-6


def run(resume=False):
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load()
    source=P.OUT/'remaining25-restraint-space.json';receipt=json.loads(source.read_text())
    assert len(receipt['selected_options'])==54 and not receipt['errors']
    assert receipt['status']=='REMAINING25_SADDLE_DOMAINS_AND_SHARED_MATERIAL_CLEAR_ROOTS_OPEN'
    for name,digest in receipt['source_sha256'].items():assert P.SHA(P.ROOT/name)==digest,name
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (
        source,Path(__file__),Path(__file__).with_name('plan_local_source_retention_roots.py'),
        Path(__file__).with_name('plan_axial_source_supports.py'),
        Path(__file__).with_name('source_arm_reservations.py'),
        Path(__file__).with_name('plan_remaining_loom_support_paths.py'))})
    groups={g['id']:g for g in receipt['spatial_groups']};profiles={};additions={}
    for gid,index in receipt['selected_options'].items():
        rec=receipt['domains'][gid][index]['recipe'];q=profile(groups[gid],rec['normal'],rec['knot_sign'])
        assert q['recipe']==rec;profiles[gid]=q
        for kind in ('body','band'):additions['Saddle/'+gid+'/'+kind]=(q[kind],None)
    file=P.OUT/'remaining25-saddle-roots.json';rows=[];errors=[];checks=0
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'remaining25-saddle-root-pairs.json',bounds.near)
    mesh_cache={};wire_cache={};parent_shapes={n:s.copy() for n,s in parents.items()}
    def save():
        result=dict(status='ALL54_SADDLE_ROOT_SEGMENTS_CLEAR_NATIVE_BANK_OPEN' if len(rows)==54 and all(r.get('path') for r in rows) and not errors else 'SADDLE_ROOT_SHARED_PLAN_OPEN',
            groups=rows,expected_groups=54,accepted_groups=sum(bool(r.get('path')) for r in rows),
            arm_half_widths_mm=HALF,checks=checks,errors=errors,source_sha256=pins,
            worker_seconds=round(time.monotonic()-tick,3),
            scope='Current shared54 frozen saddles, current full source/body/head/tail/leg scene. Wire-support arms only. Failed bank combs are NOT installed obstacles or selected parts.',
            open=['Bank structural retention and actual installed ATO service layout',
                  'Native parent unions/parameter/reopen/exports',
                  'Changed bank/source interfaces must recheck affected arms before whole selection',
                  'Whole stock,assembly,W5/M4'],selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(file);cache.save()
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and not b.Solids and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        try:check()
        except TimeoutError as e:errors.append(str(e));save();raise
        checks+=1
        try:
            gap,volume=cache.check(a,b,0,r)
            return volume>1e-5 or bool(r and gap<r-1e-6)
        except (AssertionError,RuntimeError,ValueError) as e:
            errors.append(str(e));return True
    def install(row):
        owner=row['owner'];gid=row['id'];q=profiles[gid]
        # Only aggregate extents here; native unions are a later explicit gate.
        # Avoid repeatedly rebuilding an already validated large parent BRep.
        parent_shapes[owner]=Part.makeCompound([parent_shapes[owner],q['body']])
        for i,(a,b) in enumerate(zip(row['path'],row['path'][1:])):
            s=arm_box(a,b,HALF);additions['AcceptedSaddleArm/'+owner+'/'+gid+'/'+str(i)]=(s,None)
            parent_shapes[owner]=Part.makeCompound([parent_shapes[owner],s])
    if resume and file.exists():
        old=json.loads(file.read_text());assert not old['errors']
        assert old['source_sha256']==pins and old['arm_half_widths_mm']==HALF
        for r in old['groups']:
            if r.get('path'):rows.append(r);install(r)
        print('reused exact pinned saddle roots',len(rows),flush=True)
    completed={r['id'] for r in rows}
    # Short nearby roots first reduce gratuitous long branches; every accepted
    # arm becomes a real obstacle before planning the next one.
    order=sorted(profiles,key=lambda gid:min(s.distToShape(Part.Vertex(A.Vector(*profiles[gid]['root_tip_mm'])))[0] for s in parents.values()))
    for gid in order:
        if gid in completed:continue
        check();q=profiles[gid];goal=q['root_tip_mm'];rec=q['recipe']
        row=dict(id=gid,recipe=rec,root_tip_mm=goal,owner=None,path=None,rejections=[]);rows.append(row)
        inherited=receipt['domains'][gid][receipt['selected_options'][gid]]
        touching=inherited.get('touching_printed_parents',inherited.get('touching_owners',[]))
        # Determine union ownership from actual intersections, not stale hints.
        actual=set()
        for n,s in targets.items():
            if not s.Solids or not hit(q['body'],s):continue
            actual.update(o for o in parents if same_parent(o,n,grips))
        if len(actual)>1:
            row['rejections'].append(dict(reason='Seat joins different printed parents',owners=sorted(actual)));save();continue
        v=Part.Vertex(A.Vector(*goal))
        owners=list(actual) if actual else sorted(parents,key=lambda o:parents[o].distToShape(v)[0])[:3]
        for owner in owners:
            if not printable(parent_shapes[owner],q['body'],[goal]):
                row['rejections'].append(dict(owner=owner,reason='Combined native parent+5mmbrim exceeds256cube'));continue
            allowed={n for n in targets if same_parent(owner,n,grips)}
            local={n:x for n,x in additions.items() if n!='Saddle/'+gid+'/body' and not n.startswith('AcceptedSaddleArm/'+owner+'/')}
            def blocked(s):
                for n,t in targets.items():
                    if n not in allowed and t.Solids and hit(s,t):return n
                for n,(w,radius) in wires.items():
                    if hit(s,w,radius+.25):return n
                for n,(t,_) in local.items():
                    if hit(s,t):return n
                return None
            if actual:
                joined=parents[owner].fuse(q['body']).removeSplitter()
                if joined.isValid() and len(joined.Solids)==1 and not joined.check(True):
                    row.update(owner=owner,path=[goal],direct_union_verified=True);install(row);break
            if (witness:=blocked(arm_box(goal,goal,HALF))):
                row['rejections'].append(dict(owner=owner,goal_witness=witness));continue
            for patch in patches(parents[owner],goal,limit=2):
                root=patch['point_mm']
                if (witness:=blocked(arm_box(root,root,HALF))):
                    row['rejections'].append(dict(owner=owner,root=root,witness=witness));continue
                low=[min(a,b)-24 for a,b in zip(root,goal)];high=[max(a,b)+24 for a,b in zip(root,goal)]
                contract=dict(name=owner,code=None,moving=False,arm_half_widths_world_mm=HALF)
                reserve=Reservations(targets,wires,{}, {},local,[],contract,low,high,mesh_cache,wire_cache,allowed)
                reserve.memo[tuple(round(x,7) for x in root)]=True
                reserve.memo[tuple(round(x,7) for x in goal)]=True
                candidate=None
                for points in direct_elbows(root,goal):
                    if all(all(reserve.clear([x+(y-x)*j/max(1,math.ceil(math.dist(a,b)/2)) for x,y in zip(a,b)]) for j in range(max(1,math.ceil(math.dist(a,b)/2))+1)) for a,b in zip(points,points[1:])):
                        candidate=dict(points_mm=points,method='surface_elbows');break
                if candidate is None:candidate=search(root,goal,low,high,reserve.clear)
                points=candidate['points_mm'];witness=None
                if not points:row['rejections'].append(dict(owner=owner,root=root,search=candidate));save();continue
                if not printable(parent_shapes[owner],q['body'],points):
                    row['rejections'].append(dict(owner=owner,reason='Path exceeds256cube with5mmbrim'));continue
                for a,b in zip(points,points[1:]):
                    if (witness:=blocked(arm_box(a,b,HALF))):break
                if witness:row['rejections'].append(dict(owner=owner,root=root,witness=witness,search=candidate));save();continue
                row.update(owner=owner,path=points,root_subset_verified=True,search=candidate);install(row);break
            if row['path']:break
        save();print('saddle root',gid,row['owner'],bool(row['path']),'accepted',sum(bool(r.get('path')) for r in rows),'pairs',checks,flush=True)
    save()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');run(parser.parse_args().resume)
