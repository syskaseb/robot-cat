"""Current four S1 feed blanks replace, never supplement, legacy920mm.

Only material contribution. No route/native/stock/E3 acceptance or cutting.
"""
import json,math,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def contribution(rows, fit_trim_mm=20):
    assert len(rows)==4 and {r['wire'] for r in rows}=={'W064','W065','W067','W068'}
    assert fit_trim_mm>=0
    result=[]
    for r in rows:
        assert r['sku']=='HELU23802'
        minimum=r['guide_mm']+r['rail_strip_mm']+r['ring_barrel_allowance_mm']
        nominal=5*math.ceil((minimum+fit_trim_mm)/5)
        result.append(dict(r,minimum_project_blank_mm=minimum,
            fit_trim_project_allowance_mm=fit_trim_mm,nominal_fit_blank_mm=nominal,
            actual_crimp_strip_mm=None,actual_cut_mm=None))
    return dict(status='FOUR_CURRENT_SOURCE_FEEDS_MATERIAL_CONTRIBUTION_ONLY',
        wires=result,physical_installed_wires=4,extra_920mm_cable_quantity=0,
        historical_sum_mm=920,current_guide_sum_mm=sum(r['guide_mm'] for r in result),
        nominal_fit_blank_sum_mm=sum(r['nominal_fit_blank_mm'] for r in result),
        selected=False,whole_stock_complete=False,W5_complete=False,physical_pass=False,
        interpretation='Replace historical920mm source allocation with these four current feed blanks; never add920mm again.',
        gates=['Actual ring crimp strip and delivered wire fit',
               'Native grips and installed assembly/service',
               'Aggregate all HELU23802 contributors before choosing stock',
               'E3 electrical protection data remains separate'])


def run():
    tick=time.monotonic();register=OUT/'harness-interfaces-plan.json'
    p=json.loads(register.read_text());pins={register}
    assert p['source_scope']['wires']==['W064','W065','W067','W068']
    rows=[]
    for row in p['body_conductors']:
        if row['id'] not in p['source_scope']['wires']:continue
        source=OUT/row['guide']['plan'];pins.add(source)
        receipt=json.loads(source.read_text())
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
        r=receipt['routes'][row['guide']['route']]
        guide=sum(part['length_mm'] for part in r['parts'])
        assert abs(guide-row['guide']['guide_mm'])<1e-6
        rows.append(dict(wire=row['id'],roles=row['roles'],sku=r['sku'],guide_mm=guide,
            rail_strip_mm=r['rail_strip_mm'],ring_barrel_allowance_mm=r['ring_barrel_allowance_mm'],
            recipe=source.relative_to(ROOT).as_posix()))
    result=contribution(rows)
    result.update(source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in pins|{Path(__file__)}},
                  worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'source-four-feed-material-contribution.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('physical_installed_wires','current_guide_sum_mm','nominal_fit_blank_sum_mm','worker_seconds')}))


if __name__=='__main__':run()
