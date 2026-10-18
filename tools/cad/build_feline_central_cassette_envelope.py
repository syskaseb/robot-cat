"""Materialize the already planned flat belly, preserve historical source.

Planning volume only, no shell wall/skin/print selection. Same325x200x160
budget and196maximumwidth; no widening sides to fit electronics.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import SavedShapes,ROOT,sha
from plan_feline_layout import OUT
import build_feline_layout_envelope as builder


def main():
    tick=time.monotonic();reader=SavedShapes()
    old=OUT/'FelineLayoutEnvelope.FCStd';before=sha(old)
    target=OUT/'central-cassette-envelope';target.mkdir(exist_ok=True)
    assert not (target/'FelineLayoutEnvelope.FCStd').exists(),'Receive unchanged saved candidate first'
    feet=OUT/'FelineBellyFeet.FCStd';tip=reader.shape(feet,'BellyFoot1').BoundBox.ZMin
    builder.OUT=target
    report=builder.build(32,tip)
    native=ROOT/report['native'];doc=A.openDocument(str(native))
    try:
        assert doc.getObject('TorsoEnvelope').Shape.isValid()
        assert all(doc.getObject('CrossSection'+str(i)).FullyConstrained for i in range(8))
        b=doc.getObject('TorsoEnvelope').Shape.BoundBox
        assert b.XLength<=325.00001 and b.YLength<=200 and b.ZLength<=160.00001
        report['fresh_reopen']=True
        report['actual_bounds_mm']=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
    finally:A.closeDocument(doc.Name)
    assert sha(old)==before
    report.update(status='NATIVE_FLAT_BELLY_PLANNING_VOLUME_NOT_SKIN_OR_SELECTED',selected=False,physical_pass=False,
        old_source_preserved_sha256=before,worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (old,feet,Path(builder.__file__),Path(__file__))},
        reason='Old saved envelope is158high/p4belly and differs from current160high/flatR12 design recipe. Use one explicit candidate, do not silently treat unsaved recipe as native geometry.',
        full_skin_mounts_motion_and_appearance_open=True)
    (target/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
