"""Current W5 ownership contract, before any whole-harness CAD edits.

Historical endpoints are not accepted geometry. Keep eighty continuous body
conductors, collapse graph aliases, and reserve the already selected interfaces.
No unknown supplier pin or unqualified moving leg route is manufactured here.
"""
import copy
import hashlib
import json
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'body-harness-checkpoint'
READ=lambda p:json.loads(p.read_text(encoding='utf-8'))
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def plan():
    ep=READ(BASE/'wiring-checkpoint/endpoint-plan.json')
    rows=copy.deepcopy(ep['body_conductors'])
    assert {r['id'] for r in rows}=={f'W{i:03}' for i in range(1,81)}
    assert len(rows)==80
    # P_REAR.1 now feeds the qualified short AUX branch. Same positive rail;
    # put the unselected S1 supply at5, never double-occupy1 or move E2 port4.
    source=next(r for r in rows if r['id']=='W065')
    assert source['a']=='P_REAR.1'
    source['a']='P_REAR.5'
    rebound={'role':'P_REAR.5','point_mm':[29,-13,138],
        'departure':[1,0,0],'current_owner':'E2/W1 E2Fixture',
        'basis':'Same selected P_REAR rail, unused fifth project cavity',
        'manufacturer_pin_claim':False,'delivered_fit_gate':True}
    for r in rows:
        r['historical_ends']=r.pop('ends')
        r['ends']=[dict(role=r['a'],status='CURRENT_ROUTE_AND_RELIEF_OPEN'),
                   dict(role=r['b'],status='CURRENT_ROUTE_AND_RELIEF_OPEN')]
        r['route_status']='UNSELECTED_CURRENT_W5'
        r.pop('straight_distance_only_mm',None)
        r['actual_cut_mm']=None
    source['ends'][0].update(rebound)
    fixed={}
    files=[BASE/'wiring-checkpoint/endpoint-plan.json',Path(__file__)]
    for folder in ('aux-wiring-checkpoint','head-supply-checkpoint',
                   'tail-wiring-checkpoint','pwm-branch-checkpoint'):
        path=BASE/folder/'selection.json'
        if path.exists():
            selected=READ(path)
            fixed[folder]={'selection':path.relative_to(ROOT).as_posix(),
                          'sha256':SHA(path),'geometry_and_material_retained':True,
                          'W5_complete':False}
            files.append(path)
    # Explicit current datums; nominal WAGO entries remain delivery-gated.
    fixed_ports={
        'P_REAR.1':{'wire':'XA01','point_mm':[29,13,138]},
        'P_REAR.4':{'wire':'XP01','point_mm':[29,-6.5,138]},
        'P_REAR.5':{'wire':'W065','point_mm':[29,-13,138]},
        'P_AUX.1':{'wire':'XB11','point_mm':[28,-25.5,155]},
        'P_AUX.2':{'wire':'XA03','point_mm':[28,-30.25,155]},
        'G2.5':{'wire':'XA05','point_mm':[101.5,53.5,155]},
        'G_AUX.1':{'wire':'XA05','point_mm':[-117,-16.3,123.39378221735]},
        'G_AUX.2':{'wire':'XA04','point_mm':[-117,-21.05,123.39378221735]},
        'G_AUX.3':{'wire':'XB23','point_mm':[-117,-25.8,123.39378221735]},
        'G_AUX.4':{'wire':'XB13','point_mm':[-117,-30.55,123.39378221735]},
        'G_AUX.5':{'wire':'XA06','point_mm':[-117,-35.3,123.39378221735]},
        'G_TAIL.1':{'wire':'XA06','point_mm':[37.5,-25.5,141]},
        'G_TAIL.2':{'wire':'XB33','point_mm':[37.5,-30.25,141]},
        'G_TAIL.3':{'wire':'XP03.source','point_mm':[37.5,-35,141]},
    }
    assert len({(k,v['wire']) for k,v in fixed_ports.items()})==len(fixed_ports)
    internal={}
    for row in ep['distribution_boundary']:
        if row.get('body_id'):continue
        for alias in row['graph_aliases']:
            if alias in ('W_FL_G.1','W_G1.3'):canonical='W025'
            elif alias in ('W_FR_G.1','W_G1.4'):canonical='W036'
            elif alias in ('W_G2.2','W_RL_G.1'):canonical='W062'
            elif alias in ('W_G2.3','W_RR_G.1'):canonical='W063'
            else:canonical=alias
            entry=internal.setdefault(canonical,{'graph_aliases':[],
                'counts_as_extra_body_conductor':False,
                'status':'RETAIN_SELECTED_INTERFACE_OR_COMPLETE_W5_APPROACH'})
            entry['graph_aliases'].append(alias)
    legs=copy.deepcopy(ep['leg_looms'])
    assert len(legs)==12
    return dict(status='CURRENT_W5_OWNER_PLAN_ONLY',selected=False,W5_complete=False,
        physical_pass=False,body_conductors=rows,body_conductor_count=80,
        body_end_count=160,leg_looms=legs,leg_conductor_count=36,
        fixed_interfaces=fixed,fixed_ports=fixed_ports,internal_boundary_owners=internal,
        legacy_source_scope={'wires':['W064','W065','W067','W068'],
            'historical_total_mm':920,'current_length_stock_complete':False,
            'rule':'Four existing continuous S1 feeds, not a fifth920mm cable or BAT/F0 lead.'},
        allocation_order=[
            'Retain current W1/W2/W3/W4/E2 native material, wire paths and known pads.',
            'Allocate four MAIN holders with BOTH tails, eight independent straight insulation lands, current receiving blocks and joint service access together.',
            'Allocate all twelve ATO inputs, twelve complete leg looms and ground/data fans together with registered CURRENT bank retention. R47 holders/ends/recipes remain; old BankLeft/Right plastics are superseded by CP2, not retained at raw historical poses.',
            'Bind four S1 feeds, battery/F0/S0/P_SYS/G1, F_PI/MAIN/Pi and actual BUS connector; then GPIO/monitor/balance and remaining local supply approaches.',
            'Only after shared physical acceptance implement one matched native relief set; reconcile continuous lengths and whole stock before W5 credit.'
        ],
        open_not_assumed=[
            'BUS D/G actual mating datum; historical OPEN_DATUM must not become bbox-centre pin.',
            'Twelve delivered servo cable cavity orders, exact exit geometry, motion slack and factory length.',
            'S0 nominal casing overlaps drawn terminal hardware; cannot infer metal protection from this casing.',
            'External U1 pads/pinout require actual board data, never a guessed solder connection.',
            'Twenty legacy WAGO locations, old bank plastics and CommonMtaMounts are superseded candidates, not retained whole-harness release.',
            'All global material/stock and physical delivered-fit gates remain open.'
        ],source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files})

def run():
    start=time.monotonic();p=plan();OUT.mkdir(exist_ok=True)
    p['planning_seconds']=round(time.monotonic()-start,4)
    (OUT/'owner-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:p[k] for k in ('status','body_conductor_count','body_end_count','leg_conductor_count','planning_seconds')}))

if __name__=='__main__':run()
