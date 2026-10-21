"""One corrected shared resource for W009/W069; no source-pose search.

Reuse the existing whole field and accepted cap links. Add the three later
accepted middle jackets. Preserve old artifacts and never call this N01.
"""
import copy,json,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import save_npz
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_current_joint_tangent_space import available_room
from plan_feline_tangent_corridor_network import transitions
from compose_feline_current_body_routes import current
import feline_tangent_routes as ft


def add_jacket(room,origin,recipe):
    """Nearest sampled centreline minus half sample step is a lower bound."""
    points=np.array([p for part in recipe['parts'] for p in ft.samples(part,.5)])
    radius=recipe['radius_mm'];tree=cKDTree(points)
    # Only this band can reduce a1.55mm resource. Outside it no mask changes.
    reach=radius+.25+1.4+1.55+1
    low=np.maximum(0,np.floor(points.min(0)-reach-origin).astype(int))
    high=np.minimum(np.array(room.shape)-1,np.ceil(points.max(0)+reach-origin).astype(int))
    for x in range(low[0],high[0]+1):
        yy,zz=np.meshgrid(np.arange(low[1],high[1]+1),np.arange(low[2],high[2]+1),indexing='ij')
        xyz=np.column_stack((np.full(yy.size,x),yy.ravel(),zz.ravel()))
        clearance=tree.query(xyz+origin)[0]-radius-.25-1.4
        old=room[x,low[1]:high[1]+1,low[2]:high[2]+1]
        np.minimum(old,clearance.reshape(old.shape),out=old)


def run():
    tick=time.monotonic();source=OUT/'joint-corridor-space-20261021'
    dest=OUT/'W009-W069-harness-corridor'
    assert not dest.exists(),'Receive existing result, do not repeat'
    sf=source/'n01-integrated-signed-space.json';space=json.loads(sf.read_text())
    fp=ROOT/space['field'];assert sha(fp)==space['field_sha256']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (sf,fp,Path(__file__),ROOT/'tools/cad/plan_feline_current_joint_tangent_space.py')}
    with np.load(fp,allow_pickle=False) as field:
        assert float(field['grid_mm'])==1
        origin=field['origin_mm'].copy();inside=field['inside'].copy();room=available_room(field)
    for filename in ('n01-current-W020-complete-body-plan.json','n01-current-W022-complete-body-plan.json','n01-current-W024-shared-complete-body-plan.json'):
        path=OUT/filename;r=json.loads(path.read_text())
        assert sha(ROOT/r['bundle'])==r['bundle_sha256']
        add_jacket(room,origin,r['middle_recipe'])
        pins[path.relative_to(ROOT).as_posix()]=sha(path);pins[r['bundle']]=r['bundle_sha256']
    ids,graph=transitions(inside&(room>=1.55),16)
    dest.mkdir();gf=dest/'shared.graph.npz';nf=dest/'shared.nodes.npz'
    save_npz(gf,graph);np.savez_compressed(nf,ids=ids,origin_mm=origin,step_mm=4)
    network=dict(classes={'1.55-R16':dict(graph=gf.relative_to(ROOT).as_posix(),graph_sha256=sha(gf),nodes=nf.relative_to(ROOT).as_posix(),nodes_sha256=sha(nf),bend_mm=16)})
    oldnet=json.loads((source/'current-tangent-resources.json').read_text())
    with np.load(ROOT/oldnet['classes']['1.55-R16']['nodes'],allow_pickle=False) as old:
        oldcells=np.argwhere(old['ids']>=0)
    full=json.loads((source/'current-full-source-links-exact.json').read_text())
    aliases=json.loads((source/'current-named-station-source-links-exact.json').read_text())
    domains=json.loads((source/'current-local-exact-link-proposals.json').read_text())
    _,rows,_=current();rows=[e for e in rows if e['portion_id'] in ('W009/body','W069/body')]
    links=copy.deepcopy({**full['ends'],**aliases['ends']});rejected=[]
    for row in rows:
        eid=row['id'];keep=[]
        for candidate in links[eid]['candidates']:
            rec=candidate['recipe'];cell=oldcells[rec['node']//6];new=int(ids[tuple(cell)])
            if new<0:rejected.append(eid);continue
            rec['node']=new*6+rec['heading'];keep.append(candidate)
        links[eid]['candidates']=keep
    summary=dict(status='HARNESS_AWARE_RESOURCE_CAP_LINKS_OPEN',states=graph.shape[0],primitives=graph.nnz,
        rejected_old_link_nodes=rejected,source_sha256=pins,network=network,
        includes_later_accepted_middles=['W020','W022','W024'],
        current_field_geometry_reconstruction_incomplete=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest/'resource.json',summary)
    import plan_feline_received_link_pairs as solver
    original=solver.save_json
    try:
        solver.save_json=lambda unused,result:save_json(dest/'pair-preflight.json',result)
        result=solver.run(domains,dict(ends=links),dict(ends={}),rows,network,pins)
    finally:solver.save_json=original
    print('PAIR_CORRIDOR',summary['states'],summary['primitives'],rejected,
          {k:v['status'] for k,v in result['paths'].items()},time.monotonic()-tick,flush=True)
    return summary,result
