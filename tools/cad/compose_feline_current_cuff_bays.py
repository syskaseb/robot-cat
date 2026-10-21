"""One current36-source register, not four incompatible remembered proposals."""
import json,math,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_rooted_space_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates
from feline_atomic_save import save_json

DEST=OUT/'n01-four-cuff-current-space-boundaries.json'
RECEIPTS={'FR':'n01-FR-vertical9-rooted-space','FL':'n01-FL9-common-arc-rooted-space',
          'RL':'n01-RL9-common-arc-rooted-space','RR':'n01-RR9-flat-common-bank-bridge'}


def compose():
    tick=time.monotonic();_,rows,_=parent();index={r['id']:r for r in rows};updates={};pins={};selected={}
    for leg,stem in RECEIPTS.items():
        path=OUT/(stem+'.json');p=json.loads(path.read_text())
        assert not p['N01_complete'] and not p['physical_pass']
        assert all(r['ok'] for r in p['checks'].values()) and all(r['ok'] for r in p['outer'].values())
        assert p['sampled36_leg_vertical_separation_lower_bound_mm']>=1.25
        archive=ROOT/p['bundle'];assert sha(archive)==p['bundle_sha256']
        for name,h in p['source_sha256'].items():assert sha(ROOT/name)==h,name
        recipes=p['source_recipes'] if leg=='FR' else p['plan']['recipes'];assert len(recipes)==9
        pins[path.relative_to(ROOT).as_posix()]=sha(path);pins[p['bundle']]=sha(archive)
        selected[leg]=dict(receipt=path.relative_to(ROOT).as_posix(),bundle=p['bundle'])
        for owner,r in recipes.items():
            eid=r['end_id'];old=index[eid];assert old['group']=='NineWireCuff'+leg
            point=r['new_seam_mm'] if leg in ('FR','FL') else r['original_source_mm'] if leg=='RL' else r['proposed_seam_mm']
            axis=r['new_axis'] if leg in ('FR','FL') else r['original_source_axis'] if leg=='RL' else r['departure_axis']
            parts=r['parts']+(r['resource_parts'] if leg=='RR' else [])
            end=r['resource_end_mm'] if leg=='RR' else r['exit_mm'];tangent=r['resource_end_axis'] if leg=='RR' else r['exit_axis']
            assert all(math.isfinite(v) for v in (*point,*axis,*end,*tangent))
            updates[eid]=dict(point_mm=point,departure_axis=axis,fixed_kinematic_seam_mm=point,
                routing_exit_mm=end,routing_exit_axis=tangent,prefix_geometry_owner=owner,
                planned_body_capacity_path_owners=[owner]+([r['resource']] if leg=='RR' else []),
                source_prefix_length_mm=sum(e['length_mm'] for e in parts),full_grip_arclength_mm=[0,9],
                source_prefix_length_basis='Received centreline capacity, not a finished stock cut or900mm motion qualification',
                current_restraint_receipt=path.relative_to(ROOT).as_posix(),
                independent_grip_root_and_sampled_leg_motion_received=True,
                full_middle_route_accepted=False,full_flexible_kinematics_NOT_qualified=True,
                moving_side_interface_CHANGED=point!=old['point_mm'])
    resolved=apply_updates(rows,updates)
    assert len(updates)==36 and len(resolved)==246 and len({r['portion_id'] for r in resolved})==123
    assert [r['id'] for r in resolved]==[r['id'] for r in rows]
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    pins['tools/cad/compose_feline_rooted_space_boundaries.py']=sha(ROOT/'tools/cad/compose_feline_rooted_space_boundaries.py')
    pins[(OUT/'n01-rooted-current-boundary-overlay.json').relative_to(ROOT).as_posix()]=sha(OUT/'n01-rooted-current-boundary-overlay.json')
    return dict(status='CURRENT36_CUFF_SOURCE_BAYS_AND_CAPACITY_BOUNDARIES_RECEIVED_WHOLE123_OPEN',
        updates=updates,selected_planning_receipts=selected,source_sha256=pins,
        endpoint_count=246,physical_portions=123,changed_kinematic_seams=sum(v['moving_side_interface_CHANGED'] for v in updates.values()),
        native_master_changed=False,selected_SKUs_changed=False,N01_complete=False,physical_pass=False,
        target_forks_remaining=True,whole_moving900_N02_N05_NOT_received=True,worker_seconds=round(time.monotonic()-tick,3))


def current():
    base,rows,files=parent();p=json.loads(DEST.read_text())
    for name,h in p['source_sha256'].items():assert sha(ROOT/name)==h,name
    return base,apply_updates(rows,p['updates']),(*files,DEST)


if __name__=='__main__':
    assert not DEST.exists(),'Receive current selected overlay instead of regenerating'
    p=compose();save_json(DEST,p);print(p['status'],len(p['updates']),p['worker_seconds'])
