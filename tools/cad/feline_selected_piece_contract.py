"""Selected physical piece roles before generic max-cap routing envelopes.

Bind to the baseline's selected K3 SKUs; never import old blank lengths.
Project OD/bend recipes are nominal delivery gates, not supplier guarantees.
"""
import collections,copy,json,subprocess,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import BASE,OUT
from feline_physical_wire_profiles import load as parent
from feline_atomic_save import save_json

SELECTION=BASE/'phase1-material-selection-r4.json'


def compose():
    tick=time.monotonic();result,pf,df=parent();selection=json.loads(SELECTION.read_text())
    assert selection['selected'] and selection['K3_complete']
    rel=SELECTION.relative_to(ROOT).as_posix();tag='phase1-open-prototype-100-2026-10-17'
    expected=subprocess.check_output(['git','rev-parse',tag+':'+rel],cwd=ROOT,text=True).strip()
    actual=subprocess.check_output(['git','hash-object',str(SELECTION)],cwd=ROOT,text=True).strip()
    assert actual==expected,'Do not substitute an unapproved selected-material table'
    headfile=BASE/'head-supply-checkpoint/plan.json';head=json.loads(headfile.read_text())
    auxfile=BASE/'aux-wiring-checkpoint/whole-layout-plan.json';aux=json.loads(auxfile.read_text())
    commonfile=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json';common=json.loads(commonfile.read_text())['routes']
    e2file=BASE/'pwm-branch-checkpoint/selection.json';e2=json.loads(e2file.read_text())
    assert e2['selected'] and 'ModelOD1.85/R11.1' in ' '.join(e2['assumptions'])
    endpointfile=OUT/'n01-shared-routing-boundaries.json';endpoints=json.loads(endpointfile.read_text())['endpoints']
    assert 'HELUOD2.1/fixedR12.6' in head['assumptions']
    assert all(head['routes'][w]['radius']==1.05 for w in ('XB12','XB13','XS13','XB22','XB23','XS23'))
    assert all(aux['routes'][w]['radius']==1.25 for w in ('XA02','XA03','XA04','XA05','XA06','XB11'))
    bywire=collections.defaultdict(list)
    for r in selection['wire_blanks']:bywire[r['wire']].append(r)
    e2roles={'XP02.source':('red_source','XP02_source'),'XP03.source':('black_source','XP03_source'),
        'XP02.module':('red_module','XP02_module'),'XP03.module':('black_module','XP03_module')}
    changed=[];mapped=[];unknown=[];grouped_factory=[]
    for name,row in result['portions'].items():
        wire=row['wire'];choices=bywire[wire];exact=[r for r in choices if r['id']==name]
        selected=exact[0] if len(exact)==1 else choices[0] if len(choices)==1 else None
        if selected is None and choices and len({r['sku'] for r in choices})==1:
            selected=dict(choices[0],id=[r['id'] for r in choices],physical_unit=[r['physical_unit'] for r in choices])
            grouped_factory.append(name)
        if name.startswith('W076/retained'):
            ends={r['endpoint'] for r in endpoints if r['portion_id']==name}
            key='W076/factory' if 'F0.out' in ends else 'W076/custom' if 'S0.in' in ends else None
            assert key is not None;selected=next(r for r in choices if r['id']==key)
        if wire in ('XA01','XB21','XB31'):
            role={'XA01':'F_AUX.in','XB21':'F_HP.in','XB31':'F_TY.in'}[wire]
            assert any(e['wire']==wire and e['endpoint']==role for e in endpoints)
            assert selection['factory_units']['FHAC']['included_leads_not_extra_wire_purchase']
            selected=dict(id=role+'/included_factory_lead',sku='FHAC0001ZXJ included16AWG',physical_unit=role+'/one_existing_holder_tail')
            row['source_kit_mixed_factory_custom_geometry_requires_typed_receipt']=True
        if wire in e2roles:
            key,route=e2roles[wire];sku=e2['factory_leads'][key].split()[0]
            assert sku in selection['factory_units']['E2']['used225mm_leads']
            assert e2['routes'][route]['radius']==.925
            selected=dict(id=wire+'/selected_factory_core',sku='Molex'+sku,physical_unit=sku+'/one225mm_lead')
        if selected is None:
            row['selected_piece_binding_status']='FACTORY_OR_COMPOSITE_ROLE_REQUIRES_NAMED_SOURCE';unknown.append(name);continue
        sku=selected['sku'];row.update(selected_piece_id=selected['id'],selected_sku=sku,selected_material=sku,
            selected_physical_unit=selected['physical_unit'],selected_piece_binding_status='BASELINE_SELECTED_K3_UNIT_NO_OLD_CUT_LENGTH_IMPORTED')
        mapped.append(name)
        row['stock_count_is_physical_unit_group_not_each_core']=isinstance(selected['physical_unit'],list)
        radius=None;R=None;basis=None
        if sku in ('HELU23302','HELU23301','HELU23308'):
            radius,R,basis=1.05,12.6,'Selected0.5mm2 HELU family; retained head/local nominal OD2.1/fixedR12.6'
        elif sku in ('HELU23502','HELU23501'):
            radius,R,basis=1.25,15.,'Selected1mm2 HELU family; retained AUX nominal OD2.5/R15'
        elif sku=='HELU23802':radius,R,basis=2.1,25.2,'Selected4mm2 HELU family; retained project OD4.2/R25.2'
        elif sku.startswith('MTA0100335'):radius,R,basis=2.1,25.2,'Selected MTA factory family: original four-holder project R25.2, not generic current12.4'
        elif sku.startswith('FHAC0001ZXJ'):radius,R,basis=2.,6.,'Retained selected FHAC family OD4/R6 nominal delivery assumptions; no supplier certification'
        elif wire in e2roles:radius,R,basis=.925,11.1,'Selected E2 four exact225mm prefitted leads; retained model OD1.85/R11.1'
        elif wire in common:
            source=common[wire]['source'];radius=source['OD_project_upper_mm']/2;R=source['project_radius_mm'];basis='Selected fixed whole conductor recipe, not default power envelope'
        elif 'K-1474' in sku:radius,R,basis=1.05,row.get('minimum_project_R_mm',12.4),'Retained MAIN explicit nominal OD2.1, source fit gate'
        if radius is None:continue
        old_radius=row.get('project_radius_mm');old_R=row.get('minimum_project_R_mm');new_R=max(old_R or 0,R)
        row.update(planning_capacity_radius_mm=max(old_radius or 0,radius),project_radius_mm=radius,minimum_project_R_mm=new_R,
            nominal_physical_recipe_basis=basis,geometry_capacity_must_not_be_renamed_supplier_OD=True,
            CAD_cap_larger_than_nominal_is_capacity_NOT_a_different_SKU=True,source_profile_fit_after_delivery=True)
        if old_radius is None or old_R is None or abs(old_radius-radius)>1e-7 or abs(old_R-new_R)>1e-7:changed.append(dict(portion=name,sku=sku,old_radius_mm=old_radius,new_nominal_radius_mm=radius,old_R_mm=old_R,new_R_mm=new_R))
    assert len(result['portions'])==123
    sources=(SELECTION,headfile,auxfile,commonfile,e2file,endpointfile,pf,df,ROOT/'tools/cad/plan_current_mta_interfaces.py',ROOT/'tools/cad/feline_physical_wire_profiles.py',Path(__file__))
    return dict(status='CURRENT_SELECTED_PHYSICAL_ROLES_GEOMETRY_AND_COMMON_LAYOUT_STILL_OPEN',portions=result['portions'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},selected_material_baseline_tag=tag,
        selected_material_git_blob=expected,bound_portions=mapped,unbound_factory_or_composite_roles=unknown,grouped_source_donor_factory_roles=grouped_factory,changed_physical_contracts=changed,
        selected_SKUs_changed=False,old_stock_cut_lengths_imported=False,old_max_cap_impossibility_claims_need_typed_reconciliation=True,
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))


def load():
    f=OUT/'n01-selected-piece-profile-contract.json';r=json.loads(f.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return r,f


if __name__=='__main__':
    r=compose();save_json(OUT/'n01-selected-piece-profile-contract.json',r)
    print(r['status'],'bound',len(r['bound_portions']),'factory/composite',len(r['unbound_factory_or_composite_roles']),'changed',len(r['changed_physical_contracts']),r['worker_seconds'])
    print(json.dumps(r['changed_physical_contracts'],indent=2))
