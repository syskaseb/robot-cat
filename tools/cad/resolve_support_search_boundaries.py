"""One shared exact diagnosis of existing-cap exits and two arrival boxes."""
import json,time,itertools
from pathlib import Path
import FreeCAD as A
import build_complete_source_carriers as B
from diagnose_remaining_support_endpoints import transform,moved
P=B.P

def run():
    tick=time.monotonic()
    names=['remaining-support-current-paths.json','remaining-retention-current.json',
           'front-fixed-port-clearance-native.json','leg-source-near-member-plan.json',
           'complete-source-carriers-plan.json','remaining-loom-roots-plan.json']
    files=[P.OUT/n for n in names]
    paths,ret,native,family,old,roots=[json.loads(p.read_text()) for p in files]
    reader=B.H.P.SavedShapes();model=P.ROOT/native['native']
    assert P.SHA(model)==native['native_sha256']
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    exits=[];arrivals=[]
    for group in paths['groups']:
        contract=next(g for g in roots['groups'] if g['id']==group['id'])
        selected=next(g for g in ret['groups'] if g['id']==group['id'])
        if group['id'].endswith('HipExtension'):
            leg=group['id'].removesuffix('HipExtension');parent=reader.shape(model,contract['preserved_owner'])
            root=group['root_world_mm'];side=1 if 'Left' in leg else -1
            # Leave the bond via an ALREADY RECEIVED branch, not newly added
            # material. The connecting box must be a complete parent subset.
            end=[root[0],side*20,root[2]]
            bounds=[min(a,b)-h for a,b,h in zip(root,end,(2,3,2))]+[max(a,b)+h for a,b,h in zip(root,end,(2,3,2))]
            s=P.box(bounds);outside=s.cut(parent)
            exits.append(dict(group=group['id'],start=root,end=end,bounds_mm=bounds,
                outside_mm3=outside.Volume,valid=outside.isNull() or outside.isValid()))
        for failure in group['paths']:
            if failure.get('goal_blocker') is None:continue
            port=next(p for p in selected['ports'] if p['land_id']==failure['land_id'])
            x,y,z=port['arrival_world_mm'];seed=P.box([x-2,y-3,z-2,x+2,y+3,z+2])
            loom=failure['goal_blocker'].split('/')[-1];route=next(r for r in family['routes'] if r['loom']==loom)
            code=contract['owner_stage'].split('_')[1];rows=[]
            for h,k in itertools.product((-15,0,15),repeat=2):
                t=transform(axes,code,h,k,'Knee')
                w=P.wire(B.parts_for_loom(family,loom,h,k,axes)+B.moved_parts(route['source_parts'],route['source'],h,k,axes))
                rows.append(dict(hip=h,knee=k,gap_mm=moved(seed,t).distToShape(w)[0]))
            arrivals.append(dict(land_id=failure['land_id'],samples=rows,
                minimum_gap_mm=min(r['gap_mm'] for r in rows),required_arm_gap_mm=3.5,
                conservative_sampling_reservation_mm=4))
    result=dict(status='EXACT_BOUNDARY_DIAGNOSIS_NOT_SUPPORT_APPROVAL',existing_exits=exits,
        compact_arrivals=arrivals,source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in files+[model,af,Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False)
    (P.OUT/'remaining-support-boundaries.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':run()
