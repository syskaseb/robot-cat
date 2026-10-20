"""Twenty-seven planning-capacity outlets, no new physical cable ends."""
import json,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_rooted_rrp_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates
from compose_feline_output_boundaries import cap_at
from feline_cuff_composed_context import received
from receive_feline_rrp_shared_height import load
from feline_atomic_save import save_json


def current():
    base,rows,files=parent();f=OUT/'n01-fixed-cuff-boundary-overlay.json';r=json.loads(f.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return base,apply_updates(rows,r['updates']),(*files,f)


def main():
    tick=time.monotonic();_,rows,files=parent();f,r=received();actors=load(r);updates={}
    for link in r['links']:
        n=link['name'];e=link['target_endpoint'];q=link['body_routing_exit_mm'];d=link['body_exit_axis']
        cap_at(actors[n],q,d,1.55)
        updates[e['id']]=dict(routing_exit_mm=q,routing_exit_axis=d,prefix_geometry_owner=n,
            source_prefix_length_mm=9,routing_boundary_status='CURRENT_FIXED_CUFF_CAPACITY_OUTLET_RECEIVED',
            fixed_kinematic_seam_mm=e['point_mm'],moving_seam_and_electrical_point_unchanged=True,
            source_capacity_radius_mm=1.55,selected_project_radius_mm=link['selected_project_radius_mm'],
            capacity_encloses_selected_profile=True,capacity_cap_is_NOT_physical_wire_termination=True,
            independent_individual_termination_relief_NOT_inferred=True,
            full_middle_route_accepted=False,full_flexible_kinematics_NOT_qualified=True,
            support_owner='BundleCuff:'+e['group'].removeprefix('NineWireCuff'))
    assert len(updates)==27
    changed=apply_updates(rows,updates)
    for a,b in zip(rows,changed):
        for k in ('id','wire','portion_id','endpoint','group','point_mm','departure_axis'):assert a.get(k)==b.get(k)
    result=dict(status='ALL27_MISSING_FIXED_CUFF_CAPACITY_OUTLETS_RECEIVED_NOT_N01',updates=updates,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files,f,ROOT/r['bundle'],Path(__file__))},
        physical_portions=123,ordinary_ends=246,new_connectors_or_splices=0,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-fixed-cuff-boundary-overlay.json',result)
    print(result['status'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()
