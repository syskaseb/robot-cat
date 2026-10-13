"""Resolve seed reservation rejection by exact subset, not a new offset."""
import json
import time
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_head_wiring import P


def run():
    tick=time.monotonic();planfile=OUT/'remaining-loom-roots-plan.json'
    nativefile=OUT/'complete-source-carriers-native.json'
    plan,native=[json.loads(p.read_text()) for p in (planfile,nativefile)]
    model=ROOT/native['native'];assert SHA(model)==native['native_sha256']
    reader=P.SavedShapes();rows=[]
    for g in plan['groups']:
        if not g['id'].endswith('HipExtension'):continue
        x,y,z=g['root_world_mm'];seed=Part.makeBox(4,6,4,A.Vector(x-2,y-3,z-2))
        cap=reader.shape(model,g['preserved_owner'])
        bond=reader.shape(model,'Ref_'+g['id'].removesuffix('HipExtension')+'SourceCaseBond')
        outside=seed.cut(cap).Volume;overlap=seed.common(bond).Volume
        assert outside<1e-6 and overlap<1e-6,(g['id'],outside,overlap)
        rows.append(dict(group=g['id'],seed_nominal_bounds_mm=[x-2,y-3,z-2,x+2,y+3,z+2],
                         seed_volume_mm3=seed.Volume,seed_outside_received_cap_mm3=outside,
                         seed_bond_intersection_mm3=overlap,
                         basis='Entire nominal beam seed is existing received cap material, not a new intersecting arm. Conservative expanded mesh seed overlaps intended bond; no geometric offset or collision exclusion for added material.'))
    result=dict(status='FOUR_HIP_ROOT_SEEDS_EXACT_UNCHANGED_SUBSETS',rows=rows,
                selected=False,W5_complete=False,physical_pass=False,
                source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (planfile,nativefile,model,Path(__file__))},
                worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'remaining-carrier-seed-proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],roots=len(rows),worker_seconds=result['worker_seconds'])))


if __name__=='__main__':run()
