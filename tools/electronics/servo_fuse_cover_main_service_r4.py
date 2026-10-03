"""Reconnect the actual detached front skirt with one native outer rib.

Keep both R3 solids, add a4x3.5mm vertical rib on the skirt outer corner,
and fuse them. No discarded fragment; no new printed part. New material is
explicitly not covered by old cut-only collision receipts: shared lift must
include the nominal installed pose and all actual fixed owners.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_main_service_r3.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r3_definition_only')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-cover-main-service-r3','servo-fuse-cover-main-service-r4')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
marker="        print('COVER_MAIN_SEGMENTED_RECOMPUTE',len(tools),len(covered),flush=True);d.recompute();s=final.Shape.copy();strict=s.check(True) or []"
replace(marker,"""        print('COVER_MAIN_BRACED_RECOMPUTE',len(tools),len(covered),flush=True);d.recompute()
        cut=final;rib=d.addObject('Part::Box','FrontSkirtOuterServiceRib')
        rib.Placement.Base=A.Vector(-94,-100,128);rib.Length=4;rib.Width=3.5;rib.Height=57
        d.recompute();components=cut.Shape.Solids
        overlaps=[q.common(rib.Shape).Volume for q in components]
        print('COVER_RIB_COMPONENT_CONNECTIONS',overlaps,flush=True)
        assert len(components)==2 and all(v>1e-5 for v in overlaps),'Rib must connect BOTH actual solids'
        final=d.addObject('Part::MultiFuse','CoverMainServiceBracedFinished');final.Shapes=[cut,rib];final.Refine=False
        d.recompute();s=final.Shape.copy();strict=s.check(True) or []""")
replace("added=s.cut(parent.Shape).Volume;assert added<1e-5", "added=s.cut(parent.Shape).Volume;assert 0<added<798.001")
replace("existing_upper_window_preserved=True,added_parts=0,", "existing_upper_window_preserved=True,added_parts=0,added_native_rib_mm=[-94,-100,128,-90,-96.5,185],new_material_requires_shared_installed_collision_check=True,")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
