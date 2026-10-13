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


def rooted_parts(fork,carrier,x,y,z,validate=True):
    # Actual host-face projection comes BEFORE pads, never a box corner
    # assumed to be material. These are integral replacement extensions.
    fp=carrier.Faces[6].distToShape(Part.Vertex(A.Vector(-184,y-20,80.2)))[1][0][0]
    assert abs(fp.z-80.2)<1e-7
    fixed_pads={
        'Foot':[fp.x-3,fp.y-4,fp.z-3,fp.x+3,fp.y+4,fp.z],
        'Stem':[fp.x-3,fp.y-4,72,fp.x+3,fp.y+4,fp.z],
        'Bridge':[min(x,fp.x)-3,fp.y-4,72,max(x,fp.x)+3,fp.y+4,75],
        # The real face projection can lie away from the requested aim.
        # Connect that transverse bridge to the seat with actual overlap,
        # rather than assuming their Y intervals meet.
        'SeatSpine':[x-3,min(fp.y,y-30)-3,72,x+3,max(fp.y,y-30)+3,75],
        # Entire bed shares the allocated12mm JR width. The former16mm
        # bed entered the adjacent W076 jacket despite a clear JR case.
        'JRSeat':[x-6,y-30,72,x+6,y,75],
    }
    candidates=[]
    aim=Part.Vertex(A.Vector(-176,51,150))
    for f in fork.Faces:
        if f.BoundBox.ZLength<1e-7 and 140<=f.CenterOfMass.z<=151.5 and f.Area>8:
            distance,pairs,_=f.distToShape(aim);candidates.append((distance,pairs[0][0]))
    assert candidates,'No actual Fork horizontal root face for this grip architecture'
    mp=min(candidates,key=lambda q:q[0])[1]
    moving_pads={
        'Foot':[mp.x-3,mp.y-3,mp.z-2,mp.x+3,mp.y+3,mp.z+1],
        'Post':[mp.x-3,mp.y-3,mp.z-2,mp.x+3,mp.y+3,151.5],
        'Arm':[mp.x-3,min(mp.y,51)-3,148,max(mp.x+3,-172),max(mp.y,56)+3,151.5],
        'JacketSeat':[-180,47.2187454246,148,-172,56.2187454246,152.6],
    }
    moving=S.fuse([H.T.box(b) for b in moving_pads.values()])
    fixed=S.fuse([H.T.box(b) for b in fixed_pads.values()])
    # Nominal purchased T18I profile/head reservations, not supplier head
    # measurements. One band per role; openable/cuttable before module lift.
    # Support actual nominal flat1.8mm thickness atZ153.5, not its diagonal
    # circle (which left1.1mm air beneath it). Band head lies on the WEST
    # wall with its5mm axis alongX, rather than above the cable in the skin.
    mb=H.T.box([-180.2,50,151.4,-171.8,52.5,155.6]).cut(H.T.box([-179,49.9,152.6,-173,52.6,154.4]))
    mh=H.T.box([-185.2,48.25,150.5,-180.2,54.25,156.5]);mb=mb.fuse(mh)
    # Bind the JR longitudinally at its WEST edge. A transverse strap would
    # occupy the retained W076 corridor east of the complete JR/bed stack.
    # The west band misses all three provisional straight feed cavities.
    fb=H.T.box([x-6.25,y-31.2,70.8,x-3.75,y+1.2,86.2]).cut(H.T.box([x-6.35,y-30,72,x-3.65,y,85]))
    fh=H.T.box([x-8,y-18,86.2,x-2,y-12,91.2]);fb=fb.fuse(fh)
    before_cut={'Moving':len(moving.Solids),'Fixed':len(fixed.Solids)}
    moving=moving.cut(mb).removeSplitter();fixed=fixed.cut(fb).removeSplitter()
    roots={'MovingFactoryGrip':moving,'MovingFactoryBand':mb,'FixedJRSeat':fixed,'FixedJRBand':fb}
    meta=dict(fixed_host_point_mm=list(fp),moving_host_point_mm=list(mp),fixed_pads=fixed_pads,moving_pads=moving_pads,
        actual_root_common_mm3={'Fixed':fixed.common(carrier).Volume,'Moving':moving.common(fork).Volume},
        provisional_bands=2,band_heads_nominal=True,grip_or_JR_fit_and_strength_phase2=True,
        before_band_cut_solid_count=before_cut,
        components_after_cut={n:[dict(bounds_mm=H.bb(b),volume_mm3=b.Volume) for b in s.Solids] for n,s in roots.items()})
    if validate:
        for n,s in roots.items():assert s.isValid() and len(s.Solids)==1,(n,'Disconnected or invalid complete support')
        assert all(n==1 for n in before_cut.values()),('Disconnected before band cut',before_cut)
        assert min(meta['actual_root_common_mm3'].values())>8,('No actual root',meta)
        for n,host in (('FixedJRSeat',carrier),('MovingFactoryGrip',fork)):
            joined=host.fuse(roots[n]).removeSplitter()
            assert joined.isValid() and len(joined.Solids)==1,(n,'Disconnected native host union')
    return roots,meta


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
    roots,root_meta=rooted_parts(fork,head['YawCarrier'],x,y,z)
    report=dict(status='PENDING',contacts=[],errors=[],pairs=0,poses=0,selected=False,
        native_changed=False,W2_complete=False,W3_complete=False,physical_pass=False,
        actual_root_datums=datums,JR_bounds_mm=H.bb(jr),
        rooted_support_allocation=root_meta,
        source_replacements=[],self_distance_open=True,
        scope='Factory250/JR, both rooted supports and two bands with bare retainedFork. Three complete fixed feeds/self-clearance/native/assembly remain open.',
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
        shapes.update({n:(H.moved(s,yaw) if n.startswith('Moving') else s,0) for n,s in roots.items()})
        for pitch in (-10,0,5):
            current=H.head(reader,yaw,pitch);current['Fork']=H.moved(fork,yaw)
            for n,(s,r) in shapes.items():
                for m,t in current.items():
                    if (n=='MovingFactoryGrip' and m=='Fork') or (n=='FixedJRSeat' and m=='YawCarrier'):continue
                    test(n,s,r,'head/'+m,t,pose=[yaw,pitch])
            report['poses']+=1
        for n,(s,r) in shapes.items():
            for m,t in targets.items():
                if t.Solids:test(n,s,r,m,t,pose=[yaw,0])
            for m,(t,tr) in old.items():
                if m not in retired:test(n,s,r,m,t,tr,pose=[yaw,0])
        # The final straight intentionally enters its own JR end face;
        # earlier portions must clear the entire purchased-part reservation.
        for i,e in enumerate(edges[:-1]):test('FactorySection'+str(i),e,Q.RESERVE,'FixedJR',jr,pose=[yaw,0])
        for i,e in enumerate(edges):
            for n,s in roots.items():
                test('FactorySection'+str(i),e,Q.RESERVE,n,H.moved(s,yaw) if n.startswith('Moving') else s,pose=[yaw,0])
        for n,s in roots.items():
            test(n,H.moved(s,yaw) if n.startswith('Moving') else s,0,'FixedJR',jr,pose=[yaw,0])
        cache.save();H.save('fixed-underneck-rounds-progress.json',report)
        print('Whole rounded factory yaw',yaw,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True)
        if report['contacts'] or report['errors']:break
    report.update(status='ROUNDED_FACTORY_JR_MATERIAL_SCREEN_CLEAR_ROOTS_OPEN' if report['poses']==9 and not report['contacts'] and not report['errors'] else 'REJECTED_ROUNDED_FACTORY_MATERIAL',
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**p['source_sha256'],
            **{q.relative_to(H.ROOT).as_posix():S.SHA(q) for q in (Path(__file__),Path(D.__file__),archive)}})
    H.save('fixed-underneck-rounds-material.json',report)
    print(json.dumps({k:report[k] for k in ('status','poses','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
