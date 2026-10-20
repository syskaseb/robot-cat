"""Reuse continuous exact distances with current profile/own-grip contracts.

No CAD queries are repeated. A growing profile loses its broad-phase proof
and is queued for changed pairs, never algebraically promoted to clearance.
"""
import collections,gzip,json,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_selected_material_contract import load as selected_profiles


def own_channel(e,owner):
    endpoint=e.get('endpoint') or ''
    station=endpoint.split('.')[0]
    if owner.startswith(e['id']+':') and owner.endswith(':saddle'):return .15
    if owner in ('Station:'+station+':split_common_comb','Station:'+station+':common_channelled_cap_exterior','Station:'+station+':split_cap_exterior'):return .15
    group=e.get('group','')
    if group.startswith('NineWireCuff') and owner=='BundleCuff:'+group.removeprefix('NineWireCuff'):return .2
    if owner.startswith('ShelfPWM:XLcomb:') and e['wire'].startswith('XL') and group=='PWM9685':return .15
    if owner.startswith('ShelfPWM:XScomb:') and e['wire'] in ('XS11','XS21','XS31') and group=='PWM9685':return .15
    return 1.25


def changed_contract(before,radius,constructed,required):
    if radius>before+1e-6:
        return dict(status='LARGER_PROFILE_CHANGED_BROADPHASE_RECHECK_REQUIRED',old_radius_mm=before,current_radius_mm=radius)
    if constructed is not None and constructed+1e-6<required:
        return dict(status='SELECTED_SKU_BEND_REQUIRES_NEW_TOPOLOGY',constructed_R_mm=constructed,selected_project_R_mm=required)
    return None


def main():
    tick=time.monotonic();profiles,pf,bf=selected_profiles()
    rf=OUT/'n01-source-portals-rigid-material.json';old=json.loads(rf.read_text())
    cf=OUT/'n01-curvature-source-portals.json';curves=json.loads(cf.read_text());raw=ROOT/curves['rows'];assert sha(raw)==curves['rows_sha256']
    recipes=json.loads(gzip.decompress(raw.read_bytes()))
    ef=OUT/'n01-shared-routing-boundaries.json';ends={e['id']:e for e in json.loads(ef.read_text())['endpoints']}
    rows={};owners=collections.Counter();reclassified=0
    for name,r in old['completed'].items():
        e=ends[name];profile=profiles['portions'][e['portion_id']];radius=profile['project_radius_mm'];before=r['actual_project_radius_mm']
        constructed=recipes[name]['candidate']['minimum_constructed_R_mm']
        change=changed_contract(before,radius,constructed,profile['minimum_project_R_mm'])
        if change:rows[name]=change;continue
        holds=[];clear=[]
        for h in r['holds']:
            gap=h['gap_lower_bound_mm']+before-radius;minimum=own_channel(e,h['owner'])
            witness=dict(h,current_profile_gap_lower_mm=gap,current_minimum_mm=minimum,
                continuous_distance_reused=True,nominal_own_channel_not_foreign_margin_change=minimum<1.25)
            (clear if gap>=minimum-1e-6 else holds).append(witness)
        reclassified+=len(clear)
        rows[name]=dict(status='EXACT_RIGID_PORTAL_CLEAR_CURRENT_CONTRACT' if not holds else 'EXACT_RIGID_PORTAL_HOLDS_CURRENT_CONTRACT',
            holds=holds,resolved_conservative_or_own_channel_holds=clear,
            unchanged_positive_queries_reused=True,current_profile_mm=radius)
        owners.update(h['owner'] for h in holds)
    rowsfile=OUT/'n01-source-portal-selected-material-delta.rows.json.gz'
    rowsfile.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    result=dict(status='SELECTED_MATERIAL_CONTRACT_DELTA_ON_FROZEN_PORTALS_NOT_NEW_WORLD_ACCEPTANCE',
        rows=rowsfile.relative_to(ROOT).as_posix(),rows_sha256=sha(rowsfile),
        summary=dict(collections.Counter(r['status'] for r in rows.values())),
        remaining_owner_holds=owners.most_common(),reclassified_conservative_or_own_channel_pairs=reclassified,
        foreign_rigid_margin_unchanged_mm=1.25,new_gap_queries=0,
        changed_output_layout_not_qualified_by_historical_portals=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (pf,bf,rf,ef,cf,raw,Path(__file__),ROOT/'tools/cad/feline_selected_material_contract.py',ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json',ROOT/'hardware/electronics/full-cat/servo-fuse-main-feeds-materials-r1/materials.json',ROOT/'tools/cad/feline_pwm_board_shelf.py',ROOT/'tools/cad/plan_feline_common_restraints.py')},
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-source-portal-selected-material-delta.json',result)
    print(json.dumps(dict(summary=result['summary'],reclassified=reclassified,top_owners=owners.most_common(8),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
