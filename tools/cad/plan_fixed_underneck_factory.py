"""Single uncut factory flex to a fixed under-neck receiver, before CAD.

Eliminates the moving JR, its tall arm and a second3core flex. The receiver
is allocated near the qualified neck return, not the rejected rearward body
receiver. Fail cheap on the common31yaw family before any material tests.
"""
import json, math, time
from pathlib import Path
from plan_current_joint_local_looms import solve_loop
from plan_current_moving_looms import add, sub, mul, rotation
from plan_current_mta_interfaces import line
from plan_current_main_sources import ROOT, BASE, SHA

OUT=BASE/'head-wiring-checkpoint'
END=[-214.,-20.,87.68206931238267]
TAIL=60.
START=[-176.,47.21874542459709,153.5]
PIVOT=[-152.,-5.25,25.]


def family():
    previous=json.loads((OUT/'neck-factory-plan.json').read_text())
    prefix=previous['factory']['qualified_exit_length_mm']
    free=250-prefix-18-TAIL
    poses=[];failures=[]
    for yaw in (-15,15,0,*[i for i in range(-14,15) if i!=0]):
        anchor=add(PIVOT,rotation(sub(START,PIVOT),[0,0,1],yaw))
        axis=rotation([0,1,0],[0,0,1],yaw)
        first=add(anchor,mul(axis,9));last=add(END,[0,9,0])
        bend_end=add(last,[0,TAIL,0]);best=None
        # Solve handles of ONE topology/receiver/constant factory length.
        # Not a receiver-position or cable-length search.
        for handle in (44,48,52,56,60,64,68,72):
            q=solve_loop(first,axis,bend_end,[0,-1,0],length=free,first_candidates=(handle,))
            if q and q['sampled_minimum_R_mm']>=31.5 and (best is None or q['sampled_minimum_R_mm']>best['sampled_minimum_R_mm']):best=q
        if best is None:
            failures.append(dict(yaw=yaw,cause='Fixed250mm length and both9mm lands do not yieldR31.5 in this single U+60mm-tail family'))
            break
        parts=[line(anchor,first),best,line(bend_end,last),line(last,END)]
        poses.append(dict(yaw=yaw,parts=parts,minimum_R_mm=best['sampled_minimum_R_mm']))
        print('Fixed under-neck factory math',yaw,'R',round(best['sampled_minimum_R_mm'],3),flush=True)
    return dict(prefix_mm=prefix,flex_curve_mm=free,tail_mm=TAIL,poses=poses,failures=failures)


def root_datums():
    import FreeCAD as A
    import Part
    import plan_current_head_wiring as H
    reader=H.P.SavedShapes();head=H.head(reader)
    rows={}
    # Actual horizontal bearing faces, including their holes and footprints.
    # A bounding-box corner is not assumed to contain root material again.
    for name in ('YawCarrier','Foundation'):
        s=head[name];planes=[]
        for i,f in enumerate(s.Faces):
            if f.BoundBox.ZLength>1e-7:continue
            if f.Area<20:continue
            planes.append(dict(face=i,z_mm=f.CenterOfMass.z,area_mm2=f.Area,
                bounds_mm=H.bb(f),centre_mm=list(f.CenterOfMass)))
        rows[name]=dict(bounds_mm=H.bb(s),horizontal_bearings=planes)
    return rows,reader.hashes


def run():
    tick=time.monotonic();print('One fixed under-neck factory architecture, math before material',flush=True)
    data=family();clear=len(data['poses'])==31 and not data['failures']
    report=dict(status='FIXED_UNDERNECK_FACTORY_MATH_CLEAR_ROOTS_OPEN' if clear else 'REJECTED_FIXED_UNDERNECK_FACTORY_MATH',
        selected=False,native_changed=False,W2_complete=False,W3_complete=False,physical_pass=False,
        factory_mm=250,fixed_JR_entry_mm=END,fixed_JR_axis=[0,-1,0],math=data,
        scope='Whole retainedS-exit plus one factory flex and supportedFIXED JR; removes movingJR/second3coreflex and their two grips.',
        project_reservations=['Factoryflat3.5x1.8, JR30x12x10, R31.5 and both9mm lands not supplier qualification'],
        replaces_if_qualified=['Legacy outboard Forkarm','Pitch movingJR','Three pitchHELUmovingloops','All3fixedpitchapproaches'],
        remaining=['ActualfixedJR support/receiver/independentlands and fullfixed3core route allocated together',
                   'Actualhead9poses/body/currentwires and neck containment','Native replacement/assembly/stock/selection'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (Path(__file__),OUT/'neck-factory-plan.json',
            Path(__file__).with_name('plan_current_joint_local_looms.py'),Path(__file__).with_name('plan_current_moving_looms.py'))})
    if clear:
        report['actual_root_datums'],pins=root_datums();report['source_sha256'].update(pins)
    report['worker_seconds']=round(time.monotonic()-tick,3)
    (OUT/'fixed-underneck-factory-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','worker_seconds')}),flush=True)


if __name__=='__main__':run()
