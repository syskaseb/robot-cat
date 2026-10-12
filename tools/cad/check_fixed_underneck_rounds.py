"""Exact material gate for the shared rounded factory family, no native edits."""
import json, time, re
from pathlib import Path
import FreeCAD as A
import Part
import plan_current_head_wiring as H
import plan_fixed_underneck_rounds as Q
import plan_head_neck_factory as F
import plan_low_power_station_mounts as S
import plan_current_data_ground_mounts as D
from exact_pair_receipts import PairReceipts
from open_prototype_head_preflight import flatten, HEAD as ORIGINAL, SHIFT


def run():
    tick=time.monotonic();p=H.read(H.OUT/'fixed-underneck-rounds-plan.json')
    assert p['status']=='ROUNDED_FACTORY_SHARED_SPACE_MATH_CLEAR_MATERIAL_OPEN'
    for n,h in p['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,n
    print('Received31rounded factory poses; load actual root faces before native',flush=True)
    reader=H.P.SavedShapes();head=H.head(reader)
    datums={}
    for n in ('YawCarrier','Foundation'):
        datums[n]=dict(bounds_mm=H.bb(head[n]),horizontal_faces=[dict(face=i,area_mm2=f.Area,
            bounds_mm=H.bb(f),centre_mm=list(f.CenterOfMass)) for i,f in enumerate(head[n].Faces)
            if f.BoundBox.ZLength<1e-7 and f.Area>20])
    print('Actual fixed root faces',json.dumps(datums),flush=True)
    targets,old,archive=S.scene()
    for n in list(targets):
        if n.startswith('head/'):targets.pop(n)
    station,hardware,bonds,_=D.allocate(targets)
    # This new Foundation snapshot includes the retained base plus pads.
    targets.pop('Foundation',None)
    targets.update({'station/'+n:s for n,s in station.items()})
    targets.update({'station/'+n:s for n,s in hardware.items()})
    fork=flatten(reader,ORIGINAL,'HeadNoseInsertUnit')['Fork'][0];fork.translate(SHIFT)
    fork=fork.cut(H.T.box([-195,20.5,152.25,-180,32,154.65]))
    assert fork.isValid() and len(fork.Solids)==1
    x,z=p['fixed_receiver_XZ_mm'];y=p['fixed_receiver_Y_mm']
    jr=H.T.box([x-6,y-30,z-5,x+6,y,z+5])
    report=dict(status='PENDING',contacts=[],errors=[],pairs=0,poses=0,selected=False,
        native_changed=False,W2_complete=False,W3_complete=False,physical_pass=False,
        actual_root_datums=datums,JR_bounds_mm=H.bb(jr),
        source_replacements=[],self_distance_open=True,
        scope='Factory250/JR plus bare retainedFork only. ROOT/3fixedwires/independentgrips/native not yet qualified.',
        profile_note='Centreline diagonal1.968mm reservation is conservative; contacts are reservation hits, not measured cable penetration.')
    cache=PairReceipts(H.OUT/'fixed-underneck-rounds-pairs.json',S.W.near)
    def test(n,s,rad,m,t,tr=0,pose=None):
        if not S.W.near(s,t,rad+tr+.001):return
        report['pairs']+=1
        try:d,v=cache.check(s,t,rad,tr)
        except (AssertionError,ValueError) as e:report['errors'].append([n,m,str(e)]);return
        if d<rad+tr-1e-4 or v>1e-5:report['contacts'].append(dict(a=n,b=m,pose=pose,gap_mm=d,volume_mm3=v))
    retired={n for n in old if re.search(r'(?:^|/)(?:XB22|XB23|XS23)(?:/|_|$)',n)}
    report['source_replacements']=sorted(retired)
    assert any('head-supply-checkpoint/' in n for n in retired),'Actual selected source labels were not matched'
    for yaw in (-15,0,15):
        row=next(q for q in p['poses'] if q['yaw']==yaw)
        edges=H.T.wire(row['parts']).Edges
        assert abs(sum(e.Length for e in edges)+p['prefix_mm']-250)<1e-5
        for a,b in zip(edges,edges[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6
            assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-6
        shapes={f'FactorySection{i}':(s,Q.RESERVE) for i,s in enumerate(edges)}
        shapes['FixedJR']=(jr,0)
        for pitch in (-10,0,5):
            current=H.head(reader,yaw,pitch);current['Fork']=H.moved(fork,yaw)
            for n,(s,r) in shapes.items():
                for m,t in current.items():test(n,s,r,'head/'+m,t,pose=[yaw,pitch])
            report['poses']+=1
        for n,(s,r) in shapes.items():
            for m,t in targets.items():
                if t.Solids:test(n,s,r,m,t,pose=[yaw,0])
            for m,(t,tr) in old.items():
                if m not in retired:test(n,s,r,m,t,tr,pose=[yaw,0])
        # The final straight intentionally enters its own JR end face;
        # earlier portions must clear the entire purchased-part reservation.
        for i,e in enumerate(edges[:-1]):test('FactorySection'+str(i),e,Q.RESERVE,'FixedJR',jr,pose=[yaw,0])
        cache.save();H.save('fixed-underneck-rounds-progress.json',report)
        print('Whole rounded factory yaw',yaw,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True)
        if report['contacts'] or report['errors']:break
    report.update(status='ROUNDED_FACTORY_JR_MATERIAL_SCREEN_CLEAR_ROOTS_OPEN' if report['poses']==9 and not report['contacts'] and not report['errors'] else 'REJECTED_ROUNDED_FACTORY_MATERIAL',
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**p['source_sha256'],
            **{q.relative_to(H.ROOT).as_posix():S.SHA(q) for q in (Path(__file__),Path(D.__file__),archive)}})
    H.save('fixed-underneck-rounds-material.json',report)
    print(json.dumps({k:report[k] for k in ('status','poses','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
