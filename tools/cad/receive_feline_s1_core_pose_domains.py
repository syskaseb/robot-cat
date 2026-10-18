"""Factor the proven10-part source core from provisional fixed fan directions.

Uses received cloud and unchanged fixed fields, no BRep/world rebuild.
All four fan choices must subsequently share this core pose in whole joint.
"""
import itertools
import json
import sys
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
import FreeCAD as A
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_flat_station_templates import shared_rail_bounds, to_box


def main():
    tick = time.monotonic()
    source = OUT/'n01-intrinsic-s1-whole-pose.json'
    received = json.loads(source.read_text())
    assert received['actual_ring_pair_receipts_reused_rigidly'] and not received['exact_new_cross_endpoint_failures']
    assert received['status'] != 'RUNNING_WHOLE_SOURCE_POSES', 'Receive active worker first'
    cloudpath = ROOT/received['base_cloud']
    assert sha(cloudpath) == received['base_cloud_sha256']
    cloud = np.load(cloudpath, allow_pickle=False)
    points = cloud['points'][cloud['types'] == 9]
    assert len(points)
    oldcentre = np.array(received['centre_mm'])
    fieldproof = OUT/'n01-flat20-field-modulejoint.json'
    proof = json.loads(fieldproof.read_text())
    path = ROOT/proof['field']
    assert sha(path) == proof['field_sha256']
    f = np.load(path, allow_pickle=False)
    axes = [f[k] for k in ('x','y','z')]
    grid = np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)
    fields = {k:RegularGridInterpolator(axes,f[k+'_distance'],bounds_error=False,fill_value=0)
              for k in ('material','reservation','curve_hold','motion36','outer')}
    for k in ('P_SYS','W043','BankTerm','P0Rail'):
        dd = cKDTree(f[k+'_context']).query(grid.reshape(-1,3),workers=1)[0].reshape(grid.shape[:3])
        fields[k] = RegularGridInterpolator(axes,dd,bounds_error=False,fill_value=0)
    inside = RegularGridInterpolator(axes,f['inside'].astype(float),bounds_error=False,fill_value=0)
    service = RegularGridInterpolator(axes,f['service'].astype(float),method='nearest',bounds_error=False,fill_value=1)
    result = dict(selected=False,N01_complete=False,physical_pass=False,status='RUNNING_CORE_POSES',
                  core_parts=10,proven_four_rings_included=True,fans_not_deleted_from_design=True,
                  four_whole_fans_must_share_core_pose_in_subsequent_joint=True,
                  no_unchanged_fixed_source_matrix_rebuilt=True,pose_domains=[],rejected={},attempts=0,
                  source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
                      (source,cloudpath,fieldproof,path,Path(__file__))})
    dest = OUT/'n01-s1-core-pose-domains.json'
    skip = 0
    if '--resume' in sys.argv:
        previous = json.loads(dest.read_text())
        assert previous['status'] == 'PARTIAL_CORE_POSES_RECEIVED'
        for n,h in previous['source_sha256'].items():
            if n != Path(__file__).relative_to(ROOT).as_posix():assert sha(ROOT/n)==h,n
        skip = previous['attempts']
        previous.setdefault('previous_worker_seconds',[]).append(previous['worker_seconds'])
        previous['resumed_attempts_without_requery'] = skip
        previous['status'] = 'RUNNING_CORE_POSES'
        previous['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
        result = previous
    def save():
        result['worker_seconds'] = round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    for index,(x,y,z,yaw,roll) in enumerate(itertools.product(range(-108,109,24),range(-36,37,12),(-24,0,24,48,72),(0,90,180,270),(0,90))):
        if index < skip:continue
        if time.monotonic()-tick > 90:
            result['status'] = 'PARTIAL_CORE_POSES_RECEIVED'
            break
        pr = A.Rotation(A.Vector(0,0,1),yaw)*A.Rotation(A.Vector(1,0,0),roll)
        matrix = np.array([list(pr.multVec(A.Vector(*v))) for v in np.eye(3)]).T
        p = (points-oldcentre)@matrix.T+np.array([x,y,z])
        result['attempts'] += 1
        label,margin = 'none',1e6
        if any(p[:,i].min()<axis[0] or p[:,i].max()>axis[-1] for i,axis in enumerate(axes)):
            label,margin = 'outside_field_bounds',-1e6
        elif inside(p).min()<.999:
            label,margin = 'outside_outline',-1e6
        else:
            for label,interp in fields.items():
                req = 1 if label=='outer' else 3.35 if label=='curve_hold' else .2
                margin = min(margin,float(interp(p).min()-req))
                if margin<0:
                    break
            if margin>=0 and service(p).max()>.5:
                label,margin = 'ATO_access',-.01
            if margin>=0:
                for rail in shared_rail_bounds():
                    margin = min(margin,float(to_box(p,rail).min()-.2))
                if margin<0:label='common_low_rail'
        if margin>=0:
            result['pose_domains'].append(dict(centre_mm=[x,y,z],rotation_rows=matrix.tolist(),yaw_degrees=yaw,roll_degrees=roll,numeric_margin_mm=margin))
        else:
            result['rejected'][label] = result['rejected'].get(label,0)+1
        if result['attempts']%100==0:save()
    else:
        result['status']='CORE_POSE_DOMAINS_RECEIVED_NOT_COMPLETE_SOURCE_OR_N01'
    save()
    print(json.dumps(dict(seconds=result['worker_seconds'],attempts=result['attempts'],domains=len(result['pose_domains']),rejected=result['rejected'],status=result['status'])),flush=True)


if __name__ == '__main__':
    main()
