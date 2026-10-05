"""Receive already completed bank cuts and factory-lead recipes once.

Preserve R1 diagnosis. Missing scalar blanks on composite factory leads do
not mean missing purchased cable; bind their actual extension/retained parts
explicitly rather than inventing a whole-conductor cut.
"""
from pathlib import Path
P=Path(__file__).with_name('w5_prototype_preparation.py')
code=P.read_text(encoding='utf-8').replace("OUT=BASE/'w5-prototype-preparation-r1'","OUT=BASE/'w5-prototype-preparation-r2'")


def replace(a,b):
    global code
    assert code.count(a)==1,a
    code=code.replace(a,b)


replace("    missing=[r['wire'] for r in rows if r['nominal_preparation_blank_mm'] is None and not r.get('factory_loom')]", """    inputs=read(BASE/'servo-fuse-lower-loop-materials-r1/materials.json')
    bank=read(BASE/'servo-fuse-construction-checkpoint-r47/manifest.json')
    localstock=read(BASE/'servo-fuse-bank-stock-budget-r13/stock.json')
    body=read(BASE/'source-switch-selected-r1/body-harness.json')
    inputcuts={r['wire']:r['nominal_blank_mm'] for r in inputs['rows']}
    assert len(inputcuts)==12 and sum(inputcuts.values())==localstock['LAPP0107001']['input_blanks_mm']==2880
    source_roles=source['HELU23802']['unique_roles']
    for r in rows:
        wire=r['wire']
        if wire in inputcuts:
            r.update(nominal_preparation_blank_mm=inputcuts[wire],route_or_recipe_changed=True,
                basis='hardware/electronics/full-cat/servo-fuse-lower-loop-materials-r1/materials.json',
                stock_basis='Current bank service-loop cut, not earlier150/170/190mm. One LAPP conductor, selected bankR47 terminal recipe.')
        elif wire+'_extension' in source_roles:
            r.update(composite_factory_lead=True,nominal_extension_blank_mm=source_roles[wire+'_extension'],
                nominal_preparation_blank_mm=None,
                basis='hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r47/manifest.json',
                stock_basis='Retain original MTA lead and its R47 WAGO or insulated solder extension. HELU extension counted once in source subtotal.',
                physical_factory_cut_mm=None,preparation='Keep factory lead uncut until unpowered fit; prepare extension to received blank and exact R47 end recipe.')
        elif wire=='W041':
            r.update(retain_factory_lead=True,nominal_preparation_blank_mm=None,
                basis='hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r47/manifest.json',
                stock_basis='Retained original F_FL factory input lead, no new purchased blank and no duplicate extension.',
                preparation='Preserve original lead and R47 terminal restraint; trim only after fitting. Do not invent its usable free length.')
        elif wire=='W076':
            received=next(w for w in body['conductors'] if w['id']==wire)
            assert received['current_selected_route_checked'] and received['nominal_selected_blank_mm']==80
            r.update(nominal_preparation_blank_mm=80,retained_factory_F0_lead=True,material=received['material'],
                basis=received['selected_recipe'],stock_basis='80mm preparation from original F0 lead, not80mm additional LAPP.')
    missing=[r['wire'] for r in rows if r['nominal_preparation_blank_mm'] is None and not any(r.get(k) for k in ('factory_loom','composite_factory_lead','retain_factory_lead'))]
    assert not missing,missing
    # Only affected stock contributions, NOT a fabricated complete global K3.
    lapp=sum(r['nominal_preparation_blank_mm'] or 0 for r in rows if r['wire'] in inputcuts or r['wire']=='W001')
    tkd=[r for r in rows if r['wire'] in ('W025','W036','W061','W062','W063')]
    stock_delta=dict(LAPP0107001=dict(roles=[*inputcuts,'W001'],nominal_mm=lapp,candidate_stock_m=4),
        TKD2500125=dict(roles=[r['wire'] for r in tkd],nominal_mm=sum(r['nominal_preparation_blank_mm'] for r in tkd),
            fitting_allowance_mm=200,candidate_stock_m=3),
        HELU23802=source['HELU23802'],legacy_source920mm_not_added=True,
        all_other_shared_stock_requires_one_final_global_census=True)""")
replace("        individual_blank_unresolved_wire_ids=missing,", "        individual_blank_unresolved_wire_ids=missing,affected_material_stock=stock_delta,\n        bank_recipe_retained=bank['local_assembly'],all80_P0_preparation_roles_bound=True,")
replace("        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),*dict.fromkeys(pins)]},", "        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),P,*dict.fromkeys(pins)]},")
context=dict(__file__=str(Path(__file__).resolve()),__name__='received_preparation_definition',P=P)
exec(compile(code,str(Path(__file__).resolve()),'exec'),context)
if __name__=='__main__':context['main']()
