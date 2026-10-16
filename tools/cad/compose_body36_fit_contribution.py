"""Current36 full fanouts and real12source/4donor factory cut units.

Nominal fit allowances, not cut instructions or supplier wire/ampacity data.
Three cores of a factory cable draw MAX(blank), never three separate cables.
The already planned source-owned staggered extensions are not invented anew.
"""
import json,math,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def fit_blank(minimum,trim=20):
    assert minimum>=0
    result=5*math.ceil((minimum+trim)/5);assert result<=900
    return result


def compose(rows,routes,extensions):
    assert len(rows)==len(routes)==36
    joins={r['loom']:r for r in extensions['four_source_owned_extension_candidates']}
    assert len(joins)==4
    portions=[];units={}
    for r in rows:
        wid=r['wire'];q=routes[wid];guide=sum(p['length_mm'] for p in q['parts'])
        assert abs(guide-q['guide_mm'])<1e-5
        capacity=r['capacity_before_terminal_mm'];termination=r['terminal_allowance_project_mm']
        spare=capacity-guide-termination;assert spare>=-1e-6,(wid,spare)
        if r['source_extension_candidate']:
            join=joins[r['loom']];s=next(c for c in join['staggered_core_schedule'] if c['wire']==wid)
            assert abs(s['donor_core_capacity_before_terminal_mm']-capacity)<1e-6
            original_minimum=s['original_core_cut_from_plug_face_project_mm']
            # Four mm lap allowance is the inherited source join recipe,
            # not another connector hidden in the static body fanout.
            donor_to_root=850-capacity-4
            cuts=[('SOURCE/'+r['loom'],'original_source',original_minimum),
                  ('DONOR/'+r['loom'],'source_owned_donor',donor_to_root+guide+termination+4)]
        else:
            source_to_root=850-capacity
            cuts=[('SOURCE/'+r['loom'],'continuous_factory',source_to_root+guide+termination)]
        for unit,kind,minimum in cuts:
            nominal=fit_blank(minimum)
            portions.append(dict(wire=wid,core=r['core'],loom=r['loom'],physical_unit=unit,portion=kind,
                current_body_guide_mm=guide,terminal_allowance_project_mm=termination,minimum_project_blank_mm=minimum,
                fit_trim_project_mm=20,nominal_fit_blank_mm=nominal,current_body_spare_project_mm=spare,actual_cut_mm=None))
            u=units.setdefault(unit,dict(sku='SR-Cable-5264-3PIN-900mm-6PCS',factory_nominal_mm=900,
                nominal_fit_draw_mm=0,conductors=[]))
            u['nominal_fit_draw_mm']=max(u['nominal_fit_draw_mm'],nominal);u['conductors'].append(wid)
    assert len(portions)==48 and len(units)==16 and all(len(u['conductors'])==3 for u in units.values())
    return portions,units


def run():
    tick=time.monotonic();files=[OUT/(n+'.json') for n in ('body36-shared-macro-layout','body36-recovery-layout',
        'body36-current-contract','leg-extension-budget-plan','harness-interfaces-plan','fixed-body-cut-contribution')]
    macro,base,contract,extensions,register,fixed=[json.loads(f.read_text()) for f in files]
    for receipt in (macro,base,contract,extensions,register,fixed):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert not macro['remaining_wire_ids'] and all(not a['contacts'] and not a['errors'] for a in macro['attempts'])
    routes={n:base['routes'][n] for n in macro['retained_route_ids']};routes.update(macro['qualified_changed_routes'])
    rows={r['wire']:r for r in contract['rows']};rows.update({r['wire']:r for r in macro['changed_rows']})
    portions,units=compose(list(rows.values()),routes,extensions)
    assert {p['wire'] for p in portions}=={r['id'] for r in register['body_conductors'] if r.get('loom')}
    all_units=dict(units,**fixed['physical_cut_units'])
    factory=[n for n,u in all_units.items() if u['sku']=='SR-Cable-5264-3PIN-900mm-6PCS']
    assert len(factory)==17  #12source+4real donors+ONE shared BUS D/G cable.
    result=dict(status='ALL36_CURRENT_FANOUTS_16_FACTORY_UNITS_FIT_CONTRIBUTION_NOT_STOCK_SELECTION',
        conductors=36,conductor_portions=48,portions=portions,physical_units=units,
        body_factory_units=16,shared_BUS_factory_units=1,total_factory_units_including_fixed44=17,
        candidate_factory_packs=3,cables_per_pack=6,whole_factory_spares_after_BUS=1,
        factory_usable850mm_is_project_requirement_NOT_supplier_data=True,
        old_source3_offcuts_NOT_counted_as_extra_cables=True,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files+[Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),
        open=['Whole native support/assembly selection','Other local module stock/sleeves/lacing/hardware reconciliation',
              'Delivered keyed cavity mapping,Copper/OD/useful length/termination and E3'],
        selected=False,stock_selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body36-fit-material-contribution.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('conductors','conductor_portions','body_factory_units','total_factory_units_including_fixed44','worker_seconds')}))


if __name__=='__main__':run()
