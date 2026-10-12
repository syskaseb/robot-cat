"""Shared low Hip-flex layout and its real clamp/cuff allocations.

Reject/accept SPACE before building native detail. Retained P0 material is
transformed with its actual Hip/Knee/Ankle membership; no stale rest-pose
substitution. R31/OD6/9mm lands and a fixed common length remain explicit
project assumptions. Not a selected harness or a continuous sweep proof.
"""
import copy,itertools,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT,OUT,SHA
from plan_low_power_station_mounts import scene,box,fuse,allocate as station_supports
from plan_low_joint_loom_family import hip_parts as parts_at
from plan_current_joint_local_looms import solve_loop,scene_parts
from plan_current_moving_looms import add,sub,mul,rotation
from plan_current_mta_interfaces import line
from plan_current_tail_complete import tie_x
from current_prototype_harness_scene import wire,W
from exact_pair_receipts import PairReceipts


def rejected_old_parts_at(r,angle):
    direction=[0,0,-1];end_direction=rotation([0,0,1],r['joint_axis'],angle)
    fixed=r['fixed_anchor_world_mm'];pv=r['pivot_mm']
    moving=add(pv,rotation(sub(r['moving_anchor_rest_world_mm'],pv),r['joint_axis'],angle))
    start=add(fixed,mul(direction,9));end=sub(moving,mul(end_direction,9))
    q=solve_loop(start,direction,end,end_direction,length=r['flex_length_mm'])
    return None if q is None else [line(fixed,start),q,line(end,moving)]


