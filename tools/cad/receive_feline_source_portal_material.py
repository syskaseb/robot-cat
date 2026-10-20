"""Exact CLOSED rigid-material receipt of the frozen whole portal proposal.

Positive curve/solid distance minus the enclosing circular profile is a
sufficient continuous clearance certificate. Harness/self/packing and motion
remain separate. Never promote a voxel hold to an actual part collision.
"""
import gzip,json,os,time
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_retention_composed_context import compose
from feline_common_space_context import is_jacket
from plan_feline_pi_root_access import profile_gap
from receive_feline_positive_service_deck import circle_arc
from compose_feline_integrated_boundaries import apply_updates


def curve(parts):
    edges=[]
    for p in parts:
        if p['kind']=='line':edges.append(Part.makeLine(A.Vector(*p['start']),A.Vector(*p['end'])))
        else:edges.append(circle_arc(p['start'],p['tangent'],p['bend'],p['radius'],p['angle']))
    s=Part.Wire(edges);assert s.isValid() and abs(s.Length-sum(p['length'] for p in parts))<1e-5
    return s


def bounds(s):
    b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]


def main():
    tick=time.monotonic();pf=OUT/'n01-curvature-source-portals.json';parent=json.loads(pf.read_text())
    rf=ROOT/parent['rows'];assert sha(rf)==parent['rows_sha256'];rows=json.loads(gzip.decompress(rf.read_bytes()))
    world,parts,meta,pins,docs=compose();endfile=OUT/'n01-shared-routing-boundaries.json'
    ends=json.loads(endfile.read_text())['endpoints']
    for filename in ('n01-integrated-upper-boundary-overlay.json','n01-current-retention-layout-overlay.json'):
        f=OUT/filename;ends=apply_updates(ends,json.loads(f.read_text())['updates']);pins[f.relative_to(ROOT).as_posix()]=sha(f)
    ends={e['id']:e for e in ends}
    # Soft nylon stock is not a rigid obstacle. Existing jackets/curves are
    # not discarded from the project; this receipt explicitly excludes them.
    names=[n for n,s in parts.items() if s.Solids and not is_jacket(n,meta[n]) and meta[n].get('kind') not in ('tie_reservation','project_stock_reservation')]
    boxes=np.asarray([bounds(parts[n]) for n in names]);validated={}
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (pf,rf,endfile,Path(__file__))})
    dest=OUT/'n01-source-portals-rigid-material.json';details=dest.with_suffix('.rows.json.gz')
    result=dict(status='RUNNING_WHOLE_PORTAL_RIGID_RECEIPT',source_sha256=pins,completed={},
        physical_pass=False,N01_complete=False,soft_stock_harness_self_packing_motion_access_OPEN=True)
    if dest.exists():result=json.loads(dest.read_text());assert result['source_sha256']==pins
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save()
    for end_id,row in rows.items():
        if 'candidate' not in row or end_id in result['completed']:continue
        path=curve(row['candidate']['parts']);radius=row['radius_mm'];b=np.asarray(bounds(path))
        gaps=np.linalg.norm(np.maximum(0,np.maximum(boxes[:,0]-b[1],b[0]-boxes[:,1])),axis=1)
        nearby=np.flatnonzero(gaps<radius+1.25);holds=[];queries=0
        endpoint=ends[end_id].get('endpoint');station=endpoint.split('.')[0] if endpoint else None
        for i in nearby:
            name=names[i];s=parts[name]
            # A matching grip is a designed same-kit .15mm channel, never a
            # global waiver for purchased cases, other grips or bare metal.
            own_comb=station and name=='Station:'+station+':split_common_comb'
            minimum=.15 if own_comb else 1.25
            if gaps[i]>=radius+minimum:continue
            if name not in validated:
                assert s.isValid() and all(x.isValid() for x in s.Solids),('Invalid material source',name)
                validated[name]=True
            q=path
            if name==world.bus['name']:
                q=path.copy();q.Placement=docs['inverse']*q.Placement;s=world.bus['original']
            receipt=profile_gap(s,q,radius,minimum);queries+=1
            if not receipt['ok']:holds.append(dict(owner=name,**receipt))
        result['completed'][end_id]=dict(status='EXACT_RIGID_SOURCE_PORTAL_CLEAR' if not holds else 'EXACT_RIGID_SOURCE_PORTAL_HOLDS',
            holds=holds,queries=queries,actual_project_radius_mm=radius,matching_own_comb_channel_mm=.15,
            foreign_rigid_minimum_mm=1.25,curve_length_mm=path.Length)
        save();print(end_id,'holds',len(holds),'queries',queries,flush=True)
        if time.monotonic()-tick>225:
            result['status']='PARTIAL_WHOLE_PORTAL_RIGID_RECEIPT_RESUME_SAME_INPUTS';save();return
    target=sum('candidate' in r for r in rows.values());assert len(result['completed'])==target
    summary={s:sum(r['status']==s for r in result['completed'].values()) for s in sorted({r['status'] for r in result['completed'].values()})}
    # Keep detailed witnesses compressed once complete, not thousands of
    # human-facing JSON lines or another full assembly copy.
    details.write_bytes(gzip.compress(json.dumps(result['completed'],separators=(',',':')).encode(),mtime=0))
    result.update(status='WHOLE208_SOURCE_PORTAL_RIGID_RECEIPT_COMPLETE',summary=summary,
        details=details.relative_to(ROOT).as_posix(),details_sha256=sha(details),all_endpoint_holds_collected_not_first_failure_only=True)
    save();print(json.dumps(dict(status=result['status'],summary=summary,seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
