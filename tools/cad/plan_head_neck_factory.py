"""Whole uncut pitch factory lead/JR in neck space, not a skull storage coil.

Changes the failed storage topology. The servo and this lead are yaw-owned,
not pitch-owned. A new three-core yaw transition and rooted JR support are
still required before replacing any selected W2/M2 geometry.
"""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
import plan_current_head_wiring as H
import check_low_hip_loom_layout as P
from open_prototype_head_preflight import flatten,HEAD as ORIGINAL,SHIFT
from exact_pair_receipts import PairReceipts
from head_factory_lead_storage_r2 import centerline_edges


def allocation(plane_degrees=60.):
    # Reuse the already qualified S-shaped factory exit. A guessed straight
    # prefix crosses the Fork/retainer and misses the actual head port.
    prefix=centerline_edges()[:2]
    for edge in prefix:edge.translate(SHIFT)
    a=prefix[-1].valueAt(prefix[-1].LastParameter)
    prefix_length=sum(edge.Length for edge in prefix)
    radius=38.;phi=math.radians(plane_degrees)
    delta=A.Vector(-2*radius*math.cos(phi),0,-2*radius*math.sin(phi))
    center=a+delta*.5;end=a+delta
    elbow=Part.Arc(a,center+A.Vector(0,radius,0),end).toShape()
    remaining=250-prefix_length-elbow.Length;assert remaining>9
    terminal=end-A.Vector(0,remaining,0)
    tail=Part.makeLine(end,terminal)
    assert abs(prefix_length+elbow.Length+tail.Length-250)<1e-6
    assert elbow.tangentAt(elbow.FirstParameter).dot(A.Vector(0,1,0))>1-1e-7
    assert elbow.tangentAt(elbow.LastParameter).dot(A.Vector(0,-1,0))>1-1e-7
    retained={}
    pins={}
    for i in range(2):
        p=P.ROOT/f'hardware/electronics/full-cat/head-factory-lead-local-profiles-r1/FlatLead{i}.brep'
        assert p.exists(),('Missing qualified flat exit component',i)
        s=Part.read(str(p));s.translate(SHIFT);assert s.isValid() and s.Solids
        retained['QualifiedFlatExit'+str(i)]=(s,0);pins[p.relative_to(P.ROOT).as_posix()]=P.SHA(p)
    jr=H.T.box([terminal.x-6,terminal.y-30,terminal.z-5,terminal.x+6,terminal.y,terminal.z+5])
    return {**retained,'NeckReturn':(elbow,math.hypot(3.5,1.8)/2),
            'FactoryTail':(tail,math.hypot(3.5,1.8)/2),'JRPair':(jr,0)},dict(
        full_factory_mm=250,qualified_exit_length_mm=prefix_length,return_radius_mm=radius,
        return_plane_degrees_down_from_front=plane_degrees,
        free_tail_mm=remaining,factory_terminal_mm=list(terminal),JR_bounds_mm=H.bb(jr),
        flat_exit_mm=[3.5,1.8],factory_flat_and_JR_dimensions_provisional=True,
        JR_basis='Inherited nominal mating-pair30x12x10, not delivered measurement',
        source_sha256=pins,
        change='Retain qualified25mm S-exit through existing head port, then broad38mm descending neck return instead of skull coil/protruding arm. No shorter lead, hidden part or wider torso.')


