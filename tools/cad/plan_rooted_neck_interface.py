"""Coupled lower-neck JR, factory lead, rooted support and yaw departure.

No selected geometry is changed. Retain the qualified S exit; replace the
outboard JR arm by a supported under-neck assembly before detailed CAD.
All radius/packing/JR sizes remain explicit prototype reservations.
"""
import json, math, time
from pathlib import Path
import FreeCAD as A
import Part
import plan_head_neck_factory as F
import plan_current_head_wiring as H
import plan_current_head_anchor as K
import plan_low_power_station_mounts as S
import plan_current_data_ground_mounts as D
from plan_current_moving_looms import curve_length, metrics
from exact_pair_receipts import PairReceipts
from open_prototype_head_preflight import flatten, HEAD as ORIGINAL, SHIFT

OUT=H.OUT
V=A.Vector
R=40.
FIXED=V(-110,-30,120)


def factory():
    prefix=F.centerline_edges()[:2]
    for e in prefix:e.translate(SHIFT)
    a=prefix[-1].valueAt(prefix[-1].LastParameter)
    end=a+V(-R,0,-math.sqrt(3)*R)
    elbow=Part.Arc(a,(a+end)*.5+V(0,R,0),end).toShape()
    length=250-sum(e.Length for e in prefix)-elbow.Length
    terminal=end-V(0,length,0)
    shapes,meta=F.allocation(60)
    shapes={n:q for n,q in shapes.items() if n.startswith('Qualified')}
    shapes.update(NeckReturn=(elbow,math.hypot(3.5,1.8)/2),
        FactoryTail=(Part.makeLine(end,terminal),math.hypot(3.5,1.8)/2),
        JRPair=(H.T.box([terminal.x-6,terminal.y-30,terminal.z-5,
                         terminal.x+6,terminal.y,terminal.z+5]),0))
    jr=terminal-V(0,30,0)
    land=jr-V(0,9,0)
    centre=land+V(14,0,0)
    turn=centre-V(0,14,0)
    midway=centre+V(-14/math.sqrt(2),-14/math.sqrt(2),0)
    endgrip=turn+V(9,0,0)
    departure=Part.Wire([Part.makeLine(jr,land),Part.Arc(land,midway,turn).toShape(),Part.makeLine(turn,endgrip)])
    shapes['RigidDeparture']=(departure,2.27) # all3OD2.1 triangle reservation
    meta.update(return_radius_mm=R,free_tail_mm=length,
        factory_terminal_mm=list(terminal),JR_bounds_mm=H.bb(shapes['JRPair'][0]),
        JR_exit_mm=list(jr),moving_grip_mm=list(endgrip),
        change='Complete coupled JR+14mm rigid departure+near-neck receiver, not another isolated factory radius variation.',
        rigid_departure_radius_mm=14,full_factory_mm=250)
    return shapes,meta,endgrip


def supports(meta):
    x,y,z=meta['JR_exit_mm']
    # Union root into the retained Fork, not a floating stand or cosmetic skin.
    pads={
        'ForkRoot':[-206,25,123,-202,29,127],
        'ForkPost':[-206,25,z-8,-202,29,127],
        'SeatBridge':[x-8,25,z-8,-202,29,z-5],
        'JRSeat':[x-8,y,z-8,x+8,29,z-5],
        'DepartLand':[x-8,y-10,z-8,x+8,y,z-5],
        'DepartureReturn':[x-8,y-25,z-8,x+25,y-10,z-5],
        'FixedRoot':[-115,-35,103,-107,-25,107],
        'FixedPost':[-115,-35,103,-107,-25,117.73],
        'FixedLand':[-120,-35,117.73,-107,-25,119.73],
    }
    return {n:H.T.box(b) for n,b in pads.items()},pads


def curve(start,axis,end,handle):
    c=Part.BezierCurve()
    c.setPoles([start,start+axis*handle,end-V(handle,0,0),end])
    return c.toShape()


