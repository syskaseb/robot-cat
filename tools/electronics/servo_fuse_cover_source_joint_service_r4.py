"""One native service arch over the complete stationary FR source route.

Short R3 bridge crosses W042 during lift and is rejected. Column stays
before its full Y envelope; horizontal connection is above its full Z
envelope. Keep the original mount, parent Cover, three whole joint cuts.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_source_joint_service_r2.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='arch_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-cover-source-joint-service-r2','servo-fuse-cover-source-joint-service-r4')
old="""    bridge=d.addObject('Part::Box','FrontLeftMountServiceBridge')
    bridge.Length=8;bridge.Width=12;bridge.Height=4;bridge.Placement.Base=A.Vector(-91,-100,130)"""
new="""    column=d.addObject('Part::Box','FrontLeftServiceArchColumn')
    column.Length=7;column.Width=3;column.Height=55;column.Placement.Base=A.Vector(-92,-100,123)
    beam=d.addObject('Part::Box','FrontLeftServiceArchBeam')
    beam.Length=7;beam.Width=60;beam.Height=4;beam.Placement.Base=A.Vector(-92,-100,174)
    bridge=d.addObject('Part::Fuse','FrontLeftMountServiceArch')
    bridge.Base=column;bridge.Tool=beam;bridge.Refine=False"""
assert old in code;code=code.replace(old,new)
marker='        v=s.Volume; bridgeadded=bridge.Shape.cut(parent.Shape).Volume; assert removed.Volume>0'
assert marker in code
code=code.replace(marker,"""        previous=read('hardware/electronics/full-cat/servo-fuse-cover-source-joint-service-r2/checks.json')
        assert previous['parent_cover_brep_sha256']==sha(ROOT/previous['parent_cover_brep'])
        for rel,h in previous['source_sha256'].items():
            if rel in pins:assert pins[rel]==h,rel
        assert previous['source_joint_envelopes']==envelopes
        fail=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r19/checks.json')
        assert not fail['errors'] and fail['hits'][0]['owner']=='RetainedFeed/W042_extension_DESIGN'
        oldhit='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r18/HIT_1.brep'
        pins[oldhit]=sha(ROOT/oldhit);witness=Part.read(str(ROOT/oldhit))
        residual_hit=final.Shape.common(witness).Volume
        assert residual_hit<1e-5
        fullwire='hardware/electronics/full-cat/servo-fuse-front-source-ports-r2/W042_extension_DESIGN.brep'
        pins[fullwire]=sha(ROOT/fullwire);wb=Part.read(str(ROOT/fullwire)).BoundBox
        assert column.Shape.BoundBox.YMax<wb.YMin-.35 and beam.Shape.BoundBox.ZMin>wb.ZMax+.35
        v=s.Volume; bridgeadded=bridge.Shape.cut(parent.Shape).Volume; assert removed.Volume>0""")
code=code.replace('native_union_bridge_mm=[-91,-100,130,8,12,4]',
    'native_service_arch_boxes_mm=[[-92,-100,123,7,3,55],[-92,-100,174,7,60,4]],installed_core_unchanged_R18=True,installed_core_R18_parent_cover="hardware/cad/studies/servo-fuse-cover-source-joint-service-r2/Cover_WORLD.brep",installed_core_R18_parent_cover_sha256=sha(ROOT/"hardware/cad/studies/servo-fuse-cover-source-joint-service-r2/Cover_WORLD.brep"),entire_prior_Deck_contact_removed_mm3=residual_hit')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
