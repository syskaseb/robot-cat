"""One self-contained head/neck copy, replacing two targets, not history.

The mechanical motion frames remain editable. Cable shapes are labelled
nominal-pose references; the separate constant-length family is pinned, not
misrepresented as a continuous CAD animation or a physical sweep test.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part
import plan_fixed_head_feed_interface as I
from open_prototype_head_assembly import FIXED,PITCH,reference_signature
from build_u1_grouped_grips import validate
H,S,C,Q=I.H,I.S,I.C,I.Q
MODEL=H.OUT/'HeadNeckFixedInterface.FCStd'

def run():
    tick=time.monotonic();nf=H.OUT/'fixed-head-interface-native.json';native=H.read(nf)
    assert native['status']=='FIXED_HEAD_INTERFACE_NATIVE_CANDIDATE_ASSEMBLY_STOCK_OPEN'
    for n,h in native['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,n
    source=H.ROOT/native['model'];assert S.SHA(source)==native['model_sha256']
    assert not (H.OUT/'fixed-head-native-master.json').exists(),'Receive completed result; no duplicate'
    p,feeds,roots,meta,fork,reader,allocation,archive=I.prepare()
    expected=H.head(reader)
    # Native history and a fused reference can have a different vertex order.
    # Their MATERIAL equality was already established by native Boolean gate.
    # A copy/placement test must compare to the exact qualified native source,
    # not zip vertices from a different Boolean construction of that material.
    expected.update(Fork=reader.shape(source,'MovingFork'),YawCarrier=reader.shape(source,'FixedYawCarrier'))
    if MODEL.exists():
        d=A.openDocument(str(MODEL))
        assert d.getObject('HeadInterfaceParameters') is None,'Interrupted edited copy requires explicit recovery'
        assert d.HeadParameters.Yaw==0 and d.HeadParameters.Pitch==0
    else:d=A.openDocument(str(H.HEAD));d.saveAs(str(MODEL))
    src=A.openDocument(str(source))
    # One dependency transaction: separately copying the VarSet and then a
    # recursive Body creates a second VarSet; editing the first is inert.
    copied=d.copyObject([src.HeadInterfaceParameters,src.FixedYawCarrier,src.MovingFork],True)
    parameter,fixedbody,movingbody=copied;targets={}
    for identity,body in [('Fork',movingbody),('YawCarrier',fixedbody)]:
        d.recompute();validate(body);body.Visibility=False
        link=d.getObject('Head_'+identity);assert link.TypeId=='App::Link'
        local=expected[identity].copy();local.translate(-H.SHIFT)
        link.setLink(body);link.LinkTransform=True
        link.LinkPlacement=local.Placement*body.Shape.Placement.inverse()
        link.Visibility=True;targets[identity]=body.Name;d.recompute()
    # Nominal wire/connector and restraint references are new physical roles,
    # not a second old outboard anchor or a second old pitch transition.
    refs={n:s for n,s in roots.items() if n not in ('FixedJRSeat','MovingFactoryGrip')}
    x,z=p['fixed_receiver_XZ_mm'];y=p['fixed_receiver_Y_mm']
    refs['FixedJR']=H.T.box([x-6,y-30,z-5,x+6,y,z+5])
    refs.update({n:Part.Wire(es) for n,es in feeds.items()})
    rest=next(row for row in p['poses'] if row['yaw']==0)
    refs['FactoryFreeUncut250']=H.T.wire(rest['parts'])
    qualified,_=C.F.allocation(60)
    refs.update({n:s for n,(s,r) in qualified.items() if n.startswith('Qualified')})
    for n,s in refs.items():
        ob=d.addObject('Part::Feature','Interface_'+n);s=s.copy();s.translate(-H.SHIFT);ob.Shape=s
        ob.addProperty('App::PropertyString','Scope')
        ob.Scope='Nominal pose reference; exact sampled family/assumptions in pinned interface receipt. Not a physical test.'
        (d.YawMotion if n.startswith(('Moving','Qualified')) else d.CP2Head).addObject(ob)
    rows=H.read(H.BASE/'head-mount-checkpoint/native-assembly-checks.json')['parts']
    def world(name):
        s=d.getObject('Head_'+name).Shape.copy();tr=d.CP2Head.Placement
        if name not in FIXED:tr=tr*d.YawMotion.Placement
        if name in PITCH:tr=tr*d.PitchMotion.Placement
        s.Placement=tr*s.Placement;return s
    # Reject a broken dependency BEFORE the nine retained motion cases.
    vol=world('YawCarrier').Volume;parameter.NorthRailThickness=3.2;d.recompute()
    assert world('YawCarrier').Volume>vol,('Copied parameter is inert',parameter.Name)
    parameter.NorthRailThickness=3;d.recompute();assert abs(world('YawCarrier').Volume-vol)<1e-5
    print('Shared native dependency/parameter received',round(time.monotonic()-tick,3),flush=True)
    for row in rows:reference_signature(world(row['name']),expected[row['name']],row['name'])
    checks=[]
    for yaw in (-15,0,15):
        for pitch in (-10,0,5):
            d.HeadParameters.Yaw=yaw;d.HeadParameters.Pitch=pitch
            d.recompute([d.YawMotion,d.PitchMotion])
            # The other50targets and the original motion expressions are
            # unchanged; receive their rest-copy identity once, not450times.
            for n in targets:
                wanted=H.moved(expected[n],yaw if n not in FIXED else 0,pitch if n in PITCH else 0)
                reference_signature(world(n),wanted,n)
            checks.append([yaw,pitch])
            print('Changed motion',yaw,pitch,round(time.monotonic()-tick,3),flush=True)
    d.HeadParameters.Yaw=0;d.HeadParameters.Pitch=0;d.recompute([d.YawMotion,d.PitchMotion])
    print('All52identities/9motion frames received',round(time.monotonic()-tick,3),flush=True)
    # Retained MAIN gap expression must stay46.52 world-Z at4, not double-shift.
    # The retained master has two historical VarSets exposing MainGap.
    # Resolve the actual dependency, not a global property-name count.
    expressions=dict(d.CurrentMainSupplierReference.ExpressionEngine)
    expression=expressions.get('.Placement.Base.z',expressions.get('Placement.Base.z',''))
    import re
    dependency=re.search(r'\b(\w+)\.MainGap\b',expression)
    assert dependency,('MAIN parameter dependency absent',expression)
    gaps=[d.getObject(dependency.group(1))]
    assert gaps[0] and 'MainGap' in gaps[0].PropertiesList
    for value,wanted in [(4,46.52),(5,47.52),(4,46.52)]:
        gaps[0].MainGap=value;d.recompute()
        assert abs(d.CurrentMainSupplierReference.Placement.Base.z-wanted)<1e-6
    for row in rows:reference_signature(world(row['name']),expected[row['name']],row['name'])
    d.save();A.closeDocument(src.Name);A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-head-master-') as td:
        cp=Path(td)/MODEL.name;shutil.copy2(MODEL,cp);d=A.openDocument(str(cp));d.recompute()
        assert all(o.getLinkedObject(True).Document==d for o in d.Objects if o.TypeId=='App::Link')
        for row in rows:reference_signature(world(row['name']),expected[row['name']],row['name'])
        for name in targets.values():validate(d.getObject(name))
        A.closeDocument(d.Name)
    report=dict(status='FIXED_HEAD_NATIVE_MASTER_COPY_PREPARED_SELECTION_SERVICE_STOCK_OPEN',
        selected=False,physical_pass=False,model=MODEL.relative_to(H.ROOT).as_posix(),model_sha256=S.SHA(MODEL),
        identities=52,replaced_targets=targets,pose_samples=checks,relocated_reopen=True,external_links=0,
        MAIN_worldZ_4_5_4=[46.52,47.52,46.52],native_parameter_restore_mm=[3,3.2,3],
        retired_outboard_fork_not_instanced=True,old_fork_Ymax_mm=134,new_fork_bounds_mm=H.bb(expected['Fork']),
        factory_free_curve_is_nominal_reference_not_animation=True,
        source_sha256={**native['source_sha256'],nf.relative_to(H.ROOT).as_posix():S.SHA(nf),
            source.relative_to(H.ROOT).as_posix():S.SHA(source),Path(__file__).relative_to(H.ROOT).as_posix():S.SHA(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    H.save('fixed-head-native-master.json',report)
    print(json.dumps({k:report[k] for k in ('status','identities','new_fork_bounds_mm','worker_seconds')}),flush=True)

if __name__=='__main__':run()
