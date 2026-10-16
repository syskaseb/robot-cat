"""One structural pilot for twelve catalog seats on existing UpperCarrier.

4x4mm trunks,2mm panel leaf tabs, full current wire/support scene and nominal
ATO/project-jaw reservations together. No strength/creep/extraction rating:
support the holder by hand during unpowered delivered fit trials. Old54 wire
arms are NOT repurposed as bank load roots. Native unions remain a later gate.
"""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
from remaining25_shared_context import load,P
from current_source_retention_context import C,same_parent
from current_bank_datums import datums,nominal_sweep
from plan_individual_bank_seats import seats
from plan_remaining25_restraint_space import profile
from plan_axial_source_supports import arm_box,direct_elbows
from plan_remaining25_saddle_roots import box_distance
from source_arm_reservations import Reservations
from plan_remaining_loom_support_paths import search
from loom_land_port import box
from current_work_guard import check

HALF=[2.,2.,2.]
LEAF_HALF=[2.,.8,.9]
OWNER='UpperCarrier001'


def patches(parent,goal,limit=3):
    vertex=Part.Vertex(A.Vector(*goal));out=[];seen=set()
    # These are centres of retained4mm structural members, not old1.4mm
    # wire arms. Verify each cube exactly ONCE and share across12 seats.
    for point in sorted(([-56,-22,120],[-56,-22,80],[84,40,146.5]),key=lambda p:math.dist(p,goal)):
        if not parent.isInside(A.Vector(*point),1e-7,True):continue
        if arm_box(point,point,HALF).cut(parent.copy()).Volume>1e-5:continue
        out.append(point)
    if out:return out[:limit]
    for face in sorted(parent.Faces,key=lambda f:box_distance(f,goal))[:60]:
        if type(face.Surface).__name__!='Plane':continue
        u,U,v,V=face.ParameterRange;n=face.normalAt((u+U)/2,(v+V)/2)
        near=face.distToShape(vertex)[1][0][0]
        for p in (near,face.CenterOfMass):
            for sign in (-1,1):
                point=list(p+n*(sign*2));key=tuple(round(x,6) for x in point)
                if key in seen:continue
                seen.add(key)
                if not parent.isInside(A.Vector(*point),1e-7,True):continue
                # Cheap rejection only: thin walls cannot contain a4mm cube.
                # Corners never ACCEPT it; exact subtraction below still must.
                import itertools
                if not all(parent.isInside(A.Vector(*[v+d*s for v,d,s in zip(point,HALF,signs)]),1e-7,True)
                           for signs in itertools.product((-1,1),repeat=3)):continue
                if arm_box(point,point,HALF).cut(parent.copy()).Volume>1e-5:continue
                out.append(point)
                if len(out)==limit:return out
    return out


