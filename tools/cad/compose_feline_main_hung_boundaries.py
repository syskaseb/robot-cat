"""Four actual current MAIN caps, separate pad/jacket/grip/route datums."""
import json,math,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_cuff_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates
from compose_feline_output_boundaries import cap_at
from feline_main_hung_context import received
from feline_physical_wire_profiles import load as profiles
from receive_feline_rrp_shared_height import load
from feline_atomic_save import save_json


def current():
    base,rows,files=parent();f=OUT/'n01-MAIN-hung-boundary-overlay.json';r=json.loads(f.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return base,apply_updates(rows,r['updates']),(*files,f)


def main():
    tick=time.monotonic();_,rows,files=parent();f,r=received();actors=load(r);contract,pf,df=profiles();updates={}
    for e,p in r['recipes'].items():
        old=next(row for row in rows if row['id']==e);n='MainSupported:'+e+':jacket';radius=contract['portions'][old['portion_id']]['project_radius_mm']
        cap_at(actors[n],p['routing_exit_mm'],p['routing_exit_axis'],radius)
        q=p['routing_exit_mm'];d=p['routing_exit_axis'];grip=[[q[i]-9*d[i] for i in range(3)],q]
        updates[e]=dict(point_mm=p['jacket_start_mm'],actual_source_pad_mm=p['source_pad_mm'],
            routing_exit_mm=q,routing_exit_axis=d,jacket_grip9_mm=grip,grip_axis=d,grip_length_mm=9,
            prefix_geometry_owner=n,routing_boundary_status='CURRENT_MAIN_HUNG_ACTUAL_NOMINAL_CAP_LOCAL_RECEIVED_WORLD_OPEN',
            nominal_project_jacket_radius_mm=radius,legacy_spatial_capacity_radius_mm=contract['portions'][old['portion_id']]['legacy_capacity_radius_mm'],
            physical_PAD_JACKET_GRIP_ROUTE_datums_separate=True,selected_SKU_unchanged=True,
            root_owner='SharedPi:Carrier',source_full_individual_grip_after_RNF_mm=9,
            source_RNF_raw_blank_mm=16,formed_bare_neck_mm=p['bare_neck_mm'],
            actual_strand_solder_insulation_pull_fit_after_delivery_gate=True,full_middle_route_accepted=False,
            world_and_tools_assembly_NOT_received=True,supplier_datum_guaranteed=False)
    assert len(updates)==4
    output=dict(status='CURRENT_FOUR_MAIN_NOMINAL_CAPS_RECEIVED_NOT_WHOLE_N01',updates=updates,
        physical_portions=123,ends=246,selected_SKUs_and_electrical_roles_unchanged=True,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files,f,ROOT/r['bundle'],pf,df,Path(__file__),ROOT/'tools/cad/feline_physical_wire_profiles.py',ROOT/'tools/cad/plan_current_main_neck_insulation.py')},worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-MAIN-hung-boundary-overlay.json',output);print(output['status'],output['worker_seconds'],flush=True)


if __name__=='__main__':main()
