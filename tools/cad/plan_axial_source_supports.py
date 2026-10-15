"""Joint rooted-arm plan for the four allocated complete source corridors.

Reuse exact retained native parents, not empty owner boxes. All eight printed
seats, bands, breakouts and source poses enter one planning scene before arms.
No current native document or historic source is overwritten.
"""
import itertools,json,math,time
from pathlib import Path
import FreeCAD as A
import Part
import check_near_axis_hip_sources as C
from current_axial_receiver_material import prepare_context
from plan_remaining_loom_support_paths import search
P=C.P


def port_arm_halves(recipe):
    frame=recipe['local_to_world']
    return [sum(abs(frame[j*4+i])*h for i,h in enumerate((2,3,2))) for j in range(3)]


def arm_box(a,b,halves=(2,3,2)):
    return P.box([min(x,y)-d for x,y,d in zip(a,b,halves)]+
                 [max(x,y)+d for x,y,d in zip(a,b,halves)])


def run():
    tick=time.monotonic();file=P.OUT/'body-axial-layout-chosen.json';plan=json.loads(file.read_text())
    assert len(plan['hips'])==4 and not plan['rejected']
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    targets,old,pins,family,axes,own,bare,files,subsets=prepare_context(plan)
    additions={};ports={};contracts=[];wire_owners={}
    for n in old:
        if n.startswith('leg/'):
            _,loom,h,*_=n.split('/');code=next(r['cad_code'] for r in family['hips'] if r['loom']==loom)
            wire_owners[n]=(code,int(h))
    root_plan=json.loads((P.OUT/'complete-source-carriers-plan.json').read_text())
    fixed_plan=json.loads((P.OUT/'body-low-hip-retention-plan.json').read_text())
    for row in plan['hips']:
        code,loom,leg=row['cad_code'],row['loom'],row['physical_leg']
        for moving in (False,True):
            _,profile=C.make_port(row,moving);name=leg+('HipExtension' if moving else 'FixedCarrier')
            owner=(code,0) if moving else None
            parent=targets[name+'/0/0'];goal=profile['arrival_world_mm']
            root=list(parent.distToShape(Part.Vertex(A.Vector(*goal)))[1][0][0])
            fallback=(next(r for r in root_plan['roots'] if r['leg']==leg)['paths'][0]['points_mm'][0]
                      if moving else next(r['root_world_mm'] for r in fixed_plan['retained'] if r['owner']==name))
            contracts.append(dict(name=name,loom=loom,code=code,moving=moving,root_world_mm=root,
                fallback_root_world_mm=fallback,goal_world_mm=goal,port_recipe=profile['recipe'],
                arm_half_widths_world_mm=port_arm_halves(profile['recipe']),paths=[]))
            ports[name]=profile
            for kind in ('body','band'):
                for h in C.ANGLES if moving else (0,):
                    key=name+'/'+kind+'/'+str(h)
                    additions[key]=(C.moved(profile[kind],C.transform(axes,code,h,0,'Hip')) if moving else profile[kind],(code,h) if moving else None)
        for pose in row['poses']:
            h=pose['angle']
            if h in C.ANGLES:
                key='chosen/'+loom+'/'+str(h)
                old[key]=(P.wire(pose['parts']+C.B.moved_parts(row['source_parts'],row['source'],h,0,axes)),3)
                wire_owners[key]=(code,h)
        for core in row['source_fans']:old['fan/'+loom+'/'+core['core']]=(P.wire(core['parts']),1)
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'axial-rooted-arm-pairs.json',bounds.near)
    checks=0;rejections=[];last=time.monotonic()
    def hit(s,t,r=0):
        nonlocal checks,last
        if not bounds.near(s,t,r+.0001):return False
        checks+=1;gap,volume=cache.check(s,t,0,r)
        if time.monotonic()-last>20:cache.save();last=time.monotonic()
        return volume>1e-5 or (r and gap<r-1e-6)
    def blocked(shape,row):
        name,code,moving=row['name'],row['code'],row['moving']
        for h in C.ANGLES if moving else (0,):
            current=C.moved(shape,C.transform(axes,code,h,0,'Hip')) if moving else shape
            for target,s in targets.items():
                if target.startswith(name+'/'):continue # Same physical parent, preserved by union.
                if moving and not C.same_leg_pose(own.get(target),code,h):continue
                if hit(current,s):return dict(target=target,hip=h)
            for target,(w,r) in old.items():
                if moving and not C.same_leg_pose(wire_owners.get(target),code,h):continue
                if hit(current,w,r+.25):return dict(target=target,hip=h)
            for target,(s,owner) in additions.items():
                if target.startswith(name+'/body/'):continue # Intentional arm-to-own-seat union only.
                if moving and not C.same_leg_pose(owner,code,h):continue
                if hit(current,s):return dict(target=target,hip=h)
        return None
    def save():
        result=dict(status='EIGHT_ROOTED_SOURCE_ARMS_EXACT_SEGMENTS_CLEAR_UNION_NATIVE_OPEN' if all(r['paths'] for r in contracts) else 'PARTIAL_ROOTED_SOURCE_ARM_PLAN',
            groups=contracts,rejections=rejections,checks=checks,retained_subset_receipts=subsets,
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in [file,*files,Path(__file__)]}},
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            scope='Eight4x6x4rootedarms vsallretainedmaterial,allsourceposes/12fans/20bodyroutes andpriornewarms. Ownparent/seatunion permitted only within same physical part. Booleanunion/native/36cores/stock stillOPEN.')
        out=P.OUT/'body-axial-rooted-arms-plan.json';tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(out);cache.save()
    for row in contracts:
        goal=row['goal_world_mm'];start_options=[row['root_world_mm'],row['fallback_root_world_mm']]
        for root in start_options:
            low=[min(a,b)-24 for a,b in zip(root,goal)];high=[max(a,b)+24 for a,b in zip(root,goal)]
            memo={}
            def clear(point):
                key=tuple(round(v,7) for v in point)
                if key not in memo:memo[key]=blocked(arm_box(point,point,row['arm_half_widths_world_mm']),row) is None
                return memo[key]
            candidate=search(root,goal,low,high,clear)
            points=candidate['points_mm'];witness=None
            if points:
                for a,b in zip(points,points[1:]):
                    witness=blocked(arm_box(a,b,row['arm_half_widths_world_mm']),row)
                    if witness:break
            if not points or witness:
                rejections.append(dict(group=row['name'],root=root,search=candidate,segment_witness=witness));save();continue
            row['paths']=[dict(points_mm=points,root_attachment='Actualretainednativeparent',search=candidate)]
            for i,(a,b) in enumerate(zip(points,points[1:])):
                for h in C.ANGLES if row['moving'] else (0,):
                    shape=arm_box(a,b,row['arm_half_widths_world_mm'])
                    if row['moving']:shape=C.moved(shape,C.transform(axes,row['code'],h,0,'Hip'))
                    additions[row['name']+'/arm/'+str(i)+'/'+str(h)]=(shape,(row['code'],h) if row['moving'] else None)
            break
        save();print('rooted source arm',row['name'],bool(row['paths']),'pairs',checks,flush=True)
    save()


if __name__=='__main__':run()
