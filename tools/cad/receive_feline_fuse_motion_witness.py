"""Resolve a conservative FHAC motion-screen witness in the source BRep.

No geometry retry and no whole-motion PASS: receive nearest named actual
source/pose, stop at a real nominal-gap failure, preserve every checked pair.
"""
import json
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,SavedShapes,sha,prop
from plan_feline_layout import OUT,BASE,MODEL,STAGES,transforms
from plan_feline_skin_access import surface_samples


def main():
    tick=time.monotonic();dest=OUT/'n01-dedicated-fuse-motion-witness.json';assert not dest.exists()
    files=dict(proof=OUT/'n01-dedicated-fuse-bays.json',atlas=OUT/'n01-shared-space-atlas-received.json',
        voxels=OUT/'n01-shared-space-atlas-voxels.npz',inventory=OUT/'n01-remaining-selected-inventory.json',
        motion=OUT/'motion-layout.json',axes=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json')
    p={k:json.loads(f.read_text()) for k,f in files.items() if f.suffix=='.json'}
    assert p['proof']['status']=='COUPLED_SIDE_DOMAINS_RECEIVED_NOT_N01'
    assert sha(files['voxels'])==p['atlas']['voxel_cache_sha256']
    reader=SavedShapes();r=next(r for r in p['inventory']['parts'] if r['role']=='F_HY' and not r['placed_current'])
    bundle=ROOT/p['inventory']['bundle'];assert sha(bundle)==p['inventory']['bundle_sha256']
    with zipfile.ZipFile(bundle) as z:
        raw=z.read(r['entry']);assert __import__('hashlib').sha256(raw).hexdigest()==r['sha256']
    case=Part.Shape();case.importBrepFromString(raw.decode('utf-8'));rot=A.Rotation(A.Vector(0,1,0),-90)
    centre=p['proof']['dedicated_fuse_bays']['case_centres_mm']['F_HY']
    case.Placement=A.Placement(A.Vector(*centre)-rot.multVec(case.BoundBox.Center),rot)*case.Placement
    assert case.isValid() and case.Solids
    owners=np.load(files['voxels'],allow_pickle=False)['motion36'];ids=np.flatnonzero(owners)
    dims=np.array([337,209,173]);cloud=np.column_stack((ids//(dims[1]*dims[2]),ids//dims[2]%dims[1],ids%dims[2]))+np.array([-147,-104,-54])
    v,f=case.tessellate(.6);v=np.array([list(x) for x in v]);pts=surface_samples(v[np.array(f,dtype=int)],2)
    distance,index=cKDTree(cloud).query(pts,workers=1);order=np.argsort(distance);targets=[];seen=set()
    for i in order:
        owner=int(owners[ids[index[i]]])-1
        if owner in seen:continue
        seen.add(owner);targets.append(dict(atlas_row=owner,voxel_distance_mm=float(distance[i]),
            candidate_surface_point_mm=pts[i].tolist(),motion_voxel_point_mm=cloud[index[i]].tolist()))
        if len(targets)>=12:break
    result=dict(status='RUNNING_NAMED_SOURCE_MOTION_WITNESS',selected=False,N01_complete=False,physical_pass=False,
        case_centre_mm=centre,completed_queries=[],errors=[],
        conservative_atlas_not_treated_as_collision=True,whole_motion_not_qualified=True,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*files.values(),bundle,MODEL,Path(__file__))})
    def save():
        result['source_sha256'].update(reader.hashes);result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    try:
        for row in targets:
            if time.monotonic()-tick>90:raise TimeoutError('90s witness receiver cap')
            source=p['atlas']['parts'][row['atlas_row']];assert source['category']=='motion36'
            original=reader.shape(MODEL,source['source']);assert original.isValid() and original.Solids
            axes=[next(a for a in p['axes']['axes'] if a['code']==source['leg'] and a['stage']==stage) for stage in STAGES]
            pose=p['motion']['poses'][source['pose_index']]['legs'][source['leg']]
            rotation,translation=transforms(axes,pose['angles_delta_degrees'])[STAGES.index(source['stage'])]
            m=A.Matrix()
            for i in range(3):
                for j in range(3):setattr(m,f'A{i+1}{j+1}',float(rotation[i,j]))
            transformed=original.copy();transformed.Placement=A.Placement(A.Vector(*translation),A.Rotation(m))*transformed.Placement
            assert transformed.isValid() and transformed.Solids
            gap=case.distToShape(transformed)[0]
            label=prop(reader.doc(MODEL)[source['source']],'Label')[0].get('value')
            record=dict(row,source=source,label=label,physical_leg=pose['physical_leg'],
                actual_BRep_gap_mm=gap,required_mm=1.25,zero_distance_not_positive_volume_proof=True)
            result['completed_queries'].append(record);save()
            if gap<1.25-1e-5:
                result['status']='NAMED_SOURCE_MOTION_GAP_FAILURE_CONFIRMED_NOT_VOLUME_PROOF';break
        else:result['status']='NEAREST_SOURCE_WITNESSES_CLEAR_REMAINDER_MOTION_OPEN'
    except Exception as e:result['status']='PARTIAL_NAMED_SOURCE_MOTION_WITNESS';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],pairs=len(result['completed_queries']),errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
