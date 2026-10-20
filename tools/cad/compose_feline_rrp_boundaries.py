"""Four actual curved-prefix caps; electrical and moving seams stay put."""
import json,math,time
import numpy as np
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_adjudicated_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates
from compose_feline_output_boundaries import cap_at
from feline_rrp_composed_context import received
from receive_feline_rrp_shared_height import load
from feline_atomic_save import save_json


def current():
    base,rows,files=parent();f=OUT/'n01-RRP-boundary-overlay.json';r=json.loads(f.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return base,apply_updates(rows,r['updates']),(*files,f)


def main():
    tick=time.monotonic();_,rows,files=parent();f,r=received();actors=load(r);updates={}
    for name,rec in r['recipes'].items():
        e=next(e for e in rows if e['id']==rec['end_id']);radius=rec['project_radius_mm']
        cap=cap_at(actors[name],rec['routing_exit_mm'],rec['routing_exit_axis'],radius)
        q=np.array(e['point_mm']);d=np.array(e['departure_axis']);a=q+.25*d;b=np.array([0.,0,-1]);R=25.2;angle=9/R
        point=lambda t:(a+R*math.sin(t)*d+R*(1-math.cos(t))*b).tolist()
        updates[e['id']]=dict(routing_exit_mm=rec['routing_exit_mm'],routing_exit_axis=rec['routing_exit_axis'],
            prefix_geometry_owner=name,radius_from_current_source_cap_mm=cap['radius_mm'],
            routing_boundary_status='CURRENT_RRP_CURVED_FULL9_AND_SHARED_GALLERY_EXIT',
            jacket_grip9_mm=None,grip_axis=None,grip_kind='CURVED_FULL9',grip_path_length_mm=9,
            jacket_grip9_curve_parts=[dict(kind='arc',start=point(0),mid=point(angle/2),end=point(angle),radius_mm=R,length_mm=9)],
            support_owner='EarlyRR:comb:inner',support_load_path_OPEN=True,
            full_middle_route_accepted=False,supplier_datum_guaranteed=False)
    assert len(updates)==4
    result=dict(status='FOUR_RRP_ACTUAL_CAPS_RECEIVED_ROOTS_AND_N01_OPEN',updates=updates,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files,f,ROOT/r['bundle'],Path(__file__))},
        old_fixed_cap_necessity_witnesses_superseded_ONLY_for=list(updates),
        electrical_points_and_all_other242_ends_unchanged=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-RRP-boundary-overlay.json',result)
    print(result['status'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()
