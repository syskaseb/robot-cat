"""Read existing actual source cap profiles, never infer manufacturer OD.

Use the frozen216 physical portal boundary points/tangents. Keep unmatched
provisional profiles OPEN. No guide, wire or purchased geometry is changed.
"""
import gzip,json,math,os,time
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_retention_composed_context import compose
from feline_common_space_context import is_jacket


def main():
    tick=time.monotonic();pf=OUT/'n01-curvature-source-portals.json';parent=json.loads(pf.read_text())
    rf=ROOT/parent['rows'];assert sha(rf)==parent['rows_sha256'];portals=json.loads(gzip.decompress(rf.read_bytes()))
    _,parts,meta,pins,_=compose()
    sources={n:s for n,s in parts.items() if is_jacket(n,meta[n]) and s.Solids}
    boxes={n:s.BoundBox for n,s in sources.items()};valid=set();rows={}
    for end_id,row in portals.items():
        p=A.Vector(*row['source']['point_mm']);d=A.Vector(*row['source']['outward_axis']);matches=[]
        for name,s in sources.items():
            b=boxes[name]
            if not (b.XMin-1e-5<=p.x<=b.XMax+1e-5 and b.YMin-1e-5<=p.y<=b.YMax+1e-5 and b.ZMin-1e-5<=p.z<=b.ZMax+1e-5):continue
            if name not in valid:assert s.isValid(),name;valid.add(name)
            for face in s.Faces:
                if not isinstance(face.Surface,Part.Plane) or len(face.Edges)!=1:continue
                c=face.Edges[0].Curve
                if not isinstance(c,Part.Circle) or (c.Center-p).Length>1e-4:continue
                radius=float(c.Radius)
                if abs(face.Area-math.pi*radius**2)>1e-5:continue
                u,U,v,V=face.ParameterRange;n=face.normalAt((u+U)/2,(v+V)/2)
                if not s.isInside(p-n*.05,1e-7,False):n=-n
                if n.dot(d)<1-1e-6:continue
                assert s.isInside(p-d*.05,1e-7,False),'Do not use a reversed inlet cap'
                matches.append(dict(owner=name,actual_project_cap_radius_mm=radius,
                    outward_axis=list(n),closed_shape_verified=True,supplier_OD_guaranteed=False))
        rr=[m['actual_project_cap_radius_mm'] for m in matches]
        consistent=bool(rr) and max(rr)-min(rr)<1e-5
        rows[end_id]=dict(status='ACTUAL_EXISTING_PROJECT_JACKET_CAP_RECEIVED' if consistent else 'SOURCE_PROFILE_UNRESOLVED_KEEP_CONSERVATIVE_BUDGET',
            cap_matches=matches,previous_enclosing_budget_mm=row['radius_mm'],
            actual_project_radius_mm=max(rr) if consistent else None,
            budget_encloses_actual=bool(consistent and max(rr)<=row['radius_mm']+1e-6))
    assert len(rows)==216
    result=dict(status='ALL216_SOURCE_PROFILE_DATUMS_RECEIVED_UNMATCHED_OPEN',rows=rows,
        actual_caps_received=sum(r['actual_project_radius_mm'] is not None for r in rows.values()),
        changed_geometry=False,supplier_dimensions_not_invented=True,N01_complete=False,physical_pass=False,
        source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (pf,rf,Path(__file__))}},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-current-source-cap-profiles.json',result)
    print(json.dumps(dict(status=result['status'],actual_caps=result['actual_caps_received'],unmatched=216-result['actual_caps_received'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
