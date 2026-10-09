"""Subset-only correction of two band/carrier contacts; reuse pinned peers."""
from pathlib import Path
from datetime import datetime,timezone
import json,time
import FreeCAD as A
import Part,Mesh,MeshPart
from open_prototype_tail_complete import build,ROOT,BASE,OUT,MODEL
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import rect
from open_prototype_shared_distribution_carriers import validate
from check_main_p0_placement import sha


def run():
    assert not MODEL.exists()
    tick=time.monotonic();proof=OUT/'native-mount-checks.json'
    old=json.loads(proof.read_text())
    assert old['status']=='REJECTED_CHANGED_INTERFACES' and not old['errors']
    assert {c['a'] for c in old['contacts']}=={'MonitorTie1StrapAllowance','MonitorTie2StrapAllowance'}
    assert len(old['contacts'])==2 and all(c['b']=='LowerCarrierMatched' for c in old['contacts'])
    assert all(sha(ROOT/n)==h for n,h in old['source_sha256'].items())
    parent=OUT/'pre-band-channel-checks.json';parent.write_text(json.dumps(old,indent=2)+'\n',encoding='utf-8')
    sources=[BASE/'mounting-checkpoint/RetentionMountsAssembly.FCStd',BASE/'wiring-checkpoint/TailLocalCurrent.FCStd',
          ROOT/'hardware/cad/studies/tail-p0-bridge-flange-r1/TailBridgeP0Flange.FCStd']
    docs=[A.openDocument(str(p)) for p in sources]
    doc,carrier,post,bridge,support=build(*docs)
    before=carrier.Shape.copy()
    sk=sketch(carrier,'MonitorFullBandChannelsPlan',43)
    for x in (126,133):rect(sk,x-.35,-18,3.2,35.2)
    carrier.Tip=feature(carrier,'Pocket','MonitorFullBandChannels',sk,1.68)
    doc.recompute();base=validate(doc,[carrier,post])
    added=carrier.Shape.cut(before)
    assert added.isNull() or added.Volume<1e-6,'Correction must not add material near previously checked peers'
    removed=before.cut(carrier.Shape).Volume;assert removed>0
    contacts=[]
    for i,x in enumerate((126,133)):
        outer=Part.makeBox(2.5,33.6,14.52,A.Vector(x,-16.8,41.6))
        inner=Part.makeBox(3,31.2,12.12,A.Vector(x-.25,-15.6,42.8))
        strap=outer.cut(inner)
        overlap=strap.common(carrier.Shape).Volume
        if overlap>1e-6:contacts.append(dict(a=f'MonitorTie{i+1}StrapAllowance',b='LowerCarrierMatched',volume_mm3=overlap))
        ob=doc.addObject('Part::Feature',f'MonitorTie{i+1}StrapAllowance');ob.Shape=strap
        ob=doc.addObject('Part::Feature',f'MonitorTie{i+1}HeadAllowance')
        ob.Shape=Part.makeBox(4.8,4.5,3.5,A.Vector(x-1.15,-16.8,54.92))
    assert not contacts,contacts
    monitor=doc.addObject('Part::Feature','MonitorCaseReservation')
    monitor.Shape=Part.makeBox(41,25,12,A.Vector(108,-12.5,42.92))
    # Restore the four already-qualified shared frame hardware sets for the
    # current assembly without re-running their unchanged access matrix.
    import math
    from open_prototype_tail_complete import AXES
    for i,(x,y) in enumerate(AXES):
        screw=Part.makeCylinder(1,30,A.Vector(x,y,35.22)).fuse(Part.makeCylinder(1.9,2,A.Vector(x,y,33.22)))
        ring=lambda z:Part.makeCylinder(2.5,.3,A.Vector(x,y,z)).cut(Part.makeCylinder(1.1,.3,A.Vector(x,y,z)))
        poly=Part.makePolygon([A.Vector(x+2/math.cos(math.pi/6)*math.cos(a*math.pi/3),y+2/math.cos(math.pi/6)*math.sin(a*math.pi/3),60.82) for a in range(7)])
        nut=Part.Face(Part.Wire(poly.Edges)).extrude(A.Vector(0,0,1.6)).cut(Part.makeCylinder(1.1,1.6,A.Vector(x,y,60.82)))
        for suffix,s in [('Bolt',screw),('LowerWasher',ring(35.22)),('UpperWasher',ring(60.52)),('Nut',nut)]:
            doc.addObject('Part::Feature',f'RearShared{i+1}{suffix}').Shape=s
    z=doc.RaisedTailBridge.Shape.BoundBox.ZMin
    doc.TailParameters.TailRise=16;validate(doc,[post])
    assert abs(doc.RaisedTailBridge.Shape.BoundBox.ZMin-z-1)<1e-6 and abs(post.Shape.BoundBox.ZLength-20)<1e-6
    doc.TailParameters.TailRise=15;validate(doc,[post])
    assert abs(doc.RaisedTailBridge.Shape.BoundBox.ZMin-z)<1e-6
    assert abs(carrier.Shape.Volume-base[carrier.Name])<1e-6
    doc.recompute();doc.saveAs(str(MODEL))
    exports={}
    for b,q in ((carrier,1),(post,4)):
        mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
        assert mesh.isSolid() and not mesh.hasNonManifolds()
        dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength];assert max(dims)+10<256
        mesh.translate(-mesh.BoundBox.XMin,-mesh.BoundBox.YMin,-mesh.BoundBox.ZMin)
        f=OUT/(b.Name+f'_x{q}.stl');mesh.write(str(f));reload=Mesh.Mesh(str(f));assert reload.isSolid() and not reload.hasNonManifolds()
        exports[f.name]=dict(sha256=sha(f),quantity=q,dimensions_mm=dims,closed=True)
    A.closeDocument(doc.Name)
    reopen=A.openDocument(str(MODEL));validate(reopen,[reopen.LowerCarrier,reopen.TailRiser]);A.closeDocument(reopen.Name)
    for d in docs:A.closeDocument(d.Name)
    result=dict(old)
    result.update(status='NATIVE_PLATE_ROOTED_TAIL_MOUNT_PREPARED',contacts=[],errors=[],native_sha256=sha(MODEL),
        subset_correction=dict(parent='pre-band-channel-checks.json',added_material_mm3=0,removed_material_mm3=removed,
            rationale='Only two straps touched receiving material. Removing material cannot create a new overlap with unchanged peers; complete parent scene and fastener checks pinned, not renamed as passed.',
            retained_parent_pairs=old['tested_pairs'],new_band_carrier_pairs=2,minimum_channel_floor_mm=1.6),
        parameter_restore=dict(TailRise_mm=[15,16,15],post_height_mm=[19,20,19],bridge_and_support_coupled=True),
        native_volumes_mm3=base,exports=exports,reopen_verified=True,mechanical_M3_complete=False,
        worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
    result['source_sha256']=dict(old['source_sha256'])
    for f in [parent,Path(__file__)]:result['source_sha256'][f.relative_to(ROOT).as_posix()]=sha(f)
    proof.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],removed_mm3=removed,exports=exports,worker_seconds=result['worker_seconds'])))


if __name__=='__main__':run()
