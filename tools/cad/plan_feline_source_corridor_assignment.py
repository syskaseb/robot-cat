"""Receive ALL source-to-tangent-network interfaces, not nearest-node PASS."""
import json,math,time,sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from compose_feline_integrated_boundaries import apply_updates
from propose_feline_current_corridors import macro_boundary
from plan_feline_tangent_corridor_network import DIRECTIONS


def main():
    tick=time.monotonic();nf=OUT/'n01-tangent-corridor-network.json';network=json.loads(nf.read_text())
    assert network['status']=='FINITE_RADIUS_SHARED_CORRIDOR_TOPOLOGY_RECEIVED_LINKS_PACKING_OPEN'
    thin='--actual-thin-large-bend' in sys.argv
    addonfile=OUT/'n01-tangent-corridor-thin-large-bend.json'
    if thin:
        addon=json.loads(addonfile.read_text());assert addon['parent_sha256']==sha(nf)
        network['classes'][addon['added_class']]=addon['row']
    ef=OUT/'n01-shared-routing-boundaries.json';reg=json.loads(ef.read_text());of=OUT/'n01-integrated-upper-boundary-overlay.json';overlay=json.loads(of.read_text())
    assert overlay['parent_sha256']==sha(ef);ends={r['id']:r for r in apply_updates(reg['endpoints'],overlay['updates'])}
    lf=OUT/'n01-full-lower-bay-plan-r3.json';lower={r['id']:r for r in json.loads(lf.read_text())['custom_ends']}
    pf=OUT/'prefix-allocation.json';radii={}
    for r in json.loads(pf.read_text())['specifications']:radii[r['wire']]=max(r['radius'],radii.get(r['wire'],0))
    trees={};sources=[nf,ef,of,lf,pf,Path(__file__)];result={}
    if thin:sources.append(addonfile)
    for key in (('2.1-R16','2.1-R28','3.5-R28') if thin else ('2.1-R16','3.5-R28')):
        row=network['classes'][key];nodes=ROOT/row['nodes'];assert sha(nodes)==row['nodes_sha256'];sources.append(nodes)
        with np.load(nodes,allow_pickle=False) as a:ids=a['ids'];comp=a['component'];origin=a['origin_mm'];step=int(a['step_mm'])
        cells=np.argwhere(ids>=0);base=ids[tuple(cells.T)];counts=np.bincount(comp);points=origin+step*cells
        heading=[]
        for h in range(6):
            cc=comp[base*6+h];keep=counts[cc]>=100
            heading.append(dict(tree=cKDTree(points[keep]),points=points[keep],component=cc[keep]))
        trees[key]=dict(headings=heading,origin=origin,high=origin+(np.asarray(ids.shape)-1)*step)
    factory={r['portion_id'] for r in reg['received_factory4MTA_curves']}
    for name,identities in reg['portions'].items():
        ee=[ends[e] for e in identities];wire=ee[0]['wire'];radius=radii.get(wire,1.05 if wire.startswith('X') else 1.55)
        if name in factory or wire=='W043':result[name]=dict(status='UNCHANGED_COMPLETE_SOURCE_CURVE_RETAINED');continue
        bend=max(float(e.get('minimum_R_mm') or 12.4) for e in ee)
        key=('2.1-R16' if bend<=16 else '2.1-R28') if radius<=2.1 and thin else '2.1-R16' if bend<=16 and radius<=2.1 else '3.5-R28';data=trees[key]
        assert bend<=28 and radius<=network['classes'][key]['project_corridor_radius_mm'],(name,radius,bend)
        candidates=[];source=[]
        for side,e in enumerate(ee):
            q,d,status=macro_boundary(e,lower);d=d/np.linalg.norm(d)
            source.append(dict(end=e['id'],point_mm=q.tolist(),outward_axis=d.tolist(),boundary_status=status))
            if np.any(q<data['origin']) or np.any(q>data['high']):candidates.append({});continue
            desired=d if side==0 else -d;h=int(np.argmax(DIRECTIONS@desired));tree=data['headings'][h]
            dist,index=tree['tree'].query(q,k=min(64,len(tree['points'])))
            bycomp={}
            for distance,i in zip(np.atleast_1d(dist),np.atleast_1d(index)):
                c=int(tree['component'][i])
                if c not in bycomp:bycomp[c]=dict(anchor_mm=tree['points'][i].tolist(),unqualified_link_mm=float(distance),
                    corridor_heading=DIRECTIONS[h].tolist(),tangent_change_deg=math.degrees(math.acos(float(np.clip(DIRECTIONS[h]@desired,-1,1)))))
            candidates.append(bycomp)
        common=set(candidates[0])&set(candidates[1])
        row=dict(source_ends=source,corridor_class=key,source_radius_mm=radius,minimum_R_project_mm=bend,
            radius_from_provisional_fallback_not_current_specification=wire not in radii,
            all_links_are_proposals_not_actual_source_exit_clearance=True)
        if common:
            c=min(common,key=lambda c:sum(v[c]['unqualified_link_mm'] for v in candidates))
            row.update(status='COMMON_TANGENT_COMPONENT_SOURCE_LINKS_OPEN',component=c,anchors=[v[c] for v in candidates])
        else:row['status']='EXTERNAL_OR_NO_COMMON_COMPONENT_AMONG64_NEAREST_PROPOSALS_NOT_INFEASIBILITY'
        result[name]=row
    output=dict(status='ALL123_SOURCE_CORRIDOR_INTERFACES_RECEIVED_LINKS_OPEN',portions=result,
        ordinary_ends=246,separate_USB_complete_received_not_rerouted=True,
        factory_circuits_and_internal_None_contacts_preserved=True,N01_complete=False,selected=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/('n01-source-corridor-assignment-actual-thin.json' if thin else 'n01-source-corridor-assignment.json'),output)
    counts={s:sum(r['status']==s for r in result.values()) for s in sorted({r['status'] for r in result.values()})}
    print(json.dumps(dict(status=output['status'],counts=counts,seconds=output['worker_seconds'])),flush=True)


if __name__=='__main__':main()
