"""Choose source portals by tangent/radius before distance, without moving parts.

Bounded use of existing biarcs and received graph states, not another voxel
route solver. Retain unresolved endpoint clearance explicitly for exact CAD.
No full wire, shared cross-section or installation acceptance is implied.
"""
import collections,gzip,json,math,os,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_tangent_routes import biarc,min_radius,samples
from build_feline_retention_space_delta import load_fields
from plan_feline_tangent_corridor_network import DIRECTIONS


def classify(points,radius,fields):
    ix=np.rint(points-fields['origin_mm']).astype(int)
    inside=np.all(ix>=0,1)&np.all(ix<np.asarray(fields['inside'].shape),1)
    if not inside.all():return None
    at=tuple(ix.T)
    clear=np.minimum(fields['rigid_signed_distance'][at],fields['motion36_signed_distance'][at])-radius-2.45
    clear=np.minimum(clear,fields['outer_distance'][at]-radius-4.45)
    clear=np.minimum(clear,np.where(fields['inside'][at],1e6,-1e6))
    return clear


def main():
    tick=time.monotonic();nf=OUT/'n01-current-corridor-topology.json';network=json.loads(nf.read_text())
    af=ROOT/network['assignments'];assert sha(af)==network['assignments_sha256']
    assignments=json.loads(gzip.decompress(af.read_bytes()));fields,_=load_fields();trees={};pins={}
    dest=OUT/'n01-curvature-source-portals.json';rawfile=dest.with_suffix('.rows.json.gz')
    rows={};counts=collections.Counter();evaluated=0
    for name,r in assignments.items():
        if not r.get('anchors'):continue
        key=r['corridor_class'];component=r['component'];tk=(key,component)
        if tk not in trees:
            f=ROOT/network['classes'][key]['nodes'];assert sha(f)==network['classes'][key]['nodes_sha256'];pins[f.relative_to(ROOT).as_posix()]=sha(f)
            with np.load(f,allow_pickle=False) as a:
                cells=np.argwhere(a['ids']>=0);base=a['ids'][tuple(cells.T)];cc=a['component'];origin=a['origin_mm'];step=float(a['step_mm'])
                trees[tk]=[]
                for h in range(6):
                    points=origin+step*cells[cc[base*6+h]==component]
                    trees[tk].append((points,cKDTree(points)))
        for side,e in enumerate(r['ends']):
            q=np.asarray(e['point_mm']);d=e['outward_axis'];Rmin=r['minimum_R_mm'];geometry=[]
            for h,(points,tree) in enumerate(trees[tk]):
                if not len(points):continue
                distances,indices=tree.query(q,k=min(128,len(points)),distance_upper_bound=4*Rmin+32)
                target=DIRECTIONS[h]*(1 if side==0 else -1)
                for distance,i in zip(np.atleast_1d(distances),np.atleast_1d(indices)):
                    if not math.isfinite(distance):continue
                    evaluated+=1
                    try:parts=biarc(q,d,points[i],target)
                    except ValueError:continue
                    R=min_radius(parts)
                    if R+1e-6<Rmin:continue
                    length=sum(p['length'] for p in parts)
                    geometry.append((length,h,tuple(points[i]),parts,R))
            # Whole-tangent candidates are ranked once. No scalar source offsets,
            # rejected core poses or part placements are generated.
            choices=[]
            for length,h,p,parts,R in sorted(geometry,key=lambda x:x[0])[:24]:
                points=np.asarray([v for s in parts for v in samples(s,.5)])
                clear=classify(points,r['radius_mm'],fields)
                if clear is None:continue
                bad=clear<0
                choice=dict(anchor_mm=list(p),graph_heading=DIRECTIONS[h].tolist(),
                    parts=parts,length_mm=length,minimum_constructed_R_mm=float(R) if math.isfinite(R) else None,
                    field_minimum_mm=float(clear.min()),unqualified_samples=int(bad.sum()),
                    sampled_points=len(points),first_unqualified_mm=points[np.flatnonzero(bad)[0]].tolist() if bad.any() else None,
                    last_unqualified_mm=points[np.flatnonzero(bad)[-1]].tolist() if bad.any() else None)
                choices.append(choice)
                if not bad.any():break
            row=dict(portion=name,side=side,source=e,minimum_project_R_mm=Rmin,radius_mm=r['radius_mm'],
                corridor_class=key,component=component,curvature_valid_candidates=len(geometry))
            if choices:
                best=min(choices,key=lambda x:(x['unqualified_samples'],x['length_mm']));row.update(candidate=best,
                    status='POSITIVE_SOURCE_PORTAL_FIELD_ONLY' if not best['unqualified_samples'] else 'CURVATURE_VALID_EXACT_SOURCE_CLEARANCE_OPEN')
            else:row['status']='NO_PORTAL_IN_BOUNDED_CURRENT_COMPONENT_NOT_INFEASIBILITY'
            rows[e['id']]=row;counts[row['status']]+=1
        print(name,dict(counts),flush=True)
    assert len(rows)==216
    rawfile.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (nf,af,Path(__file__),ROOT/'tools/cad/feline_tangent_routes.py',OUT/'n01-retention-space-delta.json')})
    result=dict(status='CURVATURE_AWARE_SOURCE_PORTALS_RECEIVED_NOT_WHOLE_N01',links=len(rows),summary=dict(counts),
        bounded_poses_considered=evaluated,source_parts_never_moved=True,graph_states_per_heading_limit=128,
        exact_source_clearance_shared_packing_other_roots_motion_and_installation_OPEN=True,
        rows=rawfile.relative_to(ROOT).as_posix(),rows_sha256=sha(rawfile),source_sha256=pins,
        N01_complete=False,selected=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(json.dumps(result),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