def allocate(rows,targets,with_recipe=False):
    shapes={};moving={};owners={};recipe={}
    cp=json.loads((OUT/'joint-support-corridors-plan.json').read_text())
    assert cp['status']=='FOUR_ROOT_CORRIDORS_SCREEN_CLEAR_BREP_MOTION_OPEN'
    for n,h in cp['source_sha256'].items():assert SHA(ROOT/n)==h,n
    retained_shoes,_,station_recipe=station_supports(targets)
    def put(n,s,code=None,owner=None):
        shapes[n]=s;moving[n]=code;owners[n]=owner or n
    for leg in dict.fromkeys(r['physical_leg'] for r in rows):
        rs=[r for r in rows if r['physical_leg']==leg];r=rs[0]
        side=r['side'];front=leg.startswith('Front');code=r['cad_code']
        x=r['fixed_anchor_world_mm'][0];mx=r['moving_anchor_rest_world_mm'][0]
        clamp_x=40 if front else 115
        short={'FrontLeft':'FL','FrontRight':'FR','RearLeft':'RL','RearRight':'RR'}[leg]
        def bounds(a,b,c,d,e,f):
            y0,y1=sorted((side*b,side*e));return [a,y0,c,d,y1,f]
        def B(*v):return box(bounds(*v))
        # Same four proven current P-station clamps, not four extra clamps
        # under F0/splice. Replace their top caps, preserve their native shoes.
        # Crown ABOVE the downward land/departure. The entire transverse
        # bridge goes outside F0/splice, not through their occupied corridor.
        route=next(v['points_mm'] for v in cp['roots'] if v['leg']==leg)
        fp=[dict(bounds_mm=bounds(clamp_x-10,45,38.52,clamp_x+10,61,43.52))]
        fp.append(dict(bounds_mm=bounds(clamp_x-3,59,38.52,clamp_x+3,65,43.52)))
        fp += [dict(bounds_mm=[min(a[i],b[i])-3 for i in range(3)]+[max(a[i],b[i])+3 for i in range(3)]) for a,b in zip(route,route[1:])]
        fp.append(dict(bounds_mm=bounds(x+3,88,36,x+6,128,40),length_expression='CrownParameters.Thickness'))
        fixed=fuse([box(v['bounds_mm']) for v in fp])
        jaw=retained_shoes[short+'StationShoe']
        for suffix in ('BottomBond','BackBond'):put(leg+suffix,retained_shoes[short+suffix])
        for dx in (-4,4):
            cx=clamp_x+dx
            hole=Part.makeCylinder(1.7,60,A.Vector(cx,side*55,-12))
            fixed=fixed.cut(hole);jaw=jaw.cut(hole)
            screw=Part.makeCylinder(1.5,55,A.Vector(cx,side*55,-10.98)).fuse(
                Part.makeCylinder(2.75,3,A.Vector(cx,side*55,44.02)))
            put(leg+'Screw'+str(dx),screw)
            for tag,z in [('UpperWasher',43.52),('LowerWasher',-5.5)]:
                put(leg+tag+str(dx),Part.makeCylinder(3.5,.5,A.Vector(cx,side*55,z)).cut(
                    Part.makeCylinder(1.6,.5,A.Vector(cx,side*55,z))))
            pts=[A.Vector(cx+3.2*math.cos(i*math.pi/3),side*55+3.2*math.sin(i*math.pi/3),-7.9) for i in range(7)]
            nut=Part.Face(Part.makePolygon(pts)).extrude(A.Vector(0,0,2.4)).cut(
                Part.makeCylinder(1.5,2.4,A.Vector(cx,side*55,-7.9)))
            put(leg+'Nut'+str(dx),nut)
        # The low-X face of each actual case stays outside its Knee motor.
        # A single replaceable case band + keyed cap, not two colliding bands.
        beam_x0,beam_x1=(mx-22,mx-19) if front else (mx+19,mx+22)
        cap0,cap1=(mx-18,mx+6) if front else (mx-18,mx+18)
        root0,root1=(mx-22,mx-14) if front else (mx+14,mx+22)
        rung0,rung1=(mx-22,mx+6) if front else (mx-6,mx+22)
        # Inboard bearing patch remains inside the frame screw corridor
        # throughout Hip sampling, rather than clearing only its rest pose.
        # Actual frame witness at Hip+15 reached local Z32.3493670273.
        # Relieve the root's lower edge over its full width with0.5mm margin;
        # retain the separate case bearing patch and upper joined load path.
        root_z=32.349367027314756+.5 if front else 32.2
        # Use the WHOLE fixed-head-wire bounding lower envelope, not only
        # the previous witness point. XS13 minY-98/minZ55.8, FR pivot
        # (-16,18.51), inverse Hip15 gives a conservative local minZ.
        # Keep outboard spine below its1.05mm jacket plus0.5mm margin.
        # Only the near-case beam remains above the sampled Knee member.
        crown_top=18.51+math.cos(math.radians(15))*(55.8-18.51)-math.sin(math.radians(15))*(98-16)-1.05-.5
        crown_bottom=crown_top-4
        short0,short1=(mx-6,mx-3) if front else (mx+3,mx+6)
        bridge0,bridge1=(beam_x0,short1) if front else (short0,beam_x1)
        mp=[dict(bounds_mm=bounds(cap0,7,32.2,cap1,16,36.2),length_expression='CrownParameters.Thickness'),
            dict(bounds_mm=bounds(root0,12,root_z,root1,16,40),length_expression=f'{36-root_z} mm + CrownParameters.Thickness'),
            dict(bounds_mm=bounds(beam_x0,12,36,beam_x1,84,40),length_expression='CrownParameters.Thickness'),
            dict(bounds_mm=bounds(beam_x0,80,crown_bottom,beam_x1,84,40),length_expression=f'{36-crown_bottom} mm + CrownParameters.Thickness'),
            dict(bounds_mm=bounds(bridge0,80,crown_bottom,bridge1,84,crown_top),length_expression='CrownParameters.Thickness'),
            dict(bounds_mm=bounds(short0,80,crown_bottom,short1,128,crown_top),length_expression='CrownParameters.Thickness')]
        cuff=fuse([box(v['bounds_mm']) for v in mp])
        shim=B(cap0+1,8,31.7,cap1-1,15,32.2)
        put(leg+'CaseShim',shim,code)
        # The connector's lower/back projection belongs to the physical
        # member too. Idle low-X band avoids Knee on all four legs; rear
        # structural beam attaches at the opposite cap end to clear frame.
        # Head above INBOARD case edge: outer edge crosses the arm's spine.
        bx=mx-16.5
        # Real240mm T25L case strap; short T18R cannot close this case.
        # Head budgets are provisional, not supplier dimensions.
        band=B(bx-1.4,3.029,-3.680805,bx+1.4,60.931442,37.9).cut(
            B(bx-1.6,4.429,-2.280805,bx+1.6,59.531442,36.5))
        # Front external spine occupies the outer face. Rear spine is on
        # oppositeX side, while the retained body carrier occupies its inner
        # face. Allocate these two distinct rigid assemblies accordingly.
        head=B(bx-4,4 if front else 56,37.9,bx+4,12 if front else 64,43.9)
        cuff=cuff.cut(band)
        put(leg+'CaseBand',band.fuse(head).removeSplitter(),code)
        for lane,row in enumerate(rs):
            yy=abs(row['fixed_anchor_world_mm'][1])
            for kind,xx,positive in [('Fixed',x,True),('Moving',mx,not front)]:
                p0,p1=(xx+3,xx+6) if positive else (xx-6,xx-3)
                # Both posts rise to the crown, leaving flex below free.
                top=40 if kind=='Fixed' else crown_top
                post=B(p0,yy-2,21,p1,yy+2,top)
                (fp if kind=='Fixed' else mp).append(dict(bounds_mm=bounds(p0,yy-2,21,p1,yy+2,top),length_expression=f'{top-25} mm + CrownParameters.Thickness'))
                if kind=='Fixed':fixed=fixed.fuse(post)
                else:cuff=cuff.fuse(post)
                x0,x1=(xx-4.2,xx+7.2) if positive else (xx-7.2,xx+4.2)
                b=B(x0,yy-4.2,24.25,x1,yy+4.2,26.75).cut(
                    B(x0+1.2,yy-3,24.1,x1-1.2,yy+3,26.9))
                h=B(x1 if positive else x0-4.5,yy-2.4,23.75,
                    x1+4.5 if positive else x0,yy+2.4,27.25)
                if kind=='Fixed':fixed=fixed.cut(b)
                else:cuff=cuff.cut(b)
                bb=h.BoundBox;cx=(bb.XMin+bb.XMax)/2;cy=(bb.YMin+bb.YMax)/2;cz=(bb.ZMin+bb.ZMax)/2
                h=box([cx-3,cy-3,cz-2.5,cx+3,cy+3,cz+2.5])
                # Band and ratchet head are ONE purchased physical item.
                # Their intentional union must not appear as two colliding parts.
                put(leg+kind+'Band'+str(lane),b.fuse(h).removeSplitter(),None if kind=='Fixed' else code)
        put(leg+'FixedArm',fixed.removeSplitter());put(leg+'LowerJaw',jaw)
        put(leg+'MovingCuff',cuff.removeSplitter(),code)
        recipe[leg+'FixedArm']=dict(pads=fp,holes=[[clamp_x-4,side*55],[clamp_x+4,side*55]],notches=[])
        recipe[leg+'MovingCuff']=dict(pads=mp,holes=[],notches=[bounds(bx-1.4,3.029,36.5,bx+1.4,60.931442,37.9)] if front else [])
    return (shapes,moving,owners,recipe) if with_recipe else (shapes,moving,owners)


