"""Whole occupied Pi module planning, not another cable-only local retry.

Use all rigid ports and all existing full first-bend/9mm wire resources in
ONE pose. A conservative cached-volume proposal is not CAD acceptance.
Selected parts/native remain unchanged. Old S1/core870/2800/5600 closed.
"""
import hashlib,io,itertools,json,math,os,sys,time,zipfile
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt,map_coordinates,binary_dilation
from scipy.signal import fftconvolve
from scipy.spatial.transform import Rotation
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_common_space_context import current,is_jacket
from feline_signed_voxels import deposit


def main():
    tick=time.monotonic();rigid_only='--rigid-ports-convolution' in sys.argv;world,parts,meta,pins,docs=current()
    own={n:s for n,s in parts.items() if meta[n].get('group')=='PiUpper'}
    assert len(own)>35 and 'Ref_Material_Pi4NominalPCB_0_0' in own
    pcb=own['Ref_Material_Pi4NominalPCB_0_0'];centre=np.array(list(pcb.BoundBox.Center))
    face=max(pcb.Faces,key=lambda f:f.Area);z=np.array(list(face.normalAt(0,0)));z/=np.linalg.norm(z)
    edge=max(face.Edges,key=lambda e:e.Length);x=np.array(list(edge.Vertexes[-1].Point-edge.Vertexes[0].Point));x/=np.linalg.norm(x)
    y=np.cross(z,x);y/=np.linalg.norm(y);basis=np.column_stack([x,y,z]);assert np.allclose(basis.T@basis,np.eye(3))
    sf=OUT/'n01-current-signed-space.json';old=json.loads(sf.read_text());field=ROOT/old['field'];archive=ROOT/old['voxel_source_archive']
    assert sha(field)==old['field_sha256'] and sha(archive)==old['voxel_source_archive_sha256']
    lower=OUT/'n01-usb-fore-lower-deck-space.json';low=json.loads(lower.read_text())
    assert low['status']=='TWO_WHOLE_FORE_KITS_LOWER_DECK_SPACE_RECEIVED_USB_ROOTS_OPEN'
    shifted=set(low['changed_owners'])
    with np.load(field,allow_pickle=False) as f:
        origin=f['origin_mm'];rigid=np.zeros_like(f['rigid_occupied']);motion=f['motion36_signed_distance'];outer=f['outer_distance']
    clouds=[];accounted=set()
    with zipfile.ZipFile(archive) as zz:
        for key,r in old['parts'].items():
            if not key.startswith('Static:'):continue
            n=key[7:];raw=zz.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            with np.load(io.BytesIO(raw),allow_pickle=False) as f:local=f['origin'];mask=f['occupied']
            if n in own:
                ids=np.argwhere(mask)
                # Every occupied cell, including closed source interiors.
                if len(ids) and (not rigid_only or not is_jacket(n,meta[n])):clouds.append(local+ids)
                accounted.add(n);continue
            if n in shifted:local=local+np.array([0,0,-8])
            if not is_jacket(n,meta[n]):deposit(rigid,mask,local,origin)
    missing=set(own)-accounted
    assert all(not own[n].Solids for n in missing),missing
    cloud=np.vstack(clouds)-centre;full_cloud=cloud.copy()
    # Deterministic2mm-cell sample for proposals, never actual clearance.
    _,ids=np.unique(np.rint(cloud/2).astype(int),axis=0,return_index=True);cloud=cloud[np.sort(ids)]
    distance=distance_transform_edt(~rigid).astype(np.float32);distance[rigid]=-distance_transform_edt(rigid)[rigid]
    dest=OUT/('n01-whole-pi-rigid-ports-space.json' if rigid_only else 'n01-whole-pi-occupied-pose-space.json');assert not dest.exists()
    result=dict(status='RUNNING_WHOLE_PI_OCCUPIED_POSES',source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (sf,field,archive,lower,Path(__file__))}},
        own_parts=list(own),voxelized_own_parts=len(accounted),source_PCB_centre_mm=centre.tolist(),source_PCB_basis=basis.tolist(),
        proposal_points=len(cloud),proposals=[],tested=0,N01_complete=False,physical_pass=False,selected=False,
        all_actual_ports_and_existing_prefixes_moved_together=not rigid_only,all_rigid_PCB_hardware_and_occupied_ports_together=True,
        old_elastic_prefixes_not_frozen_for_changed_PCB=rigid_only,not_new_2800_S1_core_search=True,
        every_new_route_root_grip_factory_length_and_exact_geometry_gate_OPEN=True)
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    usb=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb'];mouth=np.array(usb['pi_jacket_mouth_mm'])
    bus=np.array(usb['bus_jacket_mouth_mm']);rotations=Rotation.create_group('O').as_matrix();save()
    if rigid_only:
        result['orientation_domains']=[]
        free=(distance>=1.25)&(motion>=1.25)&(outer>=3.25)
        occupied=(~free).astype(np.float32)
        for index,target_basis in enumerate(rotations):
            rot=target_basis@basis.T;local=full_cloud@rot.T
            lo=np.floor(local.min(0)).astype(int)-2;high=np.ceil(local.max(0)).astype(int)+2
            kernel=np.zeros(tuple(high-lo+1),bool);ids=np.rint(local-lo).astype(int);kernel[tuple(ids.T)]=True
            # One neighbour layer covers rotated source cubes plus rounding;
            # occupied interiors are retained, not a surface-only hull.
            kernel=binary_dilation(kernel,structure=np.ones((3,3,3),bool))
            collision=fftconvolve(occupied,kernel[::-1,::-1,::-1].astype(np.float32),mode='valid')
            valid=np.argwhere(collision<.25);result['tested']+=int(collision.size)
            result['orientation_domains'].append(dict(orientation_index=index,kernel_shape=list(kernel.shape),
                kernel_occupied_cells=int(kernel.sum()),candidate_translations=int(len(valid)),
                minimum_collision_voxels=float(collision.min()),FFT_zero_tolerance_cells=.25))
            if len(valid):
                centres=origin+valid-lo;mouths=(mouth-centre)@rot.T+centres
                scores=np.linalg.norm(mouths-bus,axis=1)+.05*np.linalg.norm(centres-centre,axis=1)
                for j in np.argsort(scores)[:10]:
                    result['proposals'].append(dict(orientation_index=index,target_PCB_centre_mm=centres[j].tolist(),rotation=rot.tolist(),
                        USB_mouth_mm=mouths[j].tolist(),USB_departure_axis=(np.array([-1.,0,0])@rot.T).tolist(),
                        USB_direct_chord_mm=float(np.linalg.norm(mouths[j]-bus)),rigid_only_all_new_elastic_prefixes_OPEN=True))
            save();print('PI_RIGID_PORT_DOMAIN',index,'positions',len(valid),flush=True)
            if time.monotonic()-tick>180:break
        result['proposals'].sort(key=lambda r:r['USB_direct_chord_mm'])
        result['status']='WHOLE_PI_RIGID_PORT_POSE_PROPOSALS_ALL_NEW_LOOMS_OPEN' if result['proposals'] else 'RIGID_PORT_TRANSLATION_DOMAINS_NO_PROPOSAL_NOT_EXACT_INFEASIBILITY'
        save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],tested=result['tested'],proposals=result['proposals'][:3])),flush=True);return
    for index,target_basis in enumerate(rotations):
        rot=target_basis@basis.T;local=cloud@rot.T
        for c in itertools.product((-75.,-25.,25.,75.,125.),(-65.,0.,65.),(25.,55.,85.)):
            result['tested']+=1;points=local+np.array(c);coords=(points-origin).T
            if np.any(coords<0) or np.any(coords>=np.array(rigid.shape)[:,None]-1):continue
            gaps=[float(map_coordinates(f,coords,order=1,mode='constant',cval=-100,prefilter=False).min()) for f in (distance,motion,outer)]
            if min(gaps[0]-2.45,gaps[1]-2.45,gaps[2]-4.45)<0:continue
            q=(mouth-centre)@rot.T+np.array(c);d=np.array([-1.,0,0])@rot.T
            result['proposals'].append(dict(orientation_index=index,target_PCB_centre_mm=list(c),rotation=rot.tolist(),
                static_gap_proposal_mm=gaps[0],motion_gap_proposal_mm=gaps[1],outer_gap_proposal_mm=gaps[2],
                USB_mouth_mm=q.tolist(),USB_departure_axis=d.tolist(),USB_direct_chord_mm=float(np.linalg.norm(bus-q))))
        save()
        if time.monotonic()-tick>150:break
    result['proposals'].sort(key=lambda r:r['USB_direct_chord_mm'])
    result['status']='WHOLE_PI_OCCUPIED_POSE_PROPOSALS_EXACT_GATES_OPEN' if result['proposals'] else 'BOUNDED_WHOLE_PI_OCCUPIED_POSE_GRID_NO_PROPOSAL_NOT_INFEASIBILITY'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],tested=result['tested'],proposals=result['proposals'][:3])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
