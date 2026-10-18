"""Resolve the known cached BUS component error, no whole-scene rerun.

Only a valid selected historical supplier solid may replace a corrupt cached
copy. World bounds/volume must match. No healing, scaling or SKU substitution.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,MODEL
from plan_feline_n01_bus_complete import pose,bb

def main():
    tick=time.monotonic();reader=SavedShapes();name='Ref_Material_BUSsupplier25_0_0'
    received=OUT/'n01-bus-received-motion-envelope.json';r=json.loads(received.read_text())
    dest=OUT/'n01-bus-source-cache-qualification.json';assert not dest.exists()
    assert len(r['errors'])==1 and r['errors'][0]['object']==name
    assert len(r['poses'])==36 and r['pairs']==0
    assert not (r['contacts'] or r['reservation_overlaps'] or r['envelope_outside'])
    for p,h in r['source_sha256'].items():
        if p!='tools/cad/plan_feline_n01_bus_complete.py':assert sha(ROOT/p)==h,p
    T=pose(r['relative_BUS_pose']['rotation_rows'],r['relative_BUS_pose']['translation_mm'])
    source=reader.shape(MODEL,name);cached=reader.shape(OUT/'FelineInteriorMotion.FCStd',name)
    source.translate(A.Vector(0,0,42));raw_valid=source.isValid()
    bounds_gap=max(abs(x-y) for p,q in zip(bb(source),bb(cached)) for x,y in zip(p,q))
    volume_gap=abs(source.Volume-cached.Volume)
    assert bounds_gap<1e-5 and volume_gap<1e-5,'Different physical geometry, cannot reuse scope'
    source.Placement=T*source.Placement
    report={'status':'SOURCE_DIAGNOSIS_ONLY','selected':False,'N01_complete':False,'physical_pass':False,
        'native_changed':False,'source_before_pose_valid':raw_valid,'source_after_pose_valid':source.isValid(),
        'cached_valid':cached.isValid(),'bounds_max_delta_mm':bounds_gap,'volume_delta_mm3':volume_gap,
        'reused_adopted_poses':r['poses'],'reused_motion_pair_count':0,
        'source_sha256':{**reader.hashes,received.relative_to(ROOT).as_posix():sha(received),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))}}
    if source.isValid() and source.Solids:
        outer=reader.shape(OUT/'FelineLayoutEnvelope.FCStd','TorsoEnvelope');outside=source.cut(outer)
        assert outside.isNull() or outside.isValid()
        report['outside_mm3']=outside.Volume
        report['status']='VALID_BASELINE_BUS_SOURCE_CONTAINED_ADOPTED36_SEPARATION_REUSED' if outside.Volume<1e-5 else 'VALID_BASELINE_BUS_SOURCE_OUTSIDE'
    else:
        # A positive containment of a conservative world box is sufficient
        # for packaging ONLY. It does not repair/qualify the supplier BRep.
        lo,hi=bb(source);reserve=Part.makeBox(*(y-x for x,y in zip(lo,hi)),A.Vector(*lo))
        outer=reader.shape(OUT/'FelineLayoutEnvelope.FCStd','TorsoEnvelope');outside=reserve.cut(outer)
        assert outside.isNull() or outside.isValid()
        report.update(conservative_reserve_outside_mm3=outside.Volume,
            status='BUS_SOURCE_INVALID_CONSERVATIVE_PACKAGING_BOUND_CONTAINED_NOT_BREP_APPROVAL' if outside.Volume<1e-5 else 'BUS_SOURCE_INVALID_PACKAGING_BOUND_UNRESOLVED')
    report.update(source_sha256={**report['source_sha256'],**reader.hashes},worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_sha256','reused_adopted_poses')}),flush=True)

if __name__=='__main__':main()