def shared_guides(start):
    # Set the common length from the whole yaw family, not hand-picked
    # length grids. Equal handles provide a single reproducible S topology.
    rows=[];seeds=[]
    for yaw in range(-15,16):
        p=H.moved(Part.Vertex(start),yaw).Point
        axis=A.Rotation(V(0,0,1),yaw).multVec(V(1,0,0))
        end=FIXED-V(9,0,0)
        seeds.append((yaw,p,axis,end,curve(p,axis,end,45).Length))
    target=math.ceil(max(q[4] for q in seeds)*10)/10+.1
    paths={}
    for yaw,p,axis,end,_ in seeds:
        lo,hi=1.,180.
        if not curve(p,axis,end,lo).Length<=target<=curve(p,axis,end,hi).Length:
            rows.append(dict(yaw=yaw,error='Common length outside equal-handle S family'));continue
        for _ in range(36):
            mid=(lo+hi)/2
            if curve(p,axis,end,mid).Length<target:lo=mid
            else:hi=mid
        e=curve(p,axis,end,(lo+hi)/2)
        minimum=min(1/e.curvatureAt(i/360) if e.curvatureAt(i/360)>1e-12 else 1e12 for i in range(361))
        rows.append(dict(yaw=yaw,length_mm=e.Length,handle_mm=(lo+hi)/2,
            minimum_sampled_radius_mm=minimum,bounds_mm=H.bb(e)))
        paths[yaw]=e
    return paths,rows,target


def fixed_approach():
    # Three conductors must be transported together along this common
    # centreline. This is only a space reservation until individual lengths,
    # packing and source-to-anchor continuity have all been qualified.
    line,arc=H.T.line,H.T.arc
    p=[line([-121,42,136],[-130,42,136]),
       arc([-130,28,136],[-130,42,136],[-144,28,136]),
       line([-144,28,136],[-144,-44,136]),
       arc([-130,-44,136],[-144,-44,136],[-130,-58,136])]
    p+=H.T.shift(p[-1]['end'],[1,0,0],[0,0,-1],16)
    x=p[-1]['end'][0]
    p+=[arc([x,-44,120],[x,-58,120],[x+14,-44,120]),
        arc([x,-44,120],[x+14,-44,120],[x,-30,120]),
        line([x,-30,120],list(FIXED))]
    return H.T.wire(p),p