def run():
    start=time.monotonic();hf=OUT/'low-joint-family-plan.json'
    family=json.loads(hf.read_text());assert family['status']=='LOW_JOINT_FAMILY_SAMPLED_SCREEN_CLEAR_MATERIAL_ROOTS_OPEN'
    assert not family['errors'] and not family['rejected']
    for n,h in family['source_sha256'].items():assert SHA(ROOT/n)==h,n
    rows=family['hips'];knees=family['knees']
    report=dict(status='PENDING',contacts=[],errors=[],pairs=0,cases=0,math_poses=0,
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        continuous_motion_proved=False,approved_motion_limits=False,
        provisional=['OD6/R31 and +/-15 degree sampling are project assumptions, not delivered qualification',
          'Keyed cuff fit, one cuttable240mm T25L case strap, 0.5mm shim/load/PETG creep need phase2 trial',
          'Case head8x8x6 and small jacket heads6x6x5mm are project reservations, not supplier head dimensions',
          'M3x55/washer/nut envelopes; final SKU and all wire grips/joins remain open'],
        assembly=['Fit fixed split clamps to P0 side rails before wiring; no drilling into retained rails.',
          'Dry-fit keyed moving cap and shim; strap on idle low-X case side. Ratchet above inboard edge at front, outer edge at rear, avoiding spine/carrier respectively; not over shaft/connector.',
          'Install three nine-mm jacket lands per side, six independent straps per leg; leave joint-local flex free.',
          'Deep removal by cutting replaceable straps before removing each cap; no quick-service promise.'])
    chosen=rows[0]['flex_length_mm'];report['common_length_trials']=family['common_Hip_length_trials']
    report['assembly'].append('Four existing P-station shoes retained; top clamps replaced by common fixed wire arms, not duplicated. Knee flex family reflected outward together.')
    targets,old,archive=scene()
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';zf=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={q['name']:q['stage'].split('_')[1:] for q in members if q['stage'].startswith('Motion_')}
    supports,assigned,owners=allocate(rows,targets);cache={};seen=set()
    pair_gate=PairReceipts(OUT/'joint-support-pair-cache.json',W.near)
    for n,s in supports.items():
        if not s.isValid() or len(s.Solids)!=1:report['errors'].append([n,'Not one valid support/strap/hardware solid'])
    def cached(key,fn):
        if key not in cache:cache[key]=fn()
        return cache[key]
    def moved(s,t):
        q=s.copy();q.Placement=t*q.Placement;return q
    def test(n,s,m,t,rs=0,rt=0):
        if not W.near(s,t,rs+rt+.001):return
        key=(id(s),id(t),rs,rt) if id(s)<id(t) else (id(t),id(s),rt,rs)
        if key in seen:return
        seen.add(key);report['pairs']+=1
        try:gap,v=pair_gate.check(s,t,rs,rt)
        except (AssertionError,ValueError) as e:report['errors'].append([n,m,str(e)]);return
        if (rs+rt and gap<rs+rt-1e-4) or v>1e-5:
            report['contacts'].append(dict(a=n,b=m,gap_mm=gap,volume_mm3=v,pose=dict(leg=leg,Hip=h,Knee=k,Ankle=a)))
    ground=min(t.BoundBox.ZMin for n,t in targets.items()
               if n.startswith('P0_') and membership.get(n[3:],['',''])[-1]=='Ankle')
    report['rest_foot_ground_z_mm']=ground;report['minimum_cable_to_rest_ground_mm']=1e9
    if not report['errors']:
        report['reused_math_poses']=family['math_poses']
        for r in rows:r['guide_mm']=chosen+18
        legs=list(dict.fromkeys(r['physical_leg'] for r in rows))
        schedule=[(leg,[(0,0,0)]) for leg in legs]
        priority=[(15,0,0),(-15,0,0),(0,15,0),(0,-15,0),(0,0,15),(0,0,-15)]
        schedule += [(leg,priority+[p for p in itertools.product((-15,0,15),repeat=3) if p!=(0,0,0) and p not in priority]) for leg in legs]
        for leg,poses in schedule:
            if len(poses)>1 and (report['contacts'] or report['errors']):break
            family=[r for r in rows if r['physical_leg']==leg];code=family[0]['cad_code']
            for h,k,a in poses:
                report['cases']+=1;trans={};T=A.Placement()
                for stage,angle in zip(('Hip','Knee','Ankle'),(h,k,a)):
                    ax=next(v for v in axes if v['code']==code and v['stage']==stage)
                    pv=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),angle)
                    T=T*A.Placement(pv-rot.multVec(pv),rot);trans[stage]=T
                tt={}
                for n,t in targets.items():
                    member=membership.get(n.removeprefix('P0_')) if n.startswith('P0_') else None
                    if member and member[0]==code:
                        stage=member[1];angles=(h,k,a)[:('Hip','Knee','Ankle').index(stage)+1]
                        t=cached(('material',n,angles),lambda t=t,stage=stage:moved(t,trans[stage]))
                    tt[n]=t
                ss={n:cached(('support',n,h),lambda s=s:moved(s,trans['Hip']))
                    if assigned[n]==code else s for n,s in supports.items()}
                curves={r['section']:cached(('arch',r['section'],h if r['cad_code']==code else 0),
                    lambda r=r:wire(parts_at(r,h if r['cad_code']==code else 0))) for r in rows}
                kk={r['section']:cached(('knee',r['section'],h if r['cad_code']==code else 0,k if r['cad_code']==code else 0),
                    lambda r=r:wire(scene_parts(r,h if r['cad_code']==code else 0,k if r['cad_code']==code else 0,axes))) for r in knees}
                active=[(n,s,0) for n,s in ss.items() if n.startswith(leg)]
                active += [(r['section'],curves[r['section']],3) for r in family]
                active += [(r['section'],kk[r['section']],3) for r in knees if r['cad_code']==code]
                for n,s,rad in active:
                    if rad:
                        clearance=s.BoundBox.ZMin-rad-ground
                        report['minimum_cable_to_rest_ground_mm']=min(report['minimum_cable_to_rest_ground_mm'],clearance)
                        if clearance<10:report['errors'].append([n,'Less than10mm static foot-ground margin',clearance])
                    for m,t in tt.items():
                        if t.Solids:test(n,s,m,t,rad)
                    for m,(t,tr) in old.items():test(n,s,m,t,rad,tr)
                    for m,t in {**curves,**kk}.items():
                        if m!=n:test(n,s,m,t,rad,3)
                    # Full jacket rings are tangent to assigned lands, not waived.
                    if rad:
                        for m,t in ss.items():test(n,s,m,t,rad)
                    if report['contacts'] or report['errors']:break
                names=list(ss)
                for i,n in enumerate(names):
                    for m in names[i+1:]:test(n,ss[n],m,ss[m])
                if report['cases']%5==0:
                    pair_gate.save()
                    print('motion progress',leg,(h,k,a),'cases',report['cases'],'pairs',report['pairs'],'exact reused/new',pair_gate.reused,pair_gate.computed,flush=True)
                if report['contacts'] or report['errors']:break
            print('low family',leg,'cases',report['cases'],'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
            # At least nominal on every leg is useful to reject the architecture
            # as a whole, but do not spend27poses repeating a known failure.
    if report['cases']==0:report['minimum_cable_to_rest_ground_mm']=None
    pair_gate.save();report['exact_pair_receipts']=dict(reused=pair_gate.reused,computed=pair_gate.computed,checker_sha256=pair_gate.revision)
    report.update(status='REJECTED_LOW_HIP_SHARED_LAYOUT' if report['contacts'] or report['errors']
        else 'LOW_HIP_SHARED_LAYOUT_SAMPLED_CLEAR_NATIVE_FULL_JOINS_OPEN',loops=rows,
        worker_seconds=round(time.monotonic()-start,3),
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (archive,hf,af,zf,OUT/'joint-support-corridors-plan.json',ROOT/'hardware/reference/hellermann-11102519-2026-10-12/dimensions.json',Path(__file__),Path(__file__).with_name('plan_low_joint_loom_family.py'),Path(__file__).with_name('exact_pair_receipts.py'))})
    (OUT/'low-hip-shared-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','cases','math_poses','pairs','contacts','errors','worker_seconds','minimum_cable_to_rest_ground_mm')}),flush=True)


if __name__=='__main__':run()
