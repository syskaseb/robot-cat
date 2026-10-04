"""One prototype selection after native and changed terminal actions finish.

Preserve R53/BUS/bank. Supersede the R20 XA05 geometry and three vague
tie roles with two real native insulation grips and one replacement tie.
Full W5/K3/E3 remain open; 5m black wire is NOT a completed cut census.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,copy,json,shutil,math
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r54'


def main():
    start=datetime.now(timezone.utc);pins={}
    def read(rel):
        q=ROOT/rel;pins[rel]=sha(q);return json.loads(q.read_text(encoding='utf-8'))
    parent='hardware/manufacturing/one-batch-prototype-r53'
    selection=read(parent+'/selection.json');quantity=read(parent+'/one-order-quantities.json')
    catalog=read(parent+'/nonfastener-catalog.json');cart=read(parent+'/fixed-fastener-cart.json')
    body=read(parent+'/body-route-status.json')
    native_rel='hardware/electronics/full-cat/w5-xa05-native-r2/checks.json'
    access_rel='hardware/electronics/full-cat/w5-xa05-access-r1/checks.json'
    native=read(native_rel);access=read(access_rel)
    interface_rel='hardware/electronics/full-cat/w5-xa05-access-r1/interface.json';interface=read(interface_rel)
    assert native['status']=='XA05_NATIVE_STATIC_COMPLETE_UNSELECTED'
    assert access['status']=='XA05_NOMINAL_BARE_DECK_SEQUENCE_CLEAR'
    assert native['closed_STLs'] and native['relocated_reopen']
    for receipt in (native,access):
        assert not receipt['hits'] and not receipt['errors']
        for k,v in {**receipt['source_sha256'],**receipt['files']}.items():
            assert sha(ROOT/k)==v,k;pins[k]=v
    assert interface['historical_XA05_ties_superseded']==3 and interface['new_XA05_installed_ties']==2
    assert interface['nominal_trial_blank_mm']==310 and interface['actual_cut_mm'] is None
    assert selection['local_fuse_bank_complete'] and selection['BUS_local_complete'] and not selection['W5_complete']
    assert not (OUT/'selection.json').exists();OUT.mkdir(parents=True,exist_ok=True)
    cad='hardware/cad/studies/w5-xa05-native-r2'
    nativefile=cad+'/XA05JointSupports.FCStd'
    dests=[]
    for name in ('Deck','Outrigger'):
        target=OUT/'prints'/(name+'_SELECTED_x1.stl');target.parent.mkdir(exist_ok=True)
        shutil.copy2(ROOT/(cad+'/'+name+'_UNSELECTED_x1.stl'),target);dests.append(target)
    deck=next(p for p in selection['prints'] if p['identity']=='electronics:DeckP10-cover-mount')
    assert deck['quantity']==1
    deck.update(stl=dests[0].relative_to(ROOT).as_posix(),sha256=sha(dests[0]),
        native=nativefile,native_file=nativefile,native_final='XA05DeckFinished',recipe=interface_rel,
        dimensions_mm=native['dimensions_mm']['Deck'],total_brim_allowance_mm=6,
        supports='Phase2 slicer/print inspection; inherited and new XA05 supports are nominal, not physical PASS.')
    selection['prints'].append(dict(identity='electronics:XA05 insulation outrigger',module='fixed power return',
        stl=dests[1].relative_to(ROOT).as_posix(),sha256=sha(dests[1]),quantity=1,purpose='installed_candidate',
        material='PETG',status='selected_nominal_prototype',native=nativefile,native_file=nativefile,
        native_final='OutriggerFinished',recipe=interface_rel,dimensions_mm=native['dimensions_mm']['Outrigger'],
        total_brim_allowance_mm=6,orientation='Export bedZ0; assess bridge/rail supports in phase2 slicer.',
        supports='Two continuous1.7mm rail cheeks; physical stiffness and strap/screw fit require phase2.'))
    # The same three exact supplier rows, not generic/invented hardware.
    additions=[]
    for sku,extra in [('SKL000623',2),('SKL000383',2),('SKL001158',4)]:
        row=next(r for r in cart['rows'] if r['supplier_sku']==sku)
        before=copy.deepcopy(row)
        roleid='fastener:XA05-outrigger:'+sku
        role=copy.deepcopy(row['roles'][0]);role.update(id=roleid,planning_quantity=extra,
            source=interface_rel,note='Additional installed XA05 outrigger hardware; no existing screw repurposed.')
        if 'product_binding' in role:role['product_binding'].update(quantity_id=roleid,planning_quantity=extra)
        row['roles'].append(role);row['quantity_ids'].append(roleid)
        row['planning_quantity']+=extra
        multiple=row['retail_multiple_pieces'];minimum=row['retail_minimum_pieces']
        row['retail_order_quantity']=max(minimum,math.ceil(row['planning_quantity']/multiple)*multiple)
        row['pack_excess_quantity']=row['retail_order_quantity']-row['planning_quantity']
        qr=next(r for r in quantity['lines'] if r['id']==row['id'])
        assert qr['planning_quantity']==before['planning_quantity'];qr.update(copy.deepcopy(row))
        additions.append(dict(role=roleid,supplier=row['supplier'],supplier_sku=sku,added_installed=extra,
            before=before['planning_quantity'],after=row['planning_quantity']))
    ties=next(r for r in quantity['lines'] if r['id']=='tie:111-02370')
    assert ties['planning_quantity']==300 and ties['conservative_stock_upper_bound']==212
    ties.update(XA05_superseded_historical_roles=3,XA05_current_installed=2,XA05_replacement_from_same_allocation=1,
        XA05_recipe=interface_rel)
    ties['note']+=' R54 replaces3 historical XA05 roles with2 real insulation straps+1 replacement; unchanged conservative ceiling212, not a completedK3census.'
    black=next(r for r in quantity['lines'] if r['id']=='wire:HELU23501:black')
    assert black['planning_quantity']==5
    black.update(XA05_nominal_trial_blank_mm=310,XA05_actual_cut_mm=None,XA05_recipe=interface_rel,
        complete_wire_census_verified=False)
    # Inherited AUX interface becomes one current overlay, not two routes.
    aux=read('hardware/manufacturing/one-batch-prototype-r20/fixed-aux-interface.json')
    aux['routes']['XA05'].update(nominal_centerline_mm=interface['centreline_mm'],
        conservative_working_blank_m=.310,route_recipe=interface_rel,
        geometry='hardware/electronics/full-cat/w5-xa05-outer-support-r5/XA05_WORLD.brep')
    aux['XA05_precedence']=dict(supersedes='R20 XA05 path/end/midspan ties only',current_interface=interface_rel,
        native_proof=native_rel,terminal_access_proof=access_rel)
    aux['restraints']['XA05_middle']='SUPERSEDED: two native fixed insulation supports per current_interface; no phantom G1 interlink.'
    aux['restraints']['XA05_ends']='SUPERSEDED: the two real insulation supports retain each side of this continuous lead; no extra unmodelled interlinked end ties.'
    aux['restraints']['WAGO_ends']=aux['restraints']['WAGO_ends'].replace('XA05 two ends; ','')
    aux['additional_ties']=13
    aux['phase1_complete']=False;aux['physical_pass']=False
    aux_rel=(OUT/'fixed-aux-interface.json').relative_to(ROOT).as_posix()
    save(OUT/'fixed-aux-interface.json',aux)
    count=len(selection['prints']);installed=sum(p['quantity'] for p in selection['prints'] if p['purpose']=='installed_candidate')
    assert count==78 and installed==116 and len(quantity['lines'])==114
    selection.update(parent_selection=parent+'/selection.json',parent_selection_sha256=pins[parent+'/selection.json'],
        phase1_percent=75,phase1_complete=False,W5_complete=False,XA05_local_complete=True,
        XA05_recipe=interface_rel,XA05_native_proof=native_rel,XA05_access_proof=access_rel,
        fixed_aux_interface=aux_rel,current_deck_world=cad+'/Deck_WORLD.brep',
        installed_petg_parts=installed,unique_stl_jobs=count,
        local_precedence='R54 supersedes R53 Deck and only R20 XA05 route/3tie roles; adds one outrigger, preserves BUS/bank/P0/E6/all other wiring. W5/K3/E3 remain open.',
        fixed_fastener_cart=(OUT/'fixed-fastener-cart.json').relative_to(ROOT).as_posix(),
        nonfastener_catalog=(OUT/'nonfastener-catalog.json').relative_to(ROOT).as_posix(),source_sha256=pins)
    quantity.update(selected_prints=(OUT/'selection.json').relative_to(ROOT).as_posix(),fixed_fastener_cart=selection['fixed_fastener_cart'],
        nonfastener_catalog=selection['nonfastener_catalog'],XA05_recipe=interface_rel,W5_complete=False,phase1_complete=False,source_sha256=pins)
    catalog.update(current_quantities=(OUT/'one-order-quantities.json').relative_to(ROOT).as_posix(),source_sha256=pins)
    cart.update(source_sha256=pins,source_roles=sum(len(r['roles']) for r in cart['rows']),phase1_percent=75)
    body.update(selected_parent='one-batch-prototype-r54',W5_complete=False,physical_pass=False)
    assert body['current_body_route_rows_prepared']==36 and len(body['route_rows_pending'])==44
    selection['W5_body_status']=(OUT/'body-route-status.json').relative_to(ROOT).as_posix()
    for p in selection['prints']:assert sha(ROOT/p['stl'])==p['sha256']
    for r in quantity['lines']:
        if r.get('roles'):assert r['planning_quantity']==sum(t['planning_quantity'] for t in r['roles']),r['id']
    for name,obj in [('selection.json',selection),('one-order-quantities.json',quantity),('fixed-fastener-cart.json',cart),
        ('nonfastener-catalog.json',catalog),('body-route-status.json',body)]:save(OUT/name,obj)
    paths=[*OUT.glob('*.json'),*dests,Path(__file__)]
    finish=datetime.now(timezone.utc)
    save(OUT/'XA05-reconciliation.json',dict(status='ONE_R54_XA05_SELECTED_WHOLE_W5_OPEN',
        phase1_completed_count=15,phase1_total=20,physical_pass=False,W5_complete=False,
        jobs=count,PETG_installed=installed,supplier_rows=114,fastener_additions=additions,
        XA05_stock_blank_mm=310,stock_full_census_complete=False,conservative_tie_stock_ceiling=212,
        source_sha256=pins,files={q.relative_to(ROOT).as_posix():sha(q) for q in paths},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('ONE_R54_XA05_SELECTED_15_OF_20',flush=True)


if __name__=='__main__':main()