def run():
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load()
    files=[P.OUT/(n+'.json') for n in ('individual-bank-seat-relief-space','remaining25-restraint-space','remaining25-saddle-roots')]
    receipt,saddles,roots=[json.loads(f.read_text()) for f in files]
    assert receipt['status']=='TWELVE_INDIVIDUAL_BANK_SEATS_MATERIAL_CLEAR_ROOTS_SERVICE_OPEN'
    for p in (receipt,saddles,roots):
        for n,h in p['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    groups={g['id']:g for g in saddles['spatial_groups']}
    for gid,i in saddles['selected_options'].items():
        rec=saddles['domains'][gid][i]['recipe'];s=profile(groups[gid],rec['normal'],rec['knot_sign']);assert s['recipe']==rec
        targets.update({'Remaining25/'+gid+'/'+k:s[k] for k in ('body','band')})
    for r in roots['groups']:
        for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):
            targets['CurrentSaddleRoot/'+r['owner']+'/'+r['id']+'/'+str(i)]=arm_box(a,b,roots['arm_half_widths_mm'])
    placed=datums(targets);panels=seats(placed,True);parent=parents[OWNER]
    anchor_pool=None
    for r in receipt['seats']:assert r['recipe']==panels[r['id']]['recipe']
    for r in placed:
        targets['BankATOService/'+r['id']]=nominal_sweep(r)
        x,y=r['centre_xy_mm'];z=r['flange_top_z_mm']
        for sign in (-1,1):
            lo,hi=(-5.55,-2.55) if sign==-1 else (2.55,5.55)
            targets['BankJawService/'+r['id']+'/'+str(sign)]=box([x-10.55,y+lo,z+11,x+10.55,y+hi,z+58])
    allowed={n for n in targets if same_parent(OWNER,n,grips) or n.startswith('CurrentSaddleRoot/'+OWNER+'/')}
    local={'BankSeat/'+n:(q['body'],None) for n,q in panels.items()}
    # Seats all belong to the same proposed parent. Material within them is
    # union work; foreign purchased housings are NEVER globally excluded.
    files.extend(Path(__file__).with_name(n) for n in ('plan_individual_bank_roots.py','plan_individual_bank_seats.py',
        'source_arm_reservations.py','plan_remaining_loom_support_paths.py','plan_axial_source_supports.py','plan_remaining25_saddle_roots.py'))
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'individual-bank-root-pairs.json',bounds.near)
    records=[];errors=[];checks=0;mesh_cache={};wire_cache={};extent=A.BoundBox(parent.BoundBox)
    for q in panels.values():extent.add(q['body'].BoundBox)
    def save():
        out=dict(status='TWELVE_BANK_SEAT_ROOTS_CLEAR_NATIVE_SERVICE_OPEN' if len(records)==12 and all(r.get('path') for r in records) and not errors else 'INDIVIDUAL_BANK_SHARED_ROOT_PLAN_OPEN',
            groups=records,accepted=sum(bool(r.get('path')) for r in records),owner=OWNER,
            trunk_half_mm=HALF,leaf_half_mm=LEAF_HALF,checks=checks,errors=errors,source_sha256=pins,
            worker_seconds=round(time.monotonic()-tick,3),
            basis='One UpperCarrier replacement,12catalog snap seats and structural pilot roots. Old54 wire-only roots retained as obstacles/union references, not bank root anchors. All12 nominal ATO35mm and project3mm jaws constrain NEW arms; existing41service conflicts remain OPEN.',
            physical_gate='No bank strength/creep/pull-force rating; support holder during unpowered delivered snap/ATO fit sample.',
            selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        f=P.OUT/'individual-bank-roots.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2)+'\n');tmp.replace(f);cache.save()
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and not b.Solids and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        try:
            check();checks+=1;gap,volume=cache.check(a,b,0,r)
        except (TimeoutError,AssertionError,RuntimeError,ValueError) as e:errors.append(str(e));save();raise
        return volume>1e-5 or bool(r and gap<r-1e-6)
    def blocked(s,own=None,panel=None):
        for n,t in targets.items():
            if n in allowed or not t.Solids:continue
            if not hit(s,t):continue
            if n==own and panel is not None and s.common(t).cut(panel.copy()).Volume<1e-5:continue
            return n
        for n,(w,r) in wires.items():
            if hit(s,w,r+.25):return n
        return None
    save()
    print('bank roots: verifying concrete4mm structural anchors once',flush=True)
    anchor_pool=patches(parent,[40,40,123])
    print('bank roots: actual structural anchors',anchor_pool,flush=True)
    for r in sorted(placed,key=lambda r:box_distance(parent,r['centre_xy_mm']+[123])):
        gid=r['id'];q=panels[gid];x,y,z=q['recipe']['centre_mm']
        row=dict(id=gid,seat_recipe=q['recipe'],owner=OWNER,path=None,rejections=[]);records.append(row)
        save()
        # Two whole leaf-exit directions allocated before trunk search; no
        # scalar position nudges of the holder, terminal or panel are made.
        for sign in sorted((-1,1),key=lambda v:abs(y+v*12)):
            leaf_start=[x,y+sign*6.65,z-3];exit=[x,y+sign*12,z-3]
            leaf=arm_box(leaf_start,exit,LEAF_HALF)
            if (v:=blocked(leaf,r['parts']['Housing']['name'],q['body'])):
                row['rejections'].append(dict(leaf_sign=sign,witness=v));continue
            for root in sorted(anchor_pool,key=lambda p:math.dist(p,exit)):
                if (v:=blocked(arm_box(root,root,HALF))):row['rejections'].append(dict(root=root,witness=v));continue
                low=[min(a,b)-24 for a,b in zip(root,exit)];high=[max(a,b)+24 for a,b in zip(root,exit)]
                save();print('bank root corridor preparation',gid,root,exit,flush=True)
                reserve=Reservations(targets,wires,{}, {},{},[],dict(name=OWNER,code=None,moving=False,arm_half_widths_world_mm=HALF),low,high,mesh_cache,wire_cache,allowed)
                reserve.memo[tuple(round(v,7) for v in root)]=True
                reserve.memo[tuple(round(v,7) for v in exit)]=True
                candidate=None
                for points in direct_elbows(root,exit):
                    if all(all(reserve.clear([x+(y-x)*j/max(1,math.ceil(math.dist(a,b)/2)) for x,y in zip(a,b)]) for j in range(max(1,math.ceil(math.dist(a,b)/2))+1)) for a,b in zip(points,points[1:])):
                        candidate=dict(points_mm=points,method='surface_elbows');break
                if candidate is None:candidate=search(root,exit,low,high,reserve.clear)
                points=candidate['points_mm']
                if not points:row['rejections'].append(dict(root=root,search=candidate));save();continue
                witness=next((v for a,b in zip(points,points[1:]) if (v:=blocked(arm_box(a,b,HALF)))),None)
                if witness:row['rejections'].append(dict(root=root,witness=witness));save();continue
                new_extent=A.BoundBox(extent);new_extent.add(leaf.BoundBox)
                for p in points:new_extent.add(arm_box(p,p,HALF).BoundBox)
                if max(new_extent.XLength,new_extent.YLength,new_extent.ZLength)+10>256:
                    row['rejections'].append(dict(reason='Parent+all seats/arms+5mmbrim exceeds256cube'));continue
                row.update(path=points,leaf_points=[leaf_start,exit],leaf_sign=sign,root_subset_verified=True,search=candidate)
                extent=new_extent;break
            if row['path']:break
        # Same-parent bank branches may merge; their new material remains a
        # true obstacle to every retained wire and other component above.
        save();print('bank root',gid,bool(row['path']),'accepted',sum(bool(r.get('path')) for r in records),'pairs',checks,flush=True)
    save()


if __name__=='__main__':run()
