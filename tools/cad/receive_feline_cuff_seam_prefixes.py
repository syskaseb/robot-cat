"""Construct missing body-side planning prefixes at 27 fixed cuff seams.

These are continuous-conductor bookkeeping seams, not new connectors or
terminations. Use the already allocated MAX-OD3.1 cuff capacity. Preserve
the moving/fixed seam; the nine-mm prefix belongs to the existing body
portion and is never extra stock or an independent WAGO strain relief.
"""
import json,os,time
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_rooted_rrp_boundaries import current
from feline_selected_material_contract import load as profiles
from feline_rrp_rooted_context import compose
from receive_feline_planning_links import receive
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();base,ends,files=current();contract,pf,bf=profiles()
    af=OUT/'n01-current-prefix-atlas.json';atlas=json.loads(af.read_text())
    selected={n for n,r in atlas['rows'].items() if r['status']=='KINEMATIC_CUFF_BOUNDARY_NO_OWNED_PREFIX_SOLID'}
    assert len(selected)==27
    links=[]
    for e in ends:
        if e['id'] not in selected:continue
        assert e['group'] in ('NineWireCuffFL','NineWireCuffRL','NineWireCuffRR')
        radius=contract['portions'][e['portion_id']]['project_radius_mm']
        assert radius<=1.55+1e-6
        q=np.array(e['point_mm']);d=np.array(e['departure_axis']);assert abs(np.linalg.norm(d)-1)<1e-6
        tip=q+9*d
        links.append(dict(name='CuffPrefix:'+e['id'],wire=e['wire'],portion=e['portion_id'],
            radius_mm=1.55,selected_project_radius_mm=radius,capacity_radius_encloses_selected=True,
            parts=[dict(kind='line',start=q.tolist(),end=tip.tolist(),length_mm=9)],joins=[],target_endpoint=e,
            fixed_kinematic_seam_mm=q.tolist(),body_routing_exit_mm=tip.tolist(),body_exit_axis=d.tolist(),
            no_new_connector_or_solder_joint=True,not_extra_wire_or_stock=True,
            independent_individual_termination_relief_NOT_inferred=True,not_full_constant_length_moving_loom=True,
            geometry_is_retained_MAX_OD3p1_cuff_capacity_not_new_supplier_OD=True))
    assert len(links)==27 and len(base['portions'])==123 and len(ends)==246
    context=compose()
    for e in ends:
        if e['id'] in selected:assert 'End:'+e['id'] not in context[1],e['id']
    sources=(*files,pf,bf,af,Path(__file__),ROOT/'tools/cad/plan_feline_common_restraints.py',ROOT/'tools/cad/receive_feline_planning_links.py')
    result=receive('n01-fixed-cuff-seam-prefixes',links,context,{p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    result.update(worker_seconds=round(time.monotonic()-tick,3),fixed_seams_not_moved=True,
        all_existing_individual_WAGO_termination_grips_retained=True,N01_complete=False)
    save_json(OUT/'n01-fixed-cuff-seam-prefixes.json',result)
    print('Fixed cuff whole27',result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