def run():
    tick=time.monotonic();report=dict(status='PENDING',selected=False,
        native_changed=False,W2_complete=False,W3_complete=False,physical_pass=False,
        contacts=[],errors=[],pairs=0,poses=0,
        replaces=['Outboard Fork JR/splice arm toY134','Pitch factory return/tail/JR',
                  'All3pitch yaw-flex paths and all3fixed receiving approaches'],
        retains=['Qualified actual S factory exit','All yaw servo wiring','Head skins, mechanics and P0',
                 'SelectedW2/M2/W3 until a complete qualified replacement exists'],
        assumptions=['Uncut250mm factory; nominal flat3.5x1.8 and JR30x12x10 not delivered measurements',
          '3coreOD2.1 triangle and fixedR12.6/movingR31.5 project reservations',
          'Guide centreR33 includes1.212mm packing allowance; individual full conductor family still required',
          'Root strength, independent bands, skins/neck containment, installation and stock remain OPEN'])
    parts,meta,start=factory();report['factory']=meta
    roots,pads=supports(meta);report['support_pads']=pads
    paths,rows,target=shared_guides(start)
    report['yaw_guide_family']=rows;report['guide_target_mm']=target
    report['math_clear']=len(paths)==31 and min(q.get('minimum_sampled_radius_mm',0) for q in rows)>=33
    approach,recipe=fixed_approach();report['fixed_approach_centreline']=recipe
    report['fixed_approach_individual_conductors_qualified']=False
    # A failed curve family is retained. Independently test the whole physical
    # JR/root topology before detail; no implication of full harness approval.
    reader=H.P.SavedShapes()
    fork=flatten(reader,ORIGINAL,'HeadNoseInsertUnit')['Fork'][0];fork.translate(SHIFT)
    fork=fork.cut(H.T.box([-195,20.5,152.25,-180,32,154.65]))
    assert fork.isValid() and len(fork.Solids)==1
    carrier=H.head(reader)['YawCarrier']
    report['root_actual_common_mm3']={
        'ForkRoot':roots['ForkRoot'].common(fork).Volume,
        'FixedRoot':roots['FixedRoot'].common(carrier).Volume}
    targets,old,archive=S.scene()
    for n in list(targets):
        if n.startswith('head/') or 'HeadAnchor' in n or 'StationShoe' in n or 'TopClamp' in n:targets.pop(n)
    # New station supports replace their candidate predecessors, not P0.
    newstation,hardware,bonds,stationmeta=D.allocate(targets)
    targets.update({'station/'+n:s for n,s in newstation.items()})
    targets.update({'station/'+n:s for n,s in hardware.items()})
    cache=PairReceipts(OUT/'rooted-neck-interface-pairs.json',S.W.near)
    def test(n,s,rad,m,t,tr=0,pose=None):
        if not S.W.near(s,t,rad+tr+.001):return
        report['pairs']+=1
        try:gap,volume=cache.check(s,t,rad,tr)
        except (ValueError,AssertionError) as e:report['errors'].append([n,m,str(e)]);return
        if gap<rad+tr-1e-4 or volume>1e-5:
            report['contacts'].append(dict(a=n,b=m,pose=pose,gap_mm=gap,volume_mm3=volume))
    movingroots={n:s for n,s in roots.items() if not n.startswith('Fixed')}
    fixedroots={n:s for n,s in roots.items() if n.startswith('Fixed')}
    for yaw in (-15,0,15):
        current={**{n:(H.moved(s,yaw),r) for n,(s,r) in parts.items()},
                 **{n:(H.moved(s,yaw),0) for n,s in movingroots.items()},
                 **{n:(s,0) for n,s in fixedroots.items()},'FixedApproachReservation':(approach,2.27)}
        if report['math_clear']:current['YawGuideReservation']=(paths[yaw],2.27)
        for pitch in (-10,0,5):
            head=H.head(reader,yaw,pitch);head['Fork']=H.moved(fork,yaw)
            for n,(s,r) in current.items():
                for m,t in head.items():
                    if (n=='ForkRoot' and m=='Fork') or (n=='FixedRoot' and m=='YawCarrier'):continue
                    test(n,s,r,'head/'+m,t,pose=[yaw,pitch])
            report['poses']+=1
        for n,(s,r) in current.items():
            for m,t in targets.items():
                if t.Solids:test(n,s,r,m,t,pose=[yaw,0])
            for m,(t,tr) in old.items():
                if 'wire/head/' in m and any('/'+q+'/' in m for q in ('XB22','XB23','XS23')):continue
                test(n,s,r,m,t,tr,pose=[yaw,0])
        cache.save()
        print('Rooted whole-neck yaw',yaw,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True)
    # Explicit reservations also test support vs wires and each other. Only
    # adjacent joined pads are intended unions, not unrelated contact waivers.
    for n,(s,r) in parts.items():
        for m,t in roots.items():test(n,s,r,m,t,pose=[0,0])
    for n,t in fixedroots.items():test(n,t,0,'MovingForkAssembly',S.fuse(list(movingroots.values())))
    for n,(s,r) in parts.items():test(n,s,r,'FixedApproachReservation',approach,2.27)
    report.update(status='COUPLED_NECK_SPACE_CANDIDATE_DETAIL_OPEN' if report['math_clear'] and
        not report['contacts'] and not report['errors'] and min(report['root_actual_common_mm3'].values())>0 else
        'REJECTED_COUPLED_NECK_LAYOUT',worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**reader.hashes,**meta['source_sha256'],
            **{p.relative_to(H.ROOT).as_posix():H.P.sha(p) for p in (Path(__file__),Path(F.__file__),Path(D.__file__),archive)}})
    H.save('rooted-neck-interface-plan.json',report)
    print(json.dumps({k:report[k] for k in ('status','math_clear','root_actual_common_mm3','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
