"""One operating plan:24wire saddles,2rail bosses and12source case supports.

Actual retained native structure anchors every branch. Bank4mm trunks may
support insulation-only saddles, never substitute a wire pilot for a case load
root. No normal wires move and no rejected parking geometry is installed.
"""
import argparse,json,itertools,math,time
from pathlib import Path
import FreeCAD as A
import Part
from bank_upper_retained_context import prepare,P
from current_source_retention_context import C
from plan_axial_source_supports import arm_box,direct_elbows
from source_arm_reservations import Reservations
from plan_remaining_loom_support_paths import search
from current_work_guard import check


def printable(parent,body,points,half):
    b=A.BoundBox(parent.BoundBox);b.add(body.BoundBox)
    for p in points:b.add(arm_box(p,p,half).BoundBox)
    return max(b.XLength,b.YLength,b.ZLength)+10<=256+1e-6


def run(resume=False):
    check();tick=time.monotonic();scene=prepare();targets=scene['targets'];wires=scene['wires']
    file=P.OUT/'current-upper-operating-roots.json';preflight_file=P.OUT/'source-case-retention-space.json'
    preflight=json.loads(preflight_file.read_text())
    assert len(preflight['parts'])==24 and not preflight['errors']
    assert not any(r['contacts'] for r in preflight['parts']),'Case material preflight must clear before roots'
    for n,h in preflight['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    pins=dict(scene['pins']);pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (
        preflight_file,Path(__file__),Path(__file__).with_name('source_arm_reservations.py'),
        Path(__file__).with_name('plan_remaining_loom_support_paths.py'))})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'current-upper-operating-root-pairs.json',bounds.near)
    records=[];errors=[];checks=0;mesh_cache={};wire_cache={};additions={}
    parents={o:s.copy() for o,s in scene['parents'].items()}
    for n,s in targets.items():
        for o in parents:
            if n in scene['owned'][o]:parents[o]=Part.makeCompound([parents[o],s])
    def save():
        p=dict(status='ALL38_OPERATING_ROOTS_CLEAR_NATIVE_OPEN' if len(records)==38 and all(r.get('path') for r in records) and not errors else 'OPERATING_SHARED_ROOTS_OPEN',
            groups=records,expected_groups=38,accepted=sum(bool(r.get('path')) for r in records),errors=errors,
            checks=checks,computed_pairs=cache.computed,reused_pairs=cache.reused,
            retired_old_Upper_roots=24,retired_Upper_native_children=scene['retired_Upper_native_children'],
            actual_bank_roots_retained=True,normal_wires_unchanged=True,in_robot_parking=False,
            worker_seconds=round(time.monotonic()-tick,3),source_sha256=pins,
            open=['Native replacement unions,parameter/reopen,closed exports','Whole W5 selection/stock','A2 unpowered assembly/handling sequence'],
            selected=False,W5_complete=False,A2_complete=False,physical_pass=False)
        tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(file);cache.save()
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return False
        if r and not b.Solids and len(b.Edges)>1:return any(hit(a,e,r) for e in b.Edges)
        check();checks+=1;gap,volume=cache.check(a,b,0,r)
        return volume>1e-5 or bool(r and gap<r-1e-6)
    def install(r):
        owner=r['owner'];half=r['half_mm']
        for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):
            s=arm_box(a,b,half);n='AcceptedRoot/'+owner+'/'+r['id']+'/'+str(i)
            additions[n]=(s,owner);parents[owner]=Part.makeCompound([parents[owner],s])
    if resume and file.exists():
        old=json.loads(file.read_text());assert old['source_sha256']==pins and not old['errors']
        for r in old['groups']:
            if r.get('path'):records.append(r);install(r)
        print('reused accepted pinned operating roots',len(records),flush=True)
    done={r['id'] for r in records}
    order=sorted(scene['rows'],key=lambda r:(r['kind']=='wire_saddle',r['owner'],r['id']))
    save()
    for q in order:
        if q['id'] in done:continue
        owner=q['owner'];goal=q['goal'];half=q['half'];allowed=scene['owned'][owner]
        r=dict(id=q['id'],owner=owner,kind=q['kind'],goal=goal,half_mm=half,recipe=q['recipe'],path=None,rejections=[])
        records.append(r);save()
        local={n:v for n,v in additions.items() if v[1]!=owner}
        def blocked(s):
            for n,t in targets.items():
                if n not in allowed and t.Solids and hit(s,t):return n
            for n,(w,rad) in wires.items():
                if hit(s,w,rad+.25):return n
            for n,(t,_) in local.items():
                if hit(s,t):return n
        if (witness:=blocked(arm_box(goal,goal,half))):
            r['rejections'].append(dict(reason='Entire arrival block occupied',witness=witness));save()
            print('operating root',q['id'],'ARRIVAL BLOCKED',witness,flush=True);continue
        candidates=[dict(point=a['point_mm'],provenance='ActualNative/'+owner) for a in preflight['anchors'].get(owner,[])]
        if q['kind']=='wire_saddle' and owner=='UpperCarrier001':candidates+=scene['anchors']
        seen=set();pool=[]
        for a in sorted(candidates,key=lambda a:math.dist(a['point'],goal)):
            root=a['point'];k=tuple(root)
            if k in seen:continue
            seen.add(k)
            if any(math.dist(root,a['point'])<8 for a in pool):continue
            # bank anchors have a proven4mm trunk; native anchors were exactly
            # checked in preflight. A narrower insulation root is contained.
            if 'component' in a and arm_box(root,root,half).cut(a['component'].copy()).Volume>1e-5:continue
            if blocked(arm_box(root,root,half)):continue
            pool.append(a)
            if len(pool)==3:break
        for anchor in pool:
            check();root=anchor['point'];low=[min(a,b)-24 for a,b in zip(root,goal)];high=[max(a,b)+24 for a,b in zip(root,goal)]
            if not printable(parents[owner],q['body'],[root,goal],half):
                r['rejections'].append(dict(root=root,reason='Combined parent exceeds256cube+5mmbrim'));continue
            save();print('operating corridor',q['id'],'root',root,'goal',goal,flush=True)
            reserve=Reservations(targets,wires,{}, {},local,[],dict(name=owner,code=None,moving=False,arm_half_widths_world_mm=half),low,high,mesh_cache,wire_cache,allowed)
            reserve.memo[tuple(round(x,7) for x in root)]=True;reserve.memo[tuple(round(x,7) for x in goal)]=True
            candidate=None
            for points in direct_elbows(root,goal):
                if all(all(reserve.clear([x+(y-x)*j/max(1,math.ceil(math.dist(a,b)/2)) for x,y in zip(a,b)])
                           for j in range(max(1,math.ceil(math.dist(a,b)/2))+1)) for a,b in zip(points,points[1:])):
                    candidate=dict(points_mm=points,method='shared_surface_elbows');break
            if candidate is None:candidate=search(root,goal,low,high,reserve.clear)
            points=candidate['points_mm']
            if not points:r['rejections'].append(dict(root=root,search=candidate));save();continue
            witness=next((v for a,b in zip(points,points[1:]) if (v:=blocked(arm_box(a,b,half)))),None)
            if witness:r['rejections'].append(dict(root=root,witness=witness));save();continue
            if not printable(parents[owner],q['body'],points,half):
                r['rejections'].append(dict(root=root,reason='Path exceeds256cube+5mmbrim'));continue
            r.update(path=points,anchor_provenance=anchor['provenance'],root_subset_verified=True,search=candidate);install(r);break
        save();print('operating root',q['id'],bool(r['path']),'accepted',sum(bool(x.get('path')) for x in records),'pairs',checks,flush=True)
    save()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');run(parser.parse_args().resume)
