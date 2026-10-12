"""Reconcile one exact shared-route receipt with self/stock planning gates.

The curve-to-material/mutual check is exact BRep. Self proximity below is a
conservative sampled screen, explicitly not a physical/swept-volume PASS.
"""
import json,math,itertools,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from current_prototype_harness_scene import wire


def self_screen(points,diameter,step=.25):
    grid={};cell=max(diameter+step,1);travel=0;previous=None;close=[]
    for i,p in enumerate(points):
        if previous is not None:travel+=math.dist(p,previous)
        previous=p;key=tuple(math.floor(x/cell) for x in p)
        for delta in itertools.product((-1,0,1),repeat=3):
            for j,q,at in grid.get(tuple(x+y for x,y in zip(key,delta)),()):
                # Ordinary nearby sections of the same smooth tube are not
                # separate conductors. Check distant returns along the path.
                if travel-at<=3*diameter:continue
                distance=math.dist(p,q)
                if distance<diameter+step:close.append(dict(samples=[j,i],distance_mm=distance,
                    required_mm=diameter,sampling_allowance_mm=step,along_path_separation_mm=travel-at))
        grid.setdefault(key,[]).append((i,p,travel))
    return close


def run():
    tick=time.monotonic();pf=OUT/'u1-common-wiring-plan.json';gf=OUT/'u1-common-wiring-checks.json'
    p=json.loads(pf.read_text());g=json.loads(gf.read_text());assert SHA(pf)==g['plan_sha256']
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert not any(g[k] for k in ('material_resolutions','wire_contacts','USB_fit_reservations','errors'))
    routes={**p['complete_routes'],**p['changed_MAIN_pair']};issues={};lengths={}
    for n,r in routes.items():
        shape=wire(r['parts']);points=[]
        for e in shape.Edges:
            q=[list(v) for v in e.discretize(Distance=.25)]
            points.extend(q if not points else q[1:])
        found=self_screen(points,2*r['radius'])
        if found:issues[n]=found
        lengths[n]=dict(exact_curve_mm=shape.Length,planning_guide_mm=r['guide_mm'],
            guide_minus_exact_mm=r['guide_mm']-shape.Length,nominal_blank_mm=r['nominal_blank_mm'],
            project_static_min_bend_mm=r['min_fixed_radius_mm'],actual_cut_mm=None)
        # Search integrates sampled Bezier lengths; reconcile against OCCT,
        # with explicit0.1percent numerical budget, not a new cable allowance.
        assert abs(shape.Length-r['guide_mm'])<max(.1,.001*r['guide_mm']),(n,shape.Length,r['guide_mm'])
        allowance=36 if r.get('source',{}).get('AWG')==26 else 3 if n.startswith('W') else 6
        assert shape.Length+allowance<=r['nominal_blank_mm'],(n,'Blank too short')
    main=max(lengths[n]['exact_curve_mm']+3 for n in ('W079','W080'));assert main<=250
    gpio=[n for n,r in p['complete_routes'].items() if r['source'].get('AWG')==26]
    assert len(gpio)==5 and all(lengths[n]['nominal_blank_mm']<=600 for n in gpio)
    result=dict(status='SHARED_13_ROUTES_EXACT_CLEAR_SELF_STOCK_SCREEN_CLEAR_NATIVE_OPEN' if not issues else 'SELF_PROXIMITY_REQUIRES_RESOLUTION',
        routes=lengths,exact_receipt_pairs=g['pairs'],self_proximity=issues,
        self_screen_scope='Samples<=0.25mm; distant path sections only,3OD local exclusion and0.25mm allowance. Not continuous self-contact/curvature or physicalPASS.',
        PI_CABLE_P0=dict(historical_cap_mm=250,retained_cap_mm=250,new450mm_candidate_rejected_as_unnecessary=True,
            longest_required_mm=main,candidate_passive_adapter='Delock60047',quantity=1,added_contact_losses_open=True),
        GPIO_stock=dict(factory_600mm_jumpers=5,one_cut_U1_end_each=True,nominal_blanks_mm={n:lengths[n]['nominal_blank_mm'] for n in gpio}),
        selected=False,E1_complete=False,W5_complete=False,physical_pass=False,
        open=['Carrier native copies','Independent insulation restraints and USB metal isolation/support','Installed service and BUS release','Whole W5 stock/selection'],
        source_sha256={pf.relative_to(ROOT).as_posix():SHA(pf),gf.relative_to(ROOT).as_posix():SHA(gf),
            Path(__file__).relative_to(ROOT).as_posix():SHA(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'u1-common-route-qualification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