def run():
    tick=time.monotonic();reader=H.P.SavedShapes()
    fork=flatten(reader,ORIGINAL,'HeadNoseInsertUnit')['Fork'][0];fork.translate(SHIFT)
    fork=fork.cut(H.T.box([-195,20.5,152.25,-180,32,154.65]))
    assert fork.isValid() and len(fork.Solids)==1
    targets,old,archive=P.scene();cache=PairReceipts(P.OUT/'head-neck-factory-pair-cache.json',P.W.near)
    heads={}
    for yaw in (-15,0,15):
        for pitch in (-10,0,5):
            head=H.head(reader,yaw,pitch);head['Fork']=H.moved(fork,yaw)
            heads[yaw,pitch]=head
    # One bounded shared-plane allocation, not authored position variants.
    # Probe both tail/JR AND return at all head poses and with the complete
    # fixed scene before spending time on the full qualifying receipt.
    trials=[];chosen=None
    for angle in (60.,45.,30.):
        parts,meta=allocation(angle);hit=None;count=0
        for yaw in (15,-15,0):
            for n in ('JRPair','FactoryTail','NeckReturn'):
                s,rad=parts[n];s=H.moved(s,yaw)
                candidates=[]
                for pitch in (-10,0,5):
                    candidates.extend(('head/'+m,t,0,[yaw,pitch]) for m,t in heads[yaw,pitch].items())
                candidates.extend((m,t,0,[yaw,0]) for m,t in targets.items() if t.Solids)
                candidates.extend((m,t,tr,[yaw,0]) for m,(t,tr) in old.items()
                    if not ('wire/head/' in m and any(f'/{q}/' in m for q in ('XB22','XB23','XS23'))))
                for m,t,tr,pose in candidates:
                    if not P.W.near(s,t,rad+tr+.001):continue
                    count+=1;gap,volume=cache.check(s,t,rad,tr)
                    if gap<rad+tr-1e-4 or volume>1e-5:
                        hit=dict(a=n,b=m,pose=pose,gap_mm=gap,volume_mm3=volume);break
                if hit:break
            if hit:break
        trials.append(dict(plane_degrees=angle,pairs=count,first_conflict=hit))
        cache.save();print('shared neck plane',angle,'pairs',count,'blocked',hit,flush=True)
        if hit is None:chosen=angle;break
    report=dict(status='PENDING',contacts=[],errors=[],pairs=0,poses=0,selected=False,
        native_changed=False,W2_complete=False,physical_pass=False,head_containment_proved=False,
        factory=meta,plane_allocation_trials=trials,chosen_plane_degrees=chosen,
        excluded_replacement_geometry='Old pitch rigid/flex/current wires are replaced by this new complete factory/JR plus FUTURE 3core transition, not silently retained. No full W2 claim.',
        remaining=['Native supported JR and independent intact-insulation restraints',
                   'Complete constant-length3core yaw transition to current W3 boundary with actual radii/ends',
                   'Whole assembly/motion/stock/head-and-neck envelope and native replacement'])
    def test(n,s,rad,m,t,tr=0,pose=None):
        if not P.W.near(s,t,rad+tr+.001):return
        report['pairs']+=1
        try:gap,volume=cache.check(s,t,rad,tr)
        except (AssertionError,ValueError) as e:report['errors'].append([n,m,str(e)]);return
        if gap<rad+tr-1e-4 or volume>1e-5:
            report['contacts'].append(dict(a=n,b=m,pose=pose,gap_mm=gap,volume_mm3=volume))
    for yaw in ((-15,0,15) if chosen is not None else ()):
        moved={n:(H.moved(s,yaw),r) for n,(s,r) in parts.items()}
        for pitch in (-10,0,5):
            head=heads[yaw,pitch]
            report['poses']+=1
            for n,(s,r) in moved.items():
                for m,t in head.items():test(n,s,r,'head/'+m,t,pose=[yaw,pitch])
        for n,(s,r) in moved.items():
            for m,t in targets.items():
                if t.Solids:test(n,s,r,m,t,pose=[yaw,0])
            for m,(t,tr) in old.items():
                if any(f'/{q}/' in m for q in ('XB22','XB23','XS23')) and 'wire/head/' in m:continue
                test(n,s,r,m,t,tr,pose=[yaw,0])
        cache.save();print('whole neck factory yaw',yaw,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True)
    report.update(status='NECK_FACTORY_JR_MATERIAL_SCREEN_CLEAR_TRANSITION_NATIVE_OPEN' if chosen is not None and not report['contacts'] and not report['errors'] else 'REJECTED_NECK_FACTORY_JR_PLAN',
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**meta['source_sha256'],
            **{p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (archive,Path(__file__),Path(H.__file__),P.ROOT/'tools/electronics/head_factory_lead_storage_r2.py')}})
    H.save('neck-factory-plan.json',report)
    print(json.dumps({k:report[k] for k in ('status','poses','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
