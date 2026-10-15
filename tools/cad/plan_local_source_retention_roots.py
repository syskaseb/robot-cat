"""Root frozen source lands locally with the proven shared arm planner.

No new wire positions, no long global stelaż, no per-voxel OCC queries.
Meshes propose; full actual segments qualify. Each accepted arm immediately
becomes an obstacle for subsequent arms, and all seats/bands exist up front.
"""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
from current_source_retention_context import context,same_parent,P,C
from source_arm_reservations import Reservations
from plan_axial_source_supports import arm_box,direct_elbows
from plan_remaining_loom_support_paths import search
from current_work_guard import check


HALF=[1.4,1.4,1.4] # Prototype wire-support pilot, never a leg load support.


def patches(parent,goal,limit=2):
    v=Part.Vertex(A.Vector(*goal));faces=sorted(parent.Faces,key=lambda f:f.distToShape(v)[0])[:24]
    result=[];seen=set()
    for face in faces:
        if type(face.Surface).__name__!='Plane':continue
        u,U,w,W=face.ParameterRange;n=face.normalAt((u+U)/2,(w+W)/2)
        near=face.distToShape(v)[1][0][0]
        for p in (near,face.CenterOfMass):
            for sign in (-1,1):
                point=list(p+n*(sign*1.5));key=tuple(round(x,6) for x in point)
                if key in seen:continue
                seen.add(key)
                if not parent.isInside(A.Vector(*point),1e-7,True):continue
                outside=arm_box(point,point,HALF).copy().cut(parent.copy()).Volume
                if outside>1e-5:continue
                result.append(dict(point_mm=point,outside_parent_mm3=outside))
                if len(result)==limit:return result
    return result


