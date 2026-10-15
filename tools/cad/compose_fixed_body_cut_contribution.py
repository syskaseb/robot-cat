"""Nominal fit blanks for all44 non-servo body nets, not a cutting order.

Read current recipes, retain factory/custom portions separately, and never
count the historical920mm as an extra wire. No CAD or supplier search.
"""
import json,math,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def blank(guide,allowance,trim=20,limit=None):
    assert min(guide,allowance,trim)>=0
    minimum=guide+allowance
    nominal=5*math.ceil((minimum+trim)/5)
    if limit is not None:assert nominal<=limit,('Factory limit',nominal,limit)
    return dict(guide_mm=guide,termination_project_allowance_mm=allowance,
                fit_trim_project_mm=trim,minimum_project_blank_mm=minimum,
                nominal_fit_blank_mm=nominal,retained_limit_mm=limit,actual_cut_mm=None)


def material_draw(portions):
    """One shared factory cable draws MAX(core blanks), never their sum."""
    groups={};sums={}
    for r in portions:
        key=r['sku'].split()[0]
        unit=r['physical_unit']
        if unit in groups:assert groups[unit]['sku']==key,'Mixed products in physical unit'
        q=groups.setdefault(unit,dict(sku=key,nominal_mm=0,conductors=[]))
        q['nominal_mm']=max(q['nominal_mm'],r['nominal_fit_blank_mm'])
        q['conductors'].append(r['wire'])
    for q in groups.values():sums[q['sku']]=sums.get(q['sku'],0)+q['nominal_mm']
    return groups,sums


def run():
    tick=time.monotonic();pins=set();cache={};portions=[]
    def read(name):
        p=OUT/(name+'.json');pins.add(p)
        if name not in cache:cache[name]=json.loads(p.read_text())
        return cache[name]
    register=read('harness-interfaces-plan');inventory=read('retained-body-guides-inventory')
    def add(wire,part,r,sku,allowance,trim=20,limit=None,physical_unit=None):
        guide=sum(p['length_mm'] for p in r['parts'])
        q=blank(guide,allowance,trim,limit)
        if wire in ('W079','W080'):physical_unit='K1474_USB_FACTORY_PAIR'
        portions.append(dict(wire=wire,portion=part,sku=sku,physical_unit=physical_unit or wire+'_'+part,**q))
    for row in register['body_conductors']:
        wid=row['id']
        if row.get('loom'):continue
        if wid in inventory['guides']:
            g=inventory['guides'][wid];read(g['recipe_file'].removesuffix('.json'))
            for i,r in enumerate(g['segments']):
                if wid in ('W002','W003'):
                    q=dict(wire=wid,portion='factory_BUS_core',sku='SR-Cable-5264-3PIN-900mm-6PCS',
                           physical_unit='BUS_DG_ONE_FACTORY_CABLE',**blank(sum(p['length_mm'] for p in r['parts']),35.05,0,900))
                    # Preserve the routing receipt's explicit connector/end allowance.
                    assert abs(q['minimum_project_blank_mm']-r['minimum_factory_blank_project_mm'])<1e-6
                    portions.append(q);continue
                if wid=='W076':
                    add(wid,'factory' if i==0 else 'custom',r,
                        'F0 supplied12AWG' if i==0 else 'HELU23802',r['termination_allowance_mm'],
                        0 if i==0 else 20,84.5 if i==0 else None);continue
                sku=r.get('SKU') or r.get('material')
                if wid in ('W079','W080'):
                    sku='Joy-IT K-1474 retained18AWG';allowance=3;trim=0;limit=250
                elif wid in ('W077','W078'):
                    allowance=8 if wid=='W077' else 3
                    trim=0;limit=100 if wid=='W077' else 150
                elif wid in ('W075','W066'):
                    allowance=r['termination_allowance_mm'];trim=0 if wid=='W075' else 20
                    limit=50 if wid=='W075' else None
                    sku='F0 supplied12AWG' if wid=='W075' else 'HELU23802'
                else:
                    allowance=sum(r['strip_mm']);trim=0 if wid=='W060' else 20
                    limit=300 if wid=='W060' else None
                assert sku,(wid,'Missing explicit recipe material')
                add(wid,'continuous',r,sku,allowance,trim,limit)
            continue
        g=row['guide'];p=read(g['plan'].removesuffix('.json'))
        r=p['factory_routes' if g['route']=='W043' else 'routes'][g['route']]
        if wid in ('W064','W065','W067','W068'):
            allowance=r['rail_strip_mm']+r['ring_barrel_allowance_mm']
            add(wid,'continuous',r,r['sku'],allowance)
        elif g['route'].endswith('_CUSTOM'):
            add(wid,'custom',r,r.get('SKU') or r['sku'],sum(r.get('strip_mm') or r['nominal_end_strip_mm']))
            f=row['factory_segment'];fp=read(f['plan'].removesuffix('.json'))
            fr=fp['factory_override'] if f['route']=='factory_override' else fp['factory_routes'][f['route']]
            add(wid,'factory',fr,'MTA0100335 supplied4mm2',11,0,84.5)
        elif wid=='W043':add(wid,'factory',r,'FHAC0001ZXJ supplied16AWG',r['rail_strip_mm'],0,50)
        else:add(wid,'continuous',r,r['SKU'],sum(r['strip_mm']))
    ids={r['wire'] for r in portions};expected={r['id'] for r in register['body_conductors'] if not r.get('loom')}
    assert ids==expected and len(ids)==44 and len(portions)==53
    source=read('source-four-feed-material-contribution')
    for r in source['wires']:
        actual=next(p for p in portions if p['wire']==r['wire'])
        assert actual['nominal_fit_blank_mm']==r['nominal_fit_blank_mm']
    sums={}
    for r in portions:sums[r['sku']]=sums.get(r['sku'],0)+r['nominal_fit_blank_mm']
    units,draw=material_draw(portions)
    assert units['BUS_DG_ONE_FACTORY_CABLE']['nominal_mm']==395
    assert len(units['BUS_DG_ONE_FACTORY_CABLE']['conductors'])==2
    result=dict(status='ALL44_FIXED_BODY_NETS_NOMINAL_MATERIAL_CONTRIBUTION_NOT_STOCK_SELECTION',
        conductor_count=44,conductor_portion_count=53,portions=portions,
        nominal_conductor_sums_mm=sums,physical_cut_units=units,nominal_material_draw_mm=draw,
        installed_BUS_factory_cables=1,extra_historical_920mm_cables=0,
        excluded_servo_factory_looms=12,excluded_servo_conductors=36,
        joint_rule='Eight MTA factory/custom pairs and W076 are separate cuts with connectors; never bridge their case gaps by extra wire.',
        gates=['All current native retention and assembled service',
               'Factory blank/cup/strip/terminal fit after delivery; nominal allowances are not cutting instructions',
               'Combine servo looms, local electronics, sleeves/lacing and hardware before choosing whole stock',
               'E3 electrical data not qualified by length arithmetic'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in pins|{Path(__file__)}},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'fixed-body-cut-contribution.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('conductor_count','conductor_portion_count','nominal_material_draw_mm','worker_seconds')}))


if __name__=='__main__':run()
