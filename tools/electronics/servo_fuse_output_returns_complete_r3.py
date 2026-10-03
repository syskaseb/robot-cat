"""FR complete paired approach with common cage normals and low HELU route.

R2 is rejected: every extension enters a SIDE of the Y-facing connector.
Keep its failed evidence, never waive that geometric/interface failure.
FR now routes the HELU below W066 and the factory above it, with both final
tangents facing south. RL/RR rejected R1 outputs remain obstacles and OPEN;
this is explicitly a local FR construction, not a full output-bank pass.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_output_returns_complete_r1.py')
code=parent.read_text(encoding='utf-8')
code=code.replace("servo-fuse-output-returns-complete-r1'","servo-fuse-output-returns-complete-r3'")
code=code.replace('    native=ROOT/', "    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r1.py')\n    pin(ROOT/'tools/electronics/servo_fuse_output_returns_complete_r2.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r2/checks.json')\n    native=ROOT/",1)
a=code.index('    for leg,ident,left,cy,cz,rise_sine,extra,target_y in [')
b=code.index('    for n,s in changed.items():s.exportBrep',a)
code=code[:a]+'''    prior_outputs=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r1'
    pin(prior_outputs/'checks.json')
    for ident in ('W045','W053'):
        for role in ('221412','factory','extension'):
            owners['UnselectedRear/'+ident+'_'+role]=load(prior_outputs/(ident+'_'+role+'_DESIGN.brep'))
    leg='FR';ident='W037';Y=V(0,-1,0)
    f=Route([-79.5,-72,126]);sine=.3;co=math.sqrt(1-sine*sine)
    normal=Y*co-Z*sine
    f.arc(-X,normal,20)
    f.arc(normal,Y*sine+Z*co,20,math.asin(sine))
    tx=f.p.x;factory_z=f.p.z;target_y=-109
    f.line([tx,target_y,factory_z]);extension_z=factory_z-6.5
    e=Route([-82.5,-49.5,113.5]);e.line([-82.5,-55.5,113.5])
    e.shift(Y,V(tx+82.5,0,extension_z-113.5),25.2)
    straight=(V(tx,target_y,extension_z)-e.p).dot(Y)
    assert straight>=4,straight
    e.line([tx,target_y,extension_z])
    for r in (f,e):
        assert (r.edges[-1].tangentAt(r.edges[-1].LastParameter)-Y).Length<1e-7
        assert abs(r.p.y-target_y)<1e-7
    assert abs((f.p-e.p).Length-6.5)<1e-7
    lowy=target_y-18.3;lowz=extension_z-3.25
    changed[ident+'_221412']=Part.makeBox(8.15,18.3,13,V(tx-4,lowy,lowz))
    wire(ident+'_factory',f,5,'MTA_factory',11,leg)
    wire(ident+'_extension',e,4.2,'HELU23802',25,leg)
    joints.append(dict(id=ident,leg=leg,kind='WAGO221-412',SKU='221-412',
        ports_mm=[list(f.p),list(e.p)],approach_normals=[[0,-1,0],[0,-1,0]],
        shared_face_axis='Y',same_face_and_tangents_asserted=True,
        body_bounds_mm=[tx-4,lowy,lowz,tx+4.15,lowy+18.3,lowz+13],
        strip_mm=11,grip_straight_extension_mm=straight,
        dimensions_source=facts.relative_to(ROOT).as_posix(),native_grips='OPEN',
        recipe='Separate UNTINNED cages, nominal11mm strip. Upper factory/lower extension, both approach the same south-facing normal. Casing/retention only after actual shared check.',
        assumptions='Supplier nominal housing, project cage datums and factory100mm; not delivered fit or lever sweep.'))
''' +code[b:]
code=code.replace("unchanged='Four MTA bodies/front sources/rear sources/nativeRL_R5/nativeRR_R4/FRGuard; unchanged FL output retained by hashes.'", "unchanged='Four MTA bodies/all accepted sources/nativeRL_R5/nativeRR_R4/FRGuard/FL output retained. RL/RR outputs retained as unselected failed R1 obstacles; not qualified.'")
code=code.replace("status='OUTPUT_RETURN_CONTACTS' if hits or errors or factory_failures else 'OUTPUT_RETURNS_STATIC_CLEAR_NATIVE_GRIPS_OPEN'", "status='FR_OUTPUT_RETURN_CONTACTS' if hits or errors or factory_failures else 'FR_OUTPUT_STATIC_CLEAR_NATIVE_GRIPS_REAR_OUTPUTS_OPEN'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
