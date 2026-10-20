"""One whole-interface hypothesis using existing biarcs; no optimizer.

Nearest graph nodes are proposals, never endpoint links. Test all216 links
at once to expose layout families before detailed routing. A voxel rejection
is not a confirmed part collision and a positive link is not bundle packing.
"""
import collections,gzip,json,math,time
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from build_feline_retention_space_delta import load_fields
from feline_tangent_routes import biarc,min_radius,samples,unit,sub,norm


def link(p,d,q,t,minimum):
    parts=biarc(p,d,q,t)
    assert norm(sub(parts[0]['start'],p))<1e-6
    assert norm(sub(parts[-1]['end'],q))<1e-6
    radius=min_radius(parts)
    points=np.asarray([v for s in parts for v in samples(s,.5)])
    return parts,points,float(radius),bool(radius+1e-6>=minimum)


def field_test(points,radius,fields):
    indices=np.rint(points-fields['origin_mm']).astype(int)
    within=np.all(indices>=0,axis=1)&np.all(indices<np.asarray(fields['inside'].shape),axis=1)
    if not within.all():return dict(status='OUTSIDE_TORSO_FIELD_NOT_PART_COLLISION',samples_outside=int((~within).sum()))
    ix=tuple(indices.T)
    rigid=fields['rigid_signed_distance'][ix]-radius-2.45
    motion=fields['motion36_signed_distance'][ix]-radius-2.45
    outer=fields['outer_distance'][ix]-radius-4.45
    ok=fields['inside'][ix]&(rigid>=0)&(motion>=0)&(outer>=0)
    return dict(status='POSITIVE_CONSERVATIVE_FIELD_ONLY' if ok.all() else 'PROPOSAL_FIELD_HOLD_NOT_EXACT_COLLISION',
        minima_mm=dict(rigid=float(rigid.min()),motion=float(motion.min()),outer=float(outer.min())),
        first_unqualified_mm=points[np.flatnonzero(~ok)[0]].tolist() if not ok.all() else None)


def main():
    tick=time.monotonic();nf=OUT/'n01-current-corridor-topology.json';network=json.loads(nf.read_text())
    af=ROOT/network['assignments'];assert sha(af)==network['assignments_sha256']
    assignments=json.loads(gzip.decompress(af.read_bytes()));fields,_=load_fields()
    rows={};counts=collections.Counter();families=collections.defaultdict(collections.Counter)
    for name,r in assignments.items():
        if not r.get('anchors'):continue
        for side,(e,a) in enumerate(zip(r['ends'],r['anchors'])):
            # Goal graph tangent points toward its endpoint. Reverse it to
            # construct this link outward from BOTH actual source surfaces.
            t=np.asarray(a['heading'])*(1 if side==0 else -1)
            row=dict(portion=name,side=side,source=e['point_mm'],source_axis=e['outward_axis'],
                anchor=a['anchor_mm'],anchor_axis=t.tolist(),required_R_mm=r['minimum_R_mm'])
            try:
                parts,points,R,ok=link(e['point_mm'],e['outward_axis'],a['anchor_mm'],t,r['minimum_R_mm'])
                row.update(parts=parts,constructed_R_mm=R if math.isfinite(R) else None,
                    radius_qualified=ok,field=field_test(points,r['radius_mm'],fields))
                row['status']='RADIUS_HOLD_THIS_SINGLE_BIARC' if not ok else row['field']['status']
            except ValueError as exc:row.update(status='NO_FORWARD_BIARC_THIS_SINGLE_HYPOTHESIS',reason=str(exc))
            rows[e['id']]=row;counts[row['status']]+=1
            family='lower_4MTA' if '/custom/' in e['id'] else ('WAGO_row' if abs(e['point_mm'][1]) in (44.25,57.25) else 'other_sources')
            families[family][row['status']]+=1
    assert len(rows)==216,(len(rows),'Do not silently drop ordinary source links')
    archive=OUT/'n01-current-source-link-hypothesis.json.gz'
    archive.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    result=dict(status='WHOLE216_SINGLE_BIARC_HYPOTHESIS_RECEIVED_NOT_LAYOUT_ACCEPTANCE',
        links=len(rows),summary=dict(counts),families={k:dict(v) for k,v in families.items()},
        details=archive.relative_to(ROOT).as_posix(),details_sha256=sha(archive),
        hypotheses_per_link=1,exact_part_collision_not_inferred_from_field_hold=True,
        harness_packing_full_end_to_end_paths_roots_and_access_OPEN=True,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (nf,af,Path(__file__),ROOT/'tools/cad/feline_tangent_routes.py',OUT/'n01-retention-space-delta.json')},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-current-source-link-hypothesis.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
