"""One dogleg rib from the actual front lip to its nearest upper wall.

R4 straight outer column connects neither actual component, so it is not
used. Recorded R3 nearest gap is Y9mm/Z4.575mm; bridge it above the lower
output wire, not with a fictitious roof at the lip's XY coordinates.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_main_service_r4.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r4_definition_only')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-cover-main-service-r4','servo-fuse-cover-main-service-r5')
old="""        cut=final;rib=d.addObject('Part::Box','FrontSkirtOuterServiceRib')
        rib.Placement.Base=A.Vector(-94,-100,128);rib.Length=4;rib.Width=3.5;rib.Height=57
        d.recompute();components=cut.Shape.Solids
        overlaps=[q.common(rib.Shape).Volume for q in components]"""
new="""        cut=final;leg=d.addObject('Part::Box','FrontSkirtServiceRibLeg')
        leg.Placement.Base=A.Vector(-79,-100,128);leg.Length=4;leg.Width=3.5;leg.Height=11
        beam=d.addObject('Part::Box','FrontSkirtServiceRibBeam')
        beam.Placement.Base=A.Vector(-79,-100,135);beam.Length=4;beam.Width=15.5;beam.Height=4
        rib=d.addObject('Part::MultiFuse','FrontSkirtDoglegServiceRib');rib.Shapes=[leg,beam]
        d.recompute();components=cut.Shape.Solids
        overlaps=[q.common(rib.Shape).Volume for q in components]"""
assert old in code;code=code.replace(old,new)
code=code.replace('added_native_rib_mm=[-94,-100,128,-90,-96.5,185]', 'added_native_rib_mm=[[-79,-100,128,-75,-96.5,139],[-79,-100,135,-75,-84.5,139]]')
code=code.replace('assert 0<added<798.001','assert 0<added<346.001')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
