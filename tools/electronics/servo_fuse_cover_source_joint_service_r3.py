"""Whole mount bridge fits the fixed Deck edge, not a witness-sized notch.

Seven-millimetre bridge is a strict native subset of the R2 eight-mm box.
All actual R2 installed contacts were checked before its final Deck pair;
the entire saved Deck intersection must be removed, not volume-waived.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_source_joint_service_r2.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert raw.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='r2_definition')
exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-cover-source-joint-service-r2','servo-fuse-cover-source-joint-service-r3')
assert 'bridge.Length=8' in code
code=code.replace('bridge.Length=8','bridge.Length=7')
marker='        v=s.Volume; bridgeadded=bridge.Shape.cut(parent.Shape).Volume; assert removed.Volume>0'
assert marker in code
code=code.replace(marker,"""        previous=read('hardware/electronics/full-cat/servo-fuse-cover-source-joint-service-r2/checks.json')
        assert previous['native_union_bridge_mm']==[-91,-100,130,8,12,4]
        assert previous['parent_cover_brep_sha256']==sha(ROOT/previous['parent_cover_brep'])
        for rel,h in previous['source_sha256'].items():
            if rel in pins:assert pins[rel]==h,rel
        originalbridge=Part.makeBox(8,12,4,A.Vector(-91,-100,130))
        assert bridge.Shape.cut(originalbridge).Volume<1e-5
        prior18=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r18/checks.json')
        assert not prior18['errors'] and len(prior18['hits'])==1
        assert (prior18['hits'][0]['phase'],prior18['hits'][0]['part'],prior18['hits'][0]['owner'])==('sampled_lift_0','Cover','CandidateDeck')
        hitpath='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r18/HIT_1.brep'
        pins[hitpath]=sha(ROOT/hitpath);witness=Part.read(str(ROOT/hitpath))
        residual_hit=final.Shape.common(witness).Volume
        assert residual_hit<1e-5,('ENTIRE_OLD_DECK_INTERSECTION_REMAINS',residual_hit)
        v=s.Volume; bridgeadded=bridge.Shape.cut(parent.Shape).Volume; assert removed.Volume>0""")
code=code.replace('native_union_bridge_mm=[-91,-100,130,8,12,4]','native_union_bridge_mm=[-91,-100,130,7,12,4],subtractive_R2_bridge_by_native_construction=True,subset_parent_cover_brep="hardware/cad/studies/servo-fuse-cover-source-joint-service-r2/Cover_WORLD.brep",subset_parent_cover_brep_sha256=sha(ROOT/"hardware/cad/studies/servo-fuse-cover-source-joint-service-r2/Cover_WORLD.brep"),entire_prior_Deck_contact_removed_mm3=residual_hit')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
