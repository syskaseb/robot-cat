"""Whole guide demand diagnostic, never a corridor-allocation acceptance gate.

Independent connectivity can conceal coincident wires and unfilletable turns.
Report the whole hypothesis before choosing shared trunks. No physical routes
or stock are created; a failed guide is not proof that the assembly cannot fit.
"""
import collections,json,math,time
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from compose_feline_integrated_boundaries import apply_updates


def square_shelf(radii,clearance=.2):
    assert radii and min(radii)>0
    pitch=2*max(radii)+clearance
    cols=math.ceil(math.sqrt(len(radii)));rows=math.ceil(len(radii)/cols)
    # Centres explicitly on a rectangular grid. The enclosing disk is a
    # sufficient packing construction, not a claimed optimal area density.
    width=(cols-1)*pitch+2*max(radii);height=(rows-1)*pitch+2*max(radii)
    return dict(width_mm=width,height_mm=height,enclosing_radius_mm=math.hypot(width,height)/2,
        columns=cols,rows=rows,pitch_mm=pitch,wire_count=len(radii))


def main():
    tick=time.monotonic();gf=OUT/'n01-integrated-sparse-corridor-guides.json';guides=json.loads(gf.read_text())
    assert guides['status']=='ALL123_PLUS_USB_SPARSE_GUIDES_RECORDED_NOT_N01'
    sf=OUT/'n01-integrated-signed-space.json';space=json.loads(sf.read_text());fp=ROOT/space['field'];assert sha(fp)==space['field_sha256']
    ef=OUT/'n01-shared-routing-boundaries.json';of=OUT/'n01-integrated-upper-boundary-overlay.json'
    reg=json.loads(ef.read_text());overlay=json.loads(of.read_text());assert overlay['parent_sha256']==sha(ef)
    ends={e['id']:e for e in apply_updates(reg['endpoints'],overlay['updates'])}
    with np.load(fp,allow_pickle=False) as f:
        origin=f['origin_mm'];clearance=np.minimum(f['rigid_signed_distance'],f['motion36_signed_distance'])-2.45
        clearance=np.minimum(clearance,f['outer_distance']-4.45)
    edges=collections.defaultdict(set);radii={};turns={};links=[];external=[]
    for name,row in guides['portions'].items():
        if not row.get('guide',{}).get('points_mm'):
            if row['status']=='EXTERNAL_INTERFACE_ROUTE_STILL_OPEN':external.append(name)
            continue
        radii[name]=row['prototype_radius_mm'];points=np.asarray(row['guide']['points_mm'],float)
        required=max([ends[e].get('minimum_R_mm',12.4) or 12.4 for e in row['end_ids']])
        lengths=np.linalg.norm(np.diff(points,axis=0),axis=1);bad=[]
        for i,length in enumerate(lengths):
            # A right-angle fillet consumes R on each adjacent tangent. For
            # a segment between two corners both withdrawals must fit.
            need=required*((i>0)+(i<len(lengths)-1))
            if length+1e-6<need:bad.append(dict(segment=i,length_mm=float(length),required_tangent_mm=need))
        turns[name]=dict(minimum_R_project_mm=required,segments=len(lengths),short_segments=bad,
            generic_default_not_supplier_spec=any(not ends[e].get('minimum_R_mm') for e in row['end_ids']))
        for anchor in row.get('anchors',[]):
            links.append(dict(portion=name,end=anchor['end'],unqualified_length_mm=anchor['unqualified_anchor_link_mm']))
        for a,b in zip(points,points[1:]):
            delta=b-a;assert np.count_nonzero(delta)>0 and np.count_nonzero(delta)==1
            step=np.sign(delta);count=int(round(np.abs(delta).sum()));assert np.allclose(count*step,delta)
            for i in range(count):
                aa=tuple(np.rint(a+i*step-origin).astype(int));bb=tuple(np.rint(a+(i+1)*step-origin).astype(int))
                edges[tuple(sorted((aa,bb)))].add(name)
    shared=[];seen={}
    for (a,b),owners in edges.items():
        if len(owners)<2:continue
        key=tuple(sorted(owners));available=float(min(clearance[a],clearance[b]));previous=seen.get(key)
        if previous and previous['available_radius_mm']<=available:continue
        packing=square_shelf([radii[n] for n in key]);seen[key]=dict(portions=list(key),edge_mm=[(origin+np.asarray(p)).tolist() for p in (a,b)],
            available_radius_mm=available,constructive_square_shelf=packing,
            shelf_fits_current_grid=packing['enclosing_radius_mm']<=available,
            area_necessary_radius_mm=math.sqrt(sum(radii[n]**2 for n in key)))
    shared=sorted(seen.values(),key=lambda r:r['available_radius_mm']-r['constructive_square_shelf']['enclosing_radius_mm'])
    result=dict(status='WHOLE_GUIDE_DEMAND_RECEIVED_NOT_ALLOCATED',ordinary_portions=123,separate_USB=1,
        guide_count=len(turns),unique_unit_edges=len(edges),shared_membership_bottlenecks=shared,
        right_angle_tangent_tests=turns,unqualified_source_anchor_links=links,external_interfaces=external,
        packed_elbows_source_links_existing_cables_tools_and_root_network_still_OPEN=True,
        N01_complete=False,selected=False,physical_pass=False,not_global_infeasibility=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (gf,sf,fp,ef,of,ROOT/'tools/cad/check_feline_joint_guide_capacity.py')},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-integrated-guide-demand.json',result)
    print(json.dumps(dict(status=result['status'],guide_count=len(turns),shared_bottlenecks=len(shared),
        shelf_holds=sum(not r['shelf_fits_current_grid'] for r in shared),unfilletable_guides=sum(bool(r['short_segments']) for r in turns.values()),seconds=result['worker_seconds'])))


if __name__=='__main__':main()