def run():
    check();tick=time.monotonic();targets,wires,pins,profiles,recipes,parents,grips=context()
    additions={};rows=[];errors=[];checks=0;mesh_cache={};wire_cache={}
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'local-source-retention-pairs.json',bounds.near)
    for n,q in profiles.items():
        for kind in ('body','band'):additions['SourceLand/'+n+'/'+kind]=(q[kind],None)
    for f in (Path(__file__),Path(__file__).with_name('source_arm_reservations.py'),
              Path(__file__).with_name('fast_carrier_reservations.py'),
              Path(__file__).with_name('plan_remaining_loom_support_paths.py')):
        pins[f.relative_to(P.ROOT).as_posix()]=P.SHA(f)
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and not b.Solids and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        check();checks+=1
        try:
            gap,vol=cache.check(a,b,0,r)
            return vol>1e-5 or (r and gap<r-1e-6)
        except (RuntimeError,AssertionError,ValueError) as e:errors.append(str(e));return True
    def save():
        done=len(rows)==13 and all(r.get('path') for r in rows) and not errors
        result=dict(status='THIRTEEN_LOCAL_SOURCE_ROOTS_EXACT_SEGMENTS_CLEAR_NATIVE_OPEN' if done else 'LOCAL_SOURCE_ROOT_PLAN_OPEN',
            groups=rows,arm_half_widths_world_mm=HALF,errors=errors,checks=checks,source_sha256=pins,
            worker_seconds=round(time.monotonic()-tick,3),
            rejected_architecture='bd1479b: three long shared support trees; keep13clear lacing loops, replace only load paths/parent assignment.',
            gates=['Final parent unions/parameter/reopen/exports','Source case/S0 retention and other25interfaces','Whole assembly/stock/W5'],
            selected=False,W5_complete=False,physical_pass=False)
        f=P.OUT/'local-source-retention-roots.json';tmp=f.with_suffix('.tmp')
        tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    for gid,profile in profiles.items():
        check();goal=profile['root_tip_mm'];row=dict(id=gid,recipe=recipes[gid],goal_mm=goal,path=None,rejections=[])
        rows.append(row)
        # Check whole seats once, before any path or owner selection. The
        # thirteen loop placements are unchanged from their received proof.
        seat_contacts=[];touching_owners=set()
        for n,t in targets.items():
            if not hit(profile['body'],t):continue
            eligible=[owner for owner in parents if same_parent(owner,n,grips)]
            if len(eligible)==1:touching_owners.add(eligible[0])
            else:seat_contacts.append(n)
        for n,(w,r) in wires.items():
            if hit(profile['body'],w,r+.25):seat_contacts.append(n)
        for n,(t,_) in additions.items():
            if n=='SourceLand/'+gid+'/body':continue
            if hit(profile['body'],t):seat_contacts.append(n)
        if len(touching_owners)>1:seat_contacts.append('Different physical printed parents would be bridged')
        row['seat_contacts']=seat_contacts;row['touching_printed_parents']=sorted(touching_owners)
        if seat_contacts:save();print('local source seat blocked',gid,seat_contacts,flush=True);continue
        # Finite actual parent choices, ordered by REAL closest-surface
        # distance. No root on a bought casing, tie, cap or bbox reservation.
        vertex=Part.Vertex(A.Vector(*goal))
        choices=list(touching_owners) if touching_owners else sorted(parents,key=lambda n:parents[n].distToShape(vertex)[0])[:3]
        for owner in choices:
            if touching_owners:
                joined=parents[owner].fuse(profile['body']).removeSplitter()
                if joined.isValid() and len(joined.Solids)==1 and not joined.check(True):
                    row.update(owner=owner,path=[goal],direct_parent_union_verified=True)
                    break
            check();roots=patches(parents[owner],goal)
            row.setdefault('parent_candidates',[]).append(dict(owner=owner,patches=roots))
            allowed={n for n in targets if same_parent(owner,n,grips)}
            local_additions={n:v for n,v in additions.items() if n!='SourceLand/'+gid+'/body' and
                not (n.startswith('AcceptedSourceArm/'+owner+'/'))}
            def blocked(s):
                for n,t in targets.items():
                    if n not in allowed and hit(s,t):return n
                for n,(w,r) in wires.items():
                    if hit(s,w,r+.25):return n
                for n,(t,_) in local_additions.items():
                    if hit(s,t):return n
                return None
            if (witness:=blocked(arm_box(goal,goal,HALF))):
                row['rejections'].append(dict(owner=owner,goal_witness=witness));continue
            for patch in roots:
                check();root=patch['point_mm']
                if (witness:=blocked(arm_box(root,root,HALF))):
                    row['rejections'].append(dict(owner=owner,root=root,witness=witness));continue
                low=[min(a,b)-24 for a,b in zip(root,goal)];high=[max(a,b)+24 for a,b in zip(root,goal)]
                contract=dict(name=owner,code=None,moving=False,arm_half_widths_world_mm=HALF)
                reserve=Reservations(targets,wires,{}, {},local_additions,[],contract,low,high,mesh_cache,wire_cache,allowed)
                reserve.memo[tuple(round(x,7) for x in root)]=True
                reserve.memo[tuple(round(x,7) for x in goal)]=True
                candidate=None
                for points in direct_elbows(root,goal):
                    clear=True
                    for a,b in zip(points,points[1:]):
                        count=max(1,math.ceil(math.dist(a,b)/2))
                        if not all(reserve.clear([x+(y-x)*j/count for x,y in zip(a,b)]) for j in range(count+1)):
                            clear=False;break
                    if clear:candidate=dict(points_mm=points,method='shared_surface_elbows');break
                if candidate is None:candidate=search(root,goal,low,high,reserve.clear)
                points=candidate['points_mm'];witness=None
                for a,b in zip(points,points[1:]):
                    if (witness:=blocked(arm_box(a,b,HALF))):break
                if not points or witness:
                    row['rejections'].append(dict(owner=owner,root=root,search=candidate,witness=witness));save();continue
                row.update(owner=owner,path=points,root_subset_verified=True,search=candidate)
                for i,(a,b) in enumerate(zip(points,points[1:])):
                    additions['AcceptedSourceArm/'+owner+'/'+gid+'/'+str(i)]=(arm_box(a,b,HALF),None)
                break
            if row['path']:break
        save();print('local source root',gid,row.get('owner'),bool(row['path']),'pairs',checks,flush=True)
    save()


if __name__=='__main__':run()
