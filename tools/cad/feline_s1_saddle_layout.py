"""Source-owned S1 pose and four independent simple saddle/tie fan proposals.

Planning only. Purchased pinwheel is rigidly preserved. No cloud result grants
N01 or actual contact/clearance. One resumable output, not per-offset reports.
"""
import itertools
import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree

from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_flat_station_templates import box_points, compact, shared_rail_bounds, to_box


def load_sources():
    corepath = OUT / 'n01-s1-core-pose-domains.json'
    core = json.loads(corepath.read_text())
    assert core['status'] == 'CORE_POSE_DOMAINS_RECEIVED_NOT_COMPLETE_SOURCE_OR_N01'
    assert core['attempts'] == 2800
    # Resume-wrapper edits do not affect received geometry; no geometry edits
    # are made to that receiver in this implementation.
    for name, h in core['source_sha256'].items():
        assert sha(ROOT/name) == h, name
    packetpath = OUT / 'n01-intrinsic-s1-whole-pose.json'
    packet = json.loads(packetpath.read_text())
    data = np.load(ROOT/packet['base_cloud'], allow_pickle=False)
    sourcepoints = data['points'][data['types'] == 9]
    proofpath = OUT / 'n01-flat20-field-modulejoint.json'
    proof = json.loads(proofpath.read_text())
    fieldpath = ROOT/proof['field']
    assert sha(fieldpath) == proof['field_sha256']
    f = np.load(fieldpath, allow_pickle=False)
    axes = [f[k] for k in ('x', 'y', 'z')]
    fields = {k: RegularGridInterpolator(axes, f[k+'_distance'], bounds_error=False, fill_value=0)
              for k in ('material', 'reservation', 'curve_hold', 'motion36', 'outer')}
    grid = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1)
    for k in ('P_SYS', 'W043', 'BankTerm', 'P0Rail'):
        dd = cKDTree(f[k+'_context']).query(grid.reshape(-1,3), workers=1)[0].reshape(grid.shape[:3])
        fields[k] = RegularGridInterpolator(axes, dd, bounds_error=False, fill_value=0)
    inside = RegularGridInterpolator(axes, f['inside'].astype(float), bounds_error=False, fill_value=0)
    service = RegularGridInterpolator(axes, f['service'].astype(float), method='nearest', bounds_error=False, fill_value=1)
    pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in
            (corepath, packetpath, ROOT/packet['base_cloud'], proofpath, fieldpath, Path(__file__),
             ROOT/'tools/cad/feline_flat_station_templates.py')}
    return core, packet, sourcepoints, fields, inside, service, pins


def pose_points(points, packet, pose):
    return (points-np.array(packet['centre_mm']))@np.array(pose['rotation_rows']).T + np.array(pose['centre_mm'])


def source_core(packet, pose, points, pose_id):
    p = pose_points(points, packet, pose)
    return dict(ref='S1_core', source_core=True, core_pose_id=pose_id,
                centre_mm=pose['centre_mm'], rotation_rows=pose['rotation_rows'],
                points=p, radii=np.zeros(len(p)), types=np.full(len(p),9),
                bounds=np.array([p.min(0),p.max(0)]), boxes=[], wires=[])


def fan(packet, pose, recipe, pose_id, bend_angle, head_angle):
    """One 9mm lower saddle and one tie per jacket; no upper rigid clamp.

    The lower half has 2mm PETG nominal wall. The tie is a full closed loop
    (1.2mm budget), with a full6cube head. Four saddles share a future carrier;
    carrier roots are NOT silently represented by zero material.
    """
    q = np.array(recipe['point_mm']); d = np.array(recipe['departure_axis'])
    n = np.array([0.,0.,1.]); v = np.cross(d,n)
    b = math.cos(math.radians(bend_angle))*n + math.sin(math.radians(bend_angle))*v
    first, R, radius = 12., 25.2, 2.1
    a = q+first*d; aa = np.linspace(0,math.pi/2,42)
    arc = a+R*np.sin(aa)[:,None]*d+R*(1-np.cos(aa))[:,None]*b
    wire = np.vstack((np.linspace(q,a,13),arc,np.linspace(arc[-1],arc[-1]+9*b,10)))
    # Filled semicircular saddle cross-section, not just its outside surface.
    saddle = []
    for x,t,r in itertools.product(np.linspace(3,12,6),np.linspace(math.pi,2*math.pi,17),np.linspace(2.1,4.1,3)):
        saddle.append(q+x*d+r*(math.cos(t)*v+math.sin(t)*n))
    saddle = np.array(saddle)
    # Upper tie rides directly on the jacket, lower tie around the saddle.
    band = []
    for x,t,thick in itertools.product((6.25,7.5,8.75),np.linspace(0,2*math.pi,33), (0.,1.2)):
        rr = (2.1 if math.sin(t)>=0 else 4.1)+thick
        band.append(q+x*d+rr*(math.cos(t)*v+math.sin(t)*n))
    # The semicircular saddle has two radial shoulders: reserve both tie
    # transitions too, otherwise the upper and lower half loops are detached.
    for x,sign,r,z in itertools.product((6.25,7.5,8.75),(-1,1),np.linspace(2.1,5.3,5),(-.6,.6)):
        band.append(q+x*d+sign*r*v+z*n)
    band = np.array(band)
    ht = math.radians(head_angle)
    # Head centre beyond the complete band exterior; no hidden/missing head.
    radial = 2.1 if math.sin(ht)>=0 else 4.1
    h = q+7.5*d+(radial+1.2+3)*(math.cos(ht)*v+math.sin(ht)*n)
    head = box_points(h-3,h+3)
    p = pose_points(np.vstack((wire,saddle,band,head)),packet,pose)
    rr = np.r_[np.full(len(wire),radius),np.zeros(len(saddle)+len(band)+len(head))]
    tt = np.r_[np.ones(len(wire),int),np.full(len(saddle)+len(band)+len(head),2)]
    matrix = np.array(pose['rotation_rows'])
    qw = pose_points(q[None,:],packet,pose)[0]
    return dict(ref=recipe['ref'], source_fan=True, core_pose_id=pose_id,
                point_mm=qw.tolist(), departure_axis=(matrix@d).tolist(),
                bend_unit=(matrix@b).tolist(), first_mm=first, R_mm=R, radius_mm=radius,
                bend_degrees=bend_angle, head_degrees=head_angle,
                grip_start_mm=3, grip_length_mm=9, saddle_wall_mm=2,
                band_wall_budget_mm=1.2, head_budget_mm=[6,6,6],
                upper_rigid_cap_removed=True, each_wire_independent_tie=True,
                common_carrier_root_and_exact_core_fit_OPEN=True,
                after_arc_end_mm=pose_points((arc[-1]+9*b)[None,:],packet,pose)[0].tolist(),
                points=p,radii=rr,types=tt,
                bounds=np.array([(p-rr[:,None]).min(0),(p+rr[:,None]).max(0)]),boxes=[],wires=[])


