"""One coupled end-contract correction; preserve selected parts and circuits.

Reconcile six stale CAD cavity labels with the ALREADY current KiCad design.
Plan G1 face-normal exits, whole POST_F0 rotation and a nominal K-1474 common
tail plane before rechecking geometry. No external U1 pinout or fit invented.
"""
import copy
import json
import math
import time
from pathlib import Path
from compose_feline_n01_allocation import ROOT,OUT,sha


def compose():
    tick=time.monotonic();source=OUT/'n01-current-endpoint-packet-r2.json'
    ecad=ROOT/'hardware/electronics/kicad-current/design.json'
    scene=OUT/'n01-full-material-scene.json';gate=OUT/'n01-all-current-first-lands.json'
    p=copy.deepcopy(json.loads(source.read_text()));k=json.loads(ecad.read_text())
    assert not k['physical_pass'] and not k['power_authorized']
    wires={w['id']:w for w in k['wires']};ends={e['id']:e for e in p['endpoints']};changed=[]
    def revise(key,point=None,axis=None,role=None,basis=''):
        e=ends[key];before={f:copy.deepcopy(e[f]) for f in ('role','point_mm','departure_axis')}
        if point is not None:e['point_mm']=point
        if axis is not None:e['departure_axis']=axis
        if role is not None:e['role']=role
        e.update(current_update=basis,complete_route_verified=False,stock_selected=False)
        changed.append(dict(id=key,before=before,after={f:e[f] for f in before},basis=basis))
    for code,sign in (('RL',1),('RR',-1)):
        ids=('W069','W070','W071') if code=='RL' else ('W072','W073','W074')
        # Current ECAD already uses .1/.2/.3 for the legs and .4 for supply.
        # Old CAD alone retained .2/.3/.4, causing a duplicate physical cavity.
        for w in ids:
            key=w+'/body/end';e=ends[key];role=wires[w]['b'];assert role.startswith(code+'_G.')
            port=int(role.rsplit('.',1)[1]);assert port in (1,2,3)
            x=9.5+(port-1)*4.75 if sign>0 else 28.5-(port-1)*4.75
            revise(key,point=[x,e['point_mm'][1],e['point_mm'][2]],role=role,
                basis='Current KiCad selected cavity contract, NOT an electrical reassignment or new part')
    for e in p['endpoints']:
        if e['group']=='WAGO:G1_CP2':
            assert abs(e['point_mm'][1]-51.5)<1e-5
            revise(e['id'],axis=[0,1,0],basis='G1 current casing mouth lies on outerY51.5 face; old axis had been rotated twice')
    centre=[143,-35,42];R=[[0,-1,0],[1,0,0],[0,0,1]]
    for e in p['endpoints']:
        if e['group']!='POST_F0':continue
        a=[e['point_mm'][i]-centre[i] for i in range(3)]
        b=[centre[i]+sum(R[i][j]*a[j] for j in range(3)) for i in range(3)]
        d=[sum(R[i][j]*e['departure_axis'][j] for j in range(3)) for i in range(3)]
        revise(e['id'],point=b,axis=d,basis='Whole selected POST_F0 rotated90deg about its own centre; both exits now outwardY, P0 unchanged')
    for w,x in (('W079',30.95),('W080',34.45)):
        revise(w+'/retained0/end',point=[x,-45,101.3],axis=[0,-1,0],
            basis='Nominal common Joy-IT K-1474 tail plane after project10x17x5 mould reservation; two insulated leads3.5mm apart, not collinear old GUIDE points. Delivered plug/lead fit remains a gate.')
        ends[w+'/retained0/end']['nominal_project_wire_radius_mm']=1.05
    occupied={}
    for e in p['endpoints']:
        if not e['group'].startswith('WAGO:'):continue
        key=e['role'];assert key not in occupied,(key,occupied.get(key),e['id'])
        occupied[key]=e['id']
    assert len(changed)==15 and len(ends)==178
    segment_ends={}
    for e in p['endpoints']:segment_ends.setdefault(e['id'].rsplit('/',1)[0],[]).append(e)
    p['physical_segment_lower_bounds']=[dict(id=n,endpoint_ids=[e['id'] for e in es],
        straight_lower_bound_mm=math.dist(es[0]['point_mm'],es[1]['point_mm']),is_not_cut_length=True,
        full_middle_route_verified=False) for n,es in sorted(segment_ends.items())]
    p.update(status='COUPLED_CURRENT_PORT_CONTRACTS_PENDING_GEOMETRY',selected=False,N01_complete=False,
        contract_changes=changed,geometry_gate_complete=False,ecad_file_changed=False,selected_parts_changed=False,
        changed_scene_groups={'POST_F0':dict(centre_mm=centre,relative_rotation_rows=R)},
        nominal_Pi_USB_C_mould=dict(bounds_mm=[[27.7,-45,98.8],[37.7,-28,103.8]],
            basis='PROJECT RESERVATION ONLY, no supplier dimensional guarantee. Retained K-1474, no new connector.',
            mating_owner='Pi4',full225mm_pair_routes_stock_and_delivered_fit_open=True),
        owned_restraint_channels_open=['Four9wire cuff/arm passages','P_SYS/MAIN common comb cavities',
            'All independent strap/land clearance budgets','S0 real crimp-barrel exit before9mm jacket lands'],
        current_WAGO_ports_unique=True,old_full_paths_not_inherited=True,
        source_sha256={**p['source_sha256'],**{f.relative_to(ROOT).as_posix():sha(f) for f in (source,ecad,scene,gate,Path(__file__))}},
        worker_seconds=round(time.monotonic()-tick,4),
        next='One coupled geometry gate:15changedends/POST_F0/mould, source crimp throats and declared owned support channels. Preserve received lower bay/Pi routes; no new detailed native before complete N01.')
    return p


def main():
    dest=OUT/'n01-current-endpoint-packet-r3.json';assert not dest.exists()
    p=compose();dest.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(p['status'],len(p['contract_changes']),p['current_WAGO_ports_unique'],p['worker_seconds'])


if __name__=='__main__':main()
