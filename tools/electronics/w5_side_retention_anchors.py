"""Bind the four side towers to actual Carrier material before native CAD.

R1's low three-mm roots have zero common volume and must NOT be built. Read
the unchanged Carrier once, find actual contact of each complete stem, and
only where needed propose a foot to its nearest material. Foreign clearance
of the proposed feet belongs to the one whole-side construction preflight.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import w5_side_retention_plan as P
from servo_fuse_inputs_r1 import save, sha

OUT=P.N.BASE/'w5-side-retention-plan-r2'


def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'plan.json').exists()
    path=P.OUT/'plan.json';plan=json.loads(path.read_text(encoding='utf-8'))
    assert plan['all_straights_match'] and plan['received_straights_matched']==35
    for rel,digest in plan['source_sha256'].items():
        assert sha(P.ROOT/rel)==digest,rel
    carrier_path=P.ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1/SourceCarrier_CANDIDATE_WORLD.brep'
    carrier=Part.read(str(carrier_path))
    def box(b):
        return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    anchors=[];geometry=[]
    for row in plan['towers']:
        bounds=row['bounds_mm'];stem=box(bounds)
        join=stem.common(carrier).Volume
        foot=None;nearest=None;new_join=join
        if join<=1e-6:
            point=A.Vector((bounds[0]+bounds[3])/2,(bounds[1]+bounds[4])/2,142)
            distance,pairs,_=Part.Vertex(point).distToShape(carrier)
            target=pairs[0][1];nearest=dict(distance_mm=distance,material_point_mm=[target.x,target.y,target.z])
            foot=[min(point.x,target.x)-2,min(point.y,target.y)-2,min(point.z,target.z)-2,
                  max(point.x,target.x)+2,max(point.y,target.y)+2,max(point.z,target.z)+2]
            shape=box(foot)
            new_join=shape.common(carrier).Volume
            assert stem.common(shape).Volume>0,row['name']
            geometry.append(shape)
        geometry.append(stem)
        anchors.append(dict(name=row['name'],stem_bounds_mm=bounds,
            full_stem_existing_material_join_mm3=join,foot_bounds_mm=foot,
            proposed_foot_existing_material_join_mm3=new_join,
            nearest_actual_material=nearest,foreign_contacts_pending=True))
        print('SIDE_ACTUAL_ANCHOR',row['name'],join,new_join,flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    p=OUT/'FourTowerAnchors_PROPOSED_WORLD.brep';Part.makeCompound(geometry).exportBrep(str(p))
    finish=datetime.now(timezone.utc)
    result=dict(plan)
    result.update(status='SIDE_RETENTION_ANCHORED_PROPOSAL_PREFLIGHT_PENDING',
        inherited_plan=path.relative_to(P.ROOT).as_posix(),anchors=anchors,
        simple_low_root_r1_rejected=True,
        all_anchors_have_actual_material_join=all(r['proposed_foot_existing_material_join_mm3']>1e-6 for r in anchors),
        four_root_material_joins_positive=False,
        all_foreign_contacts_pending=True,native_pending=True,selected=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={**plan['source_sha256'],path.relative_to(P.ROOT).as_posix():sha(path),
                       Path(__file__).relative_to(P.ROOT).as_posix():sha(Path(__file__)),
                       carrier_path.relative_to(P.ROOT).as_posix():sha(carrier_path)},
        files={p.relative_to(P.ROOT).as_posix():sha(p)})
    save(OUT/'plan.json',result)


if __name__=='__main__':
    main()
