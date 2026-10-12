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
from plan_low_power_station_mounts import scene,box,fuse
from plan_current_joint_local_looms import solve_loop,scene_parts
from plan_current_moving_looms import add,sub,mul,rotation
from plan_current_mta_interfaces import line
from plan_current_tail_complete import tie_x
from current_prototype_harness_scene import wire,W


def parts_at(r,angle):
    direction=[0,0,-1];end_direction=rotation([0,0,1],r['joint_axis'],angle)
    fixed=r['fixed_anchor_world_mm'];pv=r['pivot_mm']
    moving=add(pv,rotation(sub(r['moving_anchor_rest_world_mm'],pv),r['joint_axis'],angle))
    start=add(fixed,mul(direction,9));end=sub(moving,mul(end_direction,9))
    q=solve_loop(start,direction,end,end_direction,length=r['flex_length_mm'])
    return None if q is None else [line(fixed,start),q,line(end,moving)]


def allocate(rows):
    shapes={};moving={};owners={}
    def put(n,s,code=None,owner=None):
        shapes[n]=s;moving[n]=code;owners[n]=owner or n
    for leg in dict.fromkeys(r['physical_leg'] for r in rows):
        rs=[r for r in rows if r['physical_leg']==leg];r=rs[0]
        side=r['side'];front=leg.startswith('Front');code=r['cad_code']
        x=r['fixed_anchor_world_mm'][0];mx=r['moving_anchor_rest_world_mm'][0]
        def B(a,b,c,d,e,f):
            y0,y1=sorted((side*b,side*e));return box([a,y0,c,d,y1,f])
        fixed=fuse([B(x-10,45,38.52,x+10,61,43.52),
                    B(x-6,55,38.52,x+6,65,43.52),
                    B(x-6,61,25,x+6,65,43.52),
                    B(x-6,61,25,x+6,124,29)])
        jaw=B(x-10,45,-5,x+10,61,-2)
        for dx in (-4,4):
            hole=Part.makeCylinder(1.7,60,A.Vector(x+dx,side*55,-12))
            fixed=fixed.cut(hole);jaw=jaw.cut(hole)
            screw=Part.makeCylinder(1.5,55,A.Vector(x+dx,side*55,-10.98)).fuse(
                Part.makeCylinder(2.75,3,A.Vector(x+dx,side*55,44.02)))
            put(leg+'Screw'+str(dx),screw)
            for tag,z in [('UpperWasher',43.52),('LowerWasher',-5.5)]:
                put(leg+tag+str(dx),Part.makeCylinder(3.5,.5,A.Vector(x+dx,side*55,z)).cut(
                    Part.makeCylinder(1.6,.5,A.Vector(x+dx,side*55,z))))
            pts=[A.Vector(x+dx+3.2*math.cos(i*math.pi/3),side*55+3.2*math.sin(i*math.pi/3),-7.9) for i in range(7)]
            nut=Part.Face(Part.makePolygon(pts)).extrude(A.Vector(0,0,2.4)).cut(
                Part.makeCylinder(1.5,2.4,A.Vector(x+dx,side*55,-7.9)))
            put(leg+'Nut'+str(dx),nut)
        # The low-X face of each actual case stays outside its Knee motor.
        # A single replaceable case band + keyed cap, not two colliding bands.
        beam_x0,beam_x1=(mx-22,mx-19) if front else (mx-19,mx-16)
        cuff=fuse([B(mx-18,7,32.2,mx+6,32,36.2),
                   B(mx-22,25,32.2,mx-14,32,40),
                   B(beam_x0,25,36,beam_x1,124,40)])
        shim=B(mx-17,8,31.7,mx+5,24,32.2)
        put(leg+'CaseShim',shim,code)
        y0,y1=sorted((side*3.229,side*60.731442))
        band,head=tie_x(mx-16.5,y0,y1,-3.480805,37.7,head_north=side<0)
        cuff=cuff.cut(band)
        put(leg+'CaseBand',band,code);put(leg+'CaseBandHead',head,code)
        for lane,row in enumerate(rs):
            yy=abs(row['fixed_anchor_world_mm'][1])
            for kind,xx,positive in [('Fixed',x,front),('Moving',mx,not front)]:
                p0,p1=(xx+3,xx+6) if positive else (xx-6,xx-3)
                post=B(p0,yy-2,21,p1,yy+2,29 if kind=='Fixed' else 40)
                if kind=='Fixed':fixed=fixed.fuse(post)
                else:cuff=cuff.fuse(post)
                x0,x1=(xx-4.2,xx+7.2) if positive else (xx-7.2,xx+4.2)
                b=B(x0,yy-4.2,24.25,x1,yy+4.2,26.75).cut(
                    B(x0+1.2,yy-3,24.1,x1-1.2,yy+3,26.9))
                h=B(x1 if positive else x0-4.5,yy-2.4,23.75,
                    x1+4.5 if positive else x0,yy+2.4,27.25)
                if kind=='Fixed':fixed=fixed.cut(b)
                else:cuff=cuff.cut(b)
                put(leg+kind+'Band'+str(lane),b,None if kind=='Fixed' else code)
                put(leg+kind+'BandHead'+str(lane),h,None if kind=='Fixed' else code)
        put(leg+'FixedArm',fixed.removeSplitter());put(leg+'LowerJaw',jaw)
        put(leg+'MovingCuff',cuff.removeSplitter(),code)
    return shapes,moving,owners


