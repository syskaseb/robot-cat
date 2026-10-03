"""Merge latest eight main feeds ONCE; candidate stock, not selected quantities.

One FL source is direct factory wire, seven feeds have HELU extensions. Do not
sum obsolete route generations or claim the remaining robot's red-wire census.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    paths={k:ROOT/'hardware/electronics/full-cat'/folder/'checks.json' for k,folder in (
        ('baseline','servo-fuse-front-source-ports-r2'),
        ('FRoutput','servo-fuse-output-returns-complete-r3'),
        ('rearoutput','servo-fuse-output-returns-complete-r8'),
        ('RLsource','servo-fuse-rl-source-complete-r2'),
        ('RRsource','servo-fuse-rr-source-complete-r8'))}
    stock=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json'
    data={k:json.loads(p.read_text(encoding='utf-8')) for k,p in paths.items()}
    for k,j in data.items():assert not j['errors'] and not j['factory_failures'],k
    catalogue={r['id']:r for r in json.loads(stock.read_text(encoding='utf-8'))['lines']}
    roles={r['id']:(r,'baseline') for r in data['baseline']['routes']}
    for k in ('FRoutput','rearoutput','RLsource','RRsource'):
        for r in data[k]['routes']:roles[r['id']]=(r,k)
    extension_ids=('W026_extension','W037_extension','W042_extension','W044_extension','W045_extension','W052_extension','W053_extension')
    factory_ids=('W026_factory','W037_factory','W041_factory_direct','W042_factory','W044_factory','W045_factory','W052_factory','W053_factory')
    assert set(roles)==set(extension_ids+factory_ids),(set(roles),set(extension_ids+factory_ids))
    extensions=[];factories=[]
    for ident in extension_ids:
        row,k=roles[ident];assert row['kind']=='HELU23802'
        extensions.append(dict(id=ident,nominal_blank_mm=row['stock_blank_mm'],actual_cut_mm=None,
            source=paths[k].relative_to(ROOT).as_posix(),replaces_prior_same_role=True))
    for ident in factory_ids:
        row,k=roles[ident];assert row['kind']=='MTA_factory'
        need=row.get('minimum_blank_mm',row.get('minimum_blank_with_allowance_mm'))
        assert need<=100
        factories.append(dict(id=ident,nominal_need_with_strip_and_reserve_mm=need,
            usable_factory_PROJECT_mm=100,manufacturer_usable_length_verified=False,margin_to_assumption_mm=100-need,
            actual_cut_mm=None,source=paths[k].relative_to(ROOT).as_posix()))
    total=sum(r['nominal_blank_mm'] for r in extensions);assert total==1190,total
    # Four OUTPUT cages, three SOURCE lap joints and one direct FL source.
    installed_splices=[dict(role=r,installed=1,manufacturer_part='221-412') for r in ('XB11','W026_output','W037_output','W045_output','W053_output')]
    red=catalogue['p0:WIRE-RED4-P0'];splice=catalogue['splice:WAGO221-412'];assert red['planning_quantity']==2 and splice['installed']==1
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-main-feeds-materials-r1';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'materials.json').exists()
    save(out/'materials.json',dict(status='EIGHT_MAIN_FEED_MATERIAL_ROLES_MERGED_OTHER_ROBOT_STOCK_OPEN',
        selected=False,physical_pass=False,W5_complete=False,K3_complete=False,E3_complete=False,
        recorded_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in list(paths.values())+[stock]},script_sha256=sha(Path(__file__)),
        HELU23802=dict(extensions=extensions,unique_extension_count=7,nominal_blank_mm=total,
            retained_W066_nominal_blank_mm=330,partial_reserved_total_mm=1520,
            selected_R51_stock_mm=2000,unallocated_after_partial_reservations_mm=480,
            unresolved_remaining_roles=['W064','W065','W067','W068'],whole_robot_stock_complete=False,
            rule='1190mm replaces ALL older seven extension lists, not an additive1190mm purchase.330mmW066 remains one separate role.480mm is leftover capacity, NOT proof it covers the four unresolved source roles.'),
        factory=factories,splice221412=dict(installed_roles=installed_splices,installed_total=5,
            retained_R51_spares=1,candidate_planning_quantity=6,selected_R51_planning_quantity=2,
            supplier_SKU=splice['supplier_sku'],supplier_url=splice['url'],retail_multiple_unverified=True,
            role_replacements='Retain XB11 once; add four output joints once. Source laps do not add221412.'),
        source_laps=dict(roles=['W042_source','W044_source','W052_source'],count=3,
            source_FL='W041 factory direct, no added HELU, solder lap, sleeve or221412.',
            retained_RNF100_pieces_per_lap=1,nominal_blank_mm_each=26,
            qualification='Existing source construction pins the sleeves and separate insulation seats. Delivery, solder/wall fit and pull/heat remain phase2.'),
        grips='FR three ties accepted; RL/RR six ties and native seats still under construction. Do not add proposed ties to installed census before receiving result.',
        open=['Whole red-wire/source stock and all-bank installed/spare strap census.','Native rear seats, lever/assembly/removal, selected one export and E3.'],
        no_selected_quantity_mutation=True))
    print(json.dumps(dict(factory_feeds=8,HELU_extensions=7,HELU_nominal_mm=total,WAGO_installed=5,candidate_with_one_spare=6,selected=False)))
if __name__=='__main__':main()
