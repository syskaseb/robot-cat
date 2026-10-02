"""Free input TE5.5mm inward; lift the bare bank, not ends across its ribs.

R2 outward parking hit14 ribs. Preserve that result; check this changed
sequence, inheriting the unchanged24 vertical-tool checks explicitly.
"""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_bank_service_r2.py')
code=base.read_text(encoding='utf-8').replace('servo-fuse-bank-service-r2','servo-fuse-bank-service-r3')
begin=code.index("    print('VERTICAL_CLIP_TOOLS',flush=True)")
end=code.index('    terminal_dir=',begin)
code=code[:begin]+'''    p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-service-r2/checks.json'
    inherited=json.loads(p.read_text(encoding='utf-8'));hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    assert not inherited['errors'] and not any(r['phase']=='vertical_clip_tool' for r in inherited['hits'])
    hashes['tools/electronics/servo_fuse_bank_service_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_service_r2.py')
'''+code[end:]
code=code.replace("for role,shift in [('IN',38),('OUT',36)]:","for role,shift in [('IN',-5.5),('OUT',0)]:")
code=code.replace('    assert len(parked)==24', '''    assert len(parked)==24
    # Continuous relative rigid-end sweep for a100mm upwards module lift.
    # Do not repeat unchanged body lift samples or claim a flexible-wire test.
    print('BANK_OVER_RELEASED_ENDS',flush=True)
    for n,q in parked.items():
        b=q.BoundBox
        swept=box([b.XMin,b.YMin,b.ZMin-100,b.XMax,b.YMax,b.ZMax])
        swept.exportBrep(str(OUT/(n+'_RELATIVE_MODULE_LIFT_SWEEP.brep')))
        for m,t in owners.items():
            if m.endswith('ClipAccessFinished_WORLD') or m.endswith('/CoverYawEndSeat.brep'):
                check('continuous_module_over_ends',n,swept,m,t)
''')
code=code.replace("VERTICAL_TOOLS_AND_RIGID_END_PARKING_CLEAR_WAGO_OPEN","INPUT_INWARD_RELEASE_MODULE_OVER_ENDS_CLEAR_WAGO_OPEN")
code=code.replace("'Remove the released AWG12 input pigtails outward38mm, then move output TE ends outward36mm.'", "'Move the freed input TE ends inward5.5mm; leave output TE axes unchanged.'")
code=code.replace('Raise each holder10mm; cut all24 bank strain ties. Remove the released AWG12 input pigtails outward38mm, then move output TE ends outward36mm.',
    'Raise each holder10mm; cut all24 bank strain ties. Move freed input TE inward5.5mm, clear of the input backers. Output ends remain in place.')
code=code.replace('Secure loose ends outside the bank before lifting the disconnected bank+cover.',
    'Input TE bodies clear the backers after5.5mm inward release. Hold released ends stationary while lifting the bare bank+cover; do not drag a terminal through an insulation seat.')
code=code.replace('Full moving leg spans must retain sufficient free length for this parked-end position; no actual flexible lead deformation proved here.',
    'Full leg wire deformation/length remains W5; rigid output ends stay on their original axes. Input pigtails are detached at WAGO, not stretched while connected.')
code=code.replace('module_sampled_clearance_inherited=True,',
    'module_sampled_clearance_inherited=True,vertical_tool_access_inherited_from_service_r2=True,continuous_module_over_ends_mm=100,')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
