"""Coupled rear outputs beneath the AUX/ground bridge, with west-facing cages.

Factory and extension final tangents agree with the connector FACE, unlike
rejected R2. HELU descends first, turns beyond the ground/AUX case then rises
west of the fuse body. Any Deck/native grip collision remains OPEN and must
be resolved in matching native construction; no implicit contact waiver.
Retain verified FR R3 and all four MTA/source stations.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_output_returns_complete_r1.py')
code=parent.read_text(encoding='utf-8')
code=code.replace("servo-fuse-output-returns-complete-r1'","servo-fuse-output-returns-complete-r4'")
code=code.replace('    native=ROOT/', "    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r1.py')\n    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r2.py')\n    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r3.py')\n    native=ROOT/",1)
a=code.index('    for leg,ident,left,cy,cz,rise_sine,extra,target_y in [')
b=code.index('    for n,s in changed.items():s.exportBrep',a)
code=code[:a]+'''    fr_folder=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r3'
    pin(fr_folder/'checks.json');fr=json.loads((fr_folder/'checks.json').read_text(encoding='utf-8'))
    assert not fr['hits'] and not fr['errors'] and not fr['factory_failures']
    for role in ('221412','factory','extension'):
        owners['AcceptedFR/W037_'+role]=load(fr_folder/('W037_'+role+'_DESIGN.brep'))
    for leg,ident,left,cy,cz,drop,tx,factory_z,extension_z in [
        ('RL','W045',16.5,72,130,9,-43.5,130,123.5),
        ('RR','W053',28.5,-86,121.5,8,-41,128,121.5)]:
        side=1 if leg=='RL' else -1;Y=V(0,side,0)
        e=Route([25.5,side*49.5,113.5]);e.line([25.5,side*53.5,113.5])
        e.shift(Y,-Z*drop,25.2)
        e.arc(Y,-X,25.2)
        target_y=e.p.y
        e.shift(-X,Z*(extension_z-e.p.z),25.2)
        straight=e.p.x-tx
        assert straight>=4,dict(leg=leg,straight=straight)
        e.line([tx,target_y,extension_z])
        f=Route([left,cy,cz])
        f.shift(-X,V(0,target_y-cy,factory_z-cz),20)
        assert f.p.x>=tx
        f.line([tx,target_y,factory_z])
        for r in (f,e):
            assert (r.edges[-1].tangentAt(r.edges[-1].LastParameter)+X).Length<1e-7
            assert abs(r.p.x-tx)<1e-7 and abs(r.p.y-target_y)<1e-7
        assert abs((f.p-e.p).Length-6.5)<1e-7
        lowy=target_y-4;lowz=extension_z-3.25
        # Local CAD dimensions depth18.3, height8.15, cage span13 are
        # rotated: depth points WEST, not the mistaken Y-facing R2 box.
        changed[ident+'_221412']=Part.makeBox(18.3,8.15,13,V(tx-18.3,lowy,lowz))
        wire(ident+'_factory',f,5,'MTA_factory',11,leg)
        wire(ident+'_extension',e,4.2,'HELU23802',25,leg)
        joints.append(dict(id=ident,leg=leg,kind='WAGO221-412',SKU='221-412',
            ports_mm=[list(f.p),list(e.p)],approach_normals=[[-1,0,0],[-1,0,0]],
            shared_face_axis='X',same_face_and_tangents_asserted=True,
            body_bounds_mm=[tx-18.3,lowy,lowz,tx,lowy+8.15,lowz+13],
            strip_mm=11,grip_straight_extension_mm=straight,
            dimensions_source=facts.relative_to(ROOT).as_posix(),native_grips='OPEN: matching below-Deck clearance, housing seats and independent insulation restraints.',
            recipe='Both UNTINNED ends on east face, approach west. Prewire unpowered removed Deck, supplier11mm strip. No side-face insertion. Retain four MTA/source assemblies.',
            assumptions='Supplier nominal envelope, project cage datums, OD/radii and100mm factory usable lead, not delivered fit/lever sweep.'))
''' +code[b:]
code=code.replace("unchanged='Four MTA bodies/front sources/rear sources/nativeRL_R5/nativeRR_R4/FRGuard; unchanged FL output retained by hashes.'", "unchanged='Four MTA bodies/all accepted sources/nativeRL_R5/nativeRR_R4/FRGuard/FR R3/FL output retained; rear native matched casing/grips remain OPEN.'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