def world_score(m, fields, inside, service):
    p,rr = m['points'],m['radii']
    if inside(p).min()<.999:return -1e6,'outside'
    best,label = 1e6,'none'
    for k,interp in fields.items():
        need = 1 if k=='outer' else 3.35 if k=='curve_hold' else .2
        val = float(np.min(interp(p)-rr-need))
        if val<best:best,label=val,k
    if best>=0 and service(p).max()>.5:return -.01,'ATO_access'
    for rail in shared_rail_bounds():
        val = float(np.min(to_box(p,rail)-rr-.2))
        if val<best:best,label=val,'common_low_rail'
    return best,label


def receive_domains():
    tick=time.monotonic()
    core,packet,sourcepoints,fields,inside,service,pins=load_sources()
    dest=OUT/'n01-s1-saddle-layout.json'
    result=dict(status='RUNNING_S1_SADDLE_DOMAINS',selected=False,N01_complete=False,physical_pass=False,
                source_sha256=pins,received_core_poses=len(core['pose_domains']),
                reused_core_attempts=2800,independent_four_fan_choices=True,
                source_ring_pinwheel_unchanged=True,full_roots_and_tools_STILL_OPEN=True,
                poses=[],rejected={},completed_pose_ids=[])
    if dest.exists():
        old=json.loads(dest.read_text())
        assert old['source_sha256']==pins,'Geometry/input change invalidates prior saddle domains'
        assert old['status'] in ('PARTIAL_S1_SADDLE_DOMAINS','S1_SADDLE_DOMAINS_RECEIVED')
        result=old;result.setdefault('previous_worker_seconds',[]).append(old['worker_seconds'])
        result['status']='RUNNING_S1_SADDLE_DOMAINS'
    done=set(result['completed_pose_ids'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    for pose_id,pose in enumerate(core['pose_domains']):
        if pose_id in done:continue
        # Save at complete source-pose boundaries. No requery of received poses.
        if time.monotonic()-tick>120:
            result['status']='PARTIAL_S1_SADDLE_DOMAINS';break
        rows={}
        for recipe in packet['recipes']:
            accepted=[]
            for bend,head in itertools.product(range(0,360,45),(0,90,180,270)):
                m=fan(packet,pose,recipe,pose_id,bend,head)
                val,why=world_score(m,fields,inside,service)
                if val>=0:m['numeric_score']=val;accepted.append(compact(m))
                else:result['rejected'][why]=result['rejected'].get(why,0)+1
            rows[recipe['ref']]=sorted(accepted,key=lambda m:-m['numeric_score'])
        result['poses'].append(dict(core_pose_id=pose_id,pose=pose,fan_domains=rows,
                                   all_four_nonempty=all(rows.values())))
        result['completed_pose_ids'].append(pose_id);save()
        print('S1pose',pose_id,'four full saddle fans', {k:len(v) for k,v in rows.items()},flush=True)
    else:result['status']='S1_SADDLE_DOMAINS_RECEIVED'
    result['all_four_domain_poses']=[r['core_pose_id'] for r in result['poses'] if r['all_four_nonempty']]
    save()
    print(json.dumps(dict(status=result['status'],worker_seconds=result['worker_seconds'],
                         poses=len(result['poses']),all_four_domain_poses=result['all_four_domain_poses'])),flush=True)


if __name__=='__main__':receive_domains()