def run():
    start=time.monotonic();hf=OUT/'side-hip-arches-plan.json';kf=OUT/'joint-local-knee-plan.json'
    rows=copy.deepcopy(json.loads(hf.read_text())['loops']);knees=json.loads(kf.read_text())['loops']
    for r in rows:
        r.pop('poses',None)
        r['fixed_anchor_world_mm'][2]=30;r['moving_anchor_rest_world_mm'][2]=30
        r['recipe']='LOW DOWNWARD XZ FLEX, fixed DOWN/moving UP, retained three independent cables'
    report=dict(status='PENDING',contacts=[],errors=[],pairs=0,cases=0,math_poses=0,
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        continuous_motion_proved=False,approved_motion_limits=False,
        provisional=['OD6/R31 and +/-15 degree sampling are project assumptions, not delivered qualification',
          'Keyed cuff fit, one cuttable T18R case strap, 0.5mm shim/load/PETG creep need phase2 trial',
          'M3x55/washer/nut envelopes; final SKU and all wire grips/joins remain open'],
        assembly=['Fit fixed split clamps to P0 side rails before wiring; no drilling into retained rails.',
          'Dry-fit keyed moving cap and shim; strap on idle low-X case side, head inward, not over shaft/connector.',
          'Install three nine-mm jacket lands per side, six independent straps per leg; leave joint-local flex free.',
          'Deep removal by cutting replaceable straps before removing each cap; no quick-service promise.'])
    # A bounded common length is solved once for the whole four-leg family.
    trials=[];chosen=None
    for length in range(125,186,5):
        for r in rows:r['flex_length_mm']=length
        good=all(parts_at(r,a) is not None for r in rows for a in (-15,0,15))
        trials.append(dict(length_mm=length,all_extrema_feasible=good))
        if good:chosen=length;break
    if chosen is None:report['errors'].append('No common fixed-length/R31 solution in125..185mm')
    report['common_length_trials']=trials
    targets,old,archive=scene()
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';zf=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={q['name']:q['stage'].split('_')[1:] for q in members if q['stage'].startswith('Motion_')}
    supports,assigned,owners=allocate(rows);cache={};seen=set()
    def cached(key,fn):
        if key not in cache:cache[key]=fn()
        return cache[key]
    def moved(s,t):
        q=s.copy();q.Placement=t*q.Placement;return q
    def test(n,s,m,t,rs=0,rt=0):
        if not W.near(s,t,rs+rt+.001):return
        key=(id(s),id(t),rs,rt)
        if key in seen:return
        seen.add(key);report['pairs']+=1
        if not s.isValid() or not t.isValid():report['errors'].append([n,m]);return
        gap=s.distToShape(t)[0]
        v=0 if rs+rt or gap>1e-5 else s.common(t).Volume
        if (rs+rt and gap<rs+rt-1e-4) or v>1e-5:
            report['contacts'].append(dict(a=n,b=m,gap_mm=gap,volume_mm3=v))
    ground=min(t.BoundBox.ZMin for n,t in targets.items()
               if n.startswith('P0_') and membership.get(n[3:],['',''])[-1]=='Ankle')
    report['rest_foot_ground_z_mm']=ground;report['minimum_cable_to_rest_ground_mm']=1e9
    if not report['errors']:
        for r in rows:
            r['guide_mm']=chosen+18
            for a in range(-15,16):
                q=parts_at(r,a);report['math_poses']+=1
                if q is None:report['errors'].append([r['section'],a,'No radius solution'])
        for leg in dict.fromkeys(r['physical_leg'] for r in rows):
            family=[r for r in rows if r['physical_leg']==leg];code=family[0]['cad_code']
            for h,k,a in [(0,0,0)]+[p for p in itertools.product((-15,0,15),repeat=3) if p!=(0,0,0)]:
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
                active=[(r['section'],curves[r['section']],3) for r in family]
                active += [(n,s,0) for n,s in ss.items() if n.startswith(leg)]
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
                names=list(ss)
                for i,n in enumerate(names):
                    for m in names[i+1:]:test(n,ss[n],m,ss[m])
                if report['contacts'] or report['errors']:break
            print('low family',leg,'cases',report['cases'],'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
            # At least nominal on every leg is useful to reject the architecture
            # as a whole, but do not spend27poses repeating a known failure.
    report.update(status='REJECTED_LOW_HIP_SHARED_LAYOUT' if report['contacts'] or report['errors']
        else 'LOW_HIP_SHARED_LAYOUT_SAMPLED_CLEAR_NATIVE_FULL_JOINS_OPEN',loops=rows,
        worker_seconds=round(time.monotonic()-start,3),
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (archive,hf,kf,af,zf,Path(__file__))})
    (OUT/'low-hip-shared-layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','cases','math_poses','pairs','contacts','errors','worker_seconds','minimum_cable_to_rest_ground_mm')}),flush=True)


if __name__=='__main__':run()
